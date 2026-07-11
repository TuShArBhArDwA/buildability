#!/usr/bin/env python3
"""Fold agent research records (data/pass1/*.json) into the compact dataset.

Any app with a live agent record is tagged source="agent" and its values win.
Apps still missing keep their prior row (source stays "model"). Human/web
verified corrections are re-applied last so the loop-3 fixes are never lost.

    python agent/merge_dataset.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPS = {a["id"]: a for a in json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))}
base = {r["id"]: r for r in json.loads((ROOT / "data" / "dataset.json").read_text(encoding="utf-8"))}
PASS1 = ROOT / "data" / "pass1"

# live human/web-verified corrections from Loop 3 — always win, source stays "verified"
OVERRIDES = {
    82: {"access_model": "SELF_SERVE_FREE",
         "main_blocker": "Sandbox keys free+instant; only Production access needs approval"},
    96: {"primary_auth": "Service-account API key (cog_ prefix; PATs coming)"},
}


def short_auth(s: str) -> str:
    """First clause of a long primary_auth sentence, for the table."""
    s = re.split(r"[;(]", s)[0].strip()
    return s[:60]


merged = 0
for p in sorted(PASS1.glob("*.json"), key=lambda x: int(x.stem)):
    rec = json.loads(p.read_text(encoding="utf-8"))
    i = rec["id"]
    row = {
        "id": i, "name": rec["name"], "category": APPS[i]["category"],
        "one_liner": rec["one_liner"], "auth": rec["auth_methods"],
        "primary_auth": short_auth(rec["primary_auth"]),
        "access_model": rec["access_model"], "api_styles": rec["api_styles"],
        "api_breadth": rec["api_breadth"], "webhooks": rec["webhooks"],
        "official_mcp": rec["official_mcp"], "buildability": rec["buildability"],
        "main_blocker": rec["main_blocker"],
        "evidence": (rec["evidence"][0]["url"] if rec.get("evidence") else base[i]["evidence"]),
        "confidence": rec["confidence"], "source": "agent",
    }
    base[i] = row
    merged += 1

# re-apply verified corrections on top of whatever the agent produced
for i, patch in OVERRIDES.items():
    if i in base:
        base[i].update(patch)
        base[i]["source"] = "verified"

out = [base[i] for i in sorted(base)]
(ROOT / "data" / "dataset.json").write_text(json.dumps(out, indent=0).replace("\n", ""), encoding="utf-8")
# pretty one-line-per-record for git-friendliness
lines = "[\n" + ",\n".join(json.dumps(r, separators=(",", ":")) for r in out) + "\n]\n"
(ROOT / "data" / "dataset.json").write_text(lines, encoding="utf-8")

by_src = {}
for r in out:
    by_src[r["source"]] = by_src.get(r["source"], 0) + 1
print(f"merged {merged} agent records; dataset now {len(out)} rows; by source: {by_src}")
