#!/usr/bin/env python3
"""App-research agent — Composio (web search) + Claude (reasoning + structured output).

For each app it: pulls Composio's hosted COMPOSIO_SEARCH toolkit as Claude tools,
lets Claude search official docs, then forces a schema-valid JSON record back.
Writes one file per app to data/pass1/<id>.json.

    pip install composio composio_anthropic anthropic
    export COMPOSIO_API_KEY=...      # free key: https://dashboard.composio.dev/settings
    export ANTHROPIC_API_KEY=...
    python agent/run_research.py                 # all apps missing a record
    python agent/run_research.py --ids 1 2 3     # specific apps
    python agent/run_research.py --limit 5       # first N missing

This is the production shape of the same pipeline the case study was built with.
(In the case study the identical prompt/rubric/schema ran as a 100-way parallel
subagent fleet; that fleet hit an account session limit at app 11, which is why
this script is written to be idempotent and resumable — rerun and it fills gaps.)
"""
import os, sys, json, argparse, pathlib

from anthropic import Anthropic
from composio import Composio
from composio_anthropic import AnthropicProvider

from schema import APP_SCHEMA, research_prompt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPS = json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "pass1"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "claude-opus-4-8"
USER_ID = "app-research"


def build_clients():
    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"], provider=AnthropicProvider())
    claude = Anthropic()  # reads ANTHROPIC_API_KEY
    # COMPOSIO_SEARCH is Composio-managed and needs no per-user connection.
    tools = composio.tools.get(user_id=USER_ID, toolkits=["COMPOSIO_SEARCH"])
    return composio, claude, tools


def research_one(app, composio, claude, search_tools):
    """Run the search->reason loop, then force one schema-valid record out."""
    messages = [{"role": "user", "content": research_prompt(app)}]

    # 1) let Claude drive Composio web-search tools until it stops calling them
    for _ in range(8):
        resp = claude.messages.create(
            model=MODEL, max_tokens=4096, tools=search_tools, messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            break
        results = composio.provider.handle_tool_calls(user_id=USER_ID, response=resp)
        messages.append({"role": "user", "content": results})

    # 2) force the structured record (Claude's structured outputs)
    messages.append({"role": "user", "content":
        "Now output ONLY the final research record as JSON matching the required schema."})
    final = claude.messages.create(
        model=MODEL, max_tokens=4096, messages=messages,
        output_config={"format": {"type": "json_schema", "schema": APP_SCHEMA}},
    )
    text = next(b.text for b in final.content if b.type == "text")
    record = json.loads(text)
    record["id"], record["name"] = app["id"], app["name"]
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", type=int)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    todo = APPS
    if args.ids:
        todo = [a for a in APPS if a["id"] in set(args.ids)]
    else:
        todo = [a for a in APPS if not (OUT / f"{a['id']}.json").exists()]  # resume
    if args.limit:
        todo = todo[: args.limit]

    if not todo:
        print("Nothing to do — all records present in data/pass1/.")
        return

    composio, claude, tools = build_clients()
    print(f"Researching {len(todo)} apps with {len(tools)} Composio search tools...")
    for app in todo:
        try:
            rec = research_one(app, composio, claude, tools)
            (OUT / f"{app['id']}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
            print(f"  [{app['id']:>3}] {app['name']:<28} {rec['access_model']:<18} {rec['buildability']}")
        except Exception as e:  # keep going; rerun fills gaps
            print(f"  [{app['id']:>3}] {app['name']:<28} FAILED: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
