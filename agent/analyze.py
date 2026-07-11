"""Aggregate the 100-app dataset into the patterns that drive the case study.

    python agent/analyze.py            # prints a human summary
    python agent/analyze.py --json     # emits data/analysis.json for the HTML page
"""
import json, sys, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "dataset.json").read_text(encoding="utf-8"))


def counts(key):
    c = collections.Counter()
    for r in DATA:
        v = r[key]
        if isinstance(v, list):
            for x in v:
                c[x] += 1
        else:
            c[v] += 1
    return dict(c.most_common())


def by_category(field):
    out = collections.defaultdict(lambda: collections.Counter())
    for r in DATA:
        out[r["category"]][r[field]] += 1
    return {k: dict(v) for k, v in out.items()}


SELF_SERVE = {"SELF_SERVE_FREE", "SELF_SERVE_TRIAL"}
GATED = {"APPROVAL_REQUIRED", "PAID_PLAN_REQUIRED", "PARTNER_GATED", "NO_PUBLIC_API"}

analysis = {
    "total": len(DATA),
    "auth_methods": counts("auth"),
    "primary_auth_family": collections.Counter(
        "OAuth2" if "OAuth" in r["primary_auth"] else
        "API key" if ("API key" in r["primary_auth"] or "key" in r["primary_auth"].lower()
                      or "token" in r["primary_auth"].lower() or "Basic" in r["primary_auth"]) else
        "None/local" if "None" in r["primary_auth"] else "Other"
        for r in DATA),
    "access_model": counts("access_model"),
    "buildability": counts("buildability"),
    "api_breadth": counts("api_breadth"),
    "official_mcp": counts("official_mcp"),
    "webhooks_yes": sum(1 for r in DATA if r["webhooks"]),
    "self_serve": sum(1 for r in DATA if r["access_model"] in SELF_SERVE),
    "gated": sum(1 for r in DATA if r["access_model"] in GATED),
    "green": sum(1 for r in DATA if r["buildability"] == "GREEN"),
    "yellow": sum(1 for r in DATA if r["buildability"] == "YELLOW"),
    "red": sum(1 for r in DATA if r["buildability"] == "RED"),
    "official_mcp_yes": sum(1 for r in DATA if r["official_mcp"] == "YES_OFFICIAL"),
    "access_by_category": by_category("access_model"),
    "buildability_by_category": by_category("buildability"),
    "by_source": counts("source"),
}
analysis["primary_auth_family"] = dict(analysis["primary_auth_family"].most_common())

# self-serve rate per category (easy wins vs outreach)
cat_rate = {}
for r in DATA:
    cat_rate.setdefault(r["category"], [0, 0])
    cat_rate[r["category"]][1] += 1
    if r["access_model"] in SELF_SERVE:
        cat_rate[r["category"]][0] += 1
analysis["self_serve_rate_by_category"] = {
    k: {"self_serve": v[0], "total": v[1], "pct": round(100 * v[0] / v[1])}
    for k, v in sorted(cat_rate.items(), key=lambda kv: -kv[1][0] / kv[1][1])
}

# blocker buckets (only non-GREEN rows have a real blocker)
blk = collections.Counter()
for r in DATA:
    if r["buildability"] == "GREEN":
        continue
    a = r["access_model"]
    label = {
        "APPROVAL_REQUIRED": "App review / approval gate",
        "PARTNER_GATED": "Contact-sales / partnership gate",
        "PAID_PLAN_REQUIRED": "Paid plan required for API",
        "NO_PUBLIC_API": "No public/hosted API",
    }.get(a, a)
    blk[label] += 1
analysis["blockers"] = dict(blk.most_common())

if "--json" in sys.argv:
    (ROOT / "data" / "analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    print("wrote data/analysis.json")
else:
    import pprint
    pprint.pp(analysis)
