#!/usr/bin/env python3
"""Verification loop — an adversarial fact-checker over each pass-1 record.

A second Claude pass is told to REFUTE the record: re-search official docs via
Composio, mark each key field CONFIRMED/WRONG/PARTIALLY_WRONG/UNVERIFIABLE, and
emit a corrected record. Writes data/verified/<id>.json + data/checks/<id>.json.
This is the "accuracy moves from a lower first pass to a higher one" loop.

    python agent/verify.py --ids 1 2 3
"""
import os, sys, json, argparse, pathlib

from anthropic import Anthropic
from composio import Composio
from composio_anthropic import AnthropicProvider

from schema import VERDICT_SCHEMA, verify_prompt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPS = {a["id"]: a for a in json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))}
PASS1 = ROOT / "data" / "pass1"
VERIFIED = ROOT / "data" / "verified"; VERIFIED.mkdir(parents=True, exist_ok=True)
CHECKS = ROOT / "data" / "checks"; CHECKS.mkdir(parents=True, exist_ok=True)

MODEL = "claude-opus-4-8"
USER_ID = "app-verify"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", type=int)
    args = ap.parse_args()

    composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"], provider=AnthropicProvider())
    claude = Anthropic()
    tools = composio.tools.get(user_id=USER_ID, toolkits=["COMPOSIO_SEARCH"])

    ids = args.ids or sorted(int(p.stem) for p in PASS1.glob("*.json"))
    for i in ids:
        pass1 = json.loads((PASS1 / f"{i}.json").read_text(encoding="utf-8"))
        messages = [{"role": "user", "content": verify_prompt(APPS[i], pass1)}]
        for _ in range(8):
            resp = claude.messages.create(model=MODEL, max_tokens=4096, tools=tools, messages=messages)
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                break
            messages.append({"role": "user",
                             "content": composio.provider.handle_tool_calls(user_id=USER_ID, response=resp)})
        messages.append({"role": "user", "content":
            "Now output ONLY the verdict object (field_checks + overall_verdict + corrected) as JSON."})
        final = claude.messages.create(model=MODEL, max_tokens=4096, messages=messages,
            output_config={"format": {"type": "json_schema", "schema": VERDICT_SCHEMA}})
        obj = json.loads(next(b.text for b in final.content if b.type == "text"))
        (CHECKS / f"{i}.json").write_text(json.dumps(obj, indent=2), encoding="utf-8")
        (VERIFIED / f"{i}.json").write_text(json.dumps(obj["corrected"], indent=2), encoding="utf-8")
        print(f"  [{i:>3}] {APPS[i]['name']:<28} {obj['overall_verdict']}")


if __name__ == "__main__":
    main()
