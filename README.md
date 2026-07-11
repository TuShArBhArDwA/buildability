# App Buildability Research Agent — Composio take-home

Research 100 apps for **agent-toolkit buildability**: auth method, self-serve vs
gated access, API surface, official MCP, a GREEN/YELLOW/RED verdict, and evidence
URLs — then cluster the results into patterns and verify accuracy against live docs.

**Live case study:** _(deployed HTML link — see the Artifact published from this repo)_
**Deliverable page:** [`site/index.html`](site/index.html) — one self-explanatory page.

---

## What I built

A three-loop pipeline. The unit of work is one app; every app goes through the
**same schema and rubric** (`agent/schema.py`) so 100 independent runs are comparable.

```
apps.json ─▶ Loop 1  research agent   (Claude + Composio COMPOSIO_SEARCH web tools)
                     │  search official docs → forced JSON record  → data/pass1/
             Loop 2  adversarial verifier (2nd Claude pass, told to REFUTE)
                     │  re-check each field → corrected record      → data/verified/ + data/checks/
             Loop 3  human + live-web spot check (WebFetch vs official docs)
                     └  hits/misses recorded                        → data/verification.json
        analyze.py ─▶ cluster stats                                 → data/analysis.json
        (site/index.html renders dataset + analysis + verification)
```

- **Research** (`agent/run_research.py`): pulls Composio's hosted `COMPOSIO_SEARCH`
  toolkit as Claude tools (no per-app auth needed), lets Claude search official
  developer docs, then uses **structured outputs** to force a schema-valid record.
- **Verify** (`agent/verify.py`): a second Claude pass is prompted adversarially to
  *refute* pass 1, re-searching docs and correcting fields — this is the loop that
  moves accuracy up.
- **Analyze** (`agent/analyze.py`): deterministic Python; no LLM. Emits the patterns.

Built with Composio's own SDK + MCP catalog, in the spirit of the role.

### Where a human was needed
- **Rubric design** — what separates `SELF_SERVE_FREE` from `SELF_SERVE_TRIAL` vs
  `APPROVAL_REQUIRED` is a judgement call the agent can't invent; a human wrote it.
- **Disambiguation** — e.g. `developer.copper.co` (digital-asset custody) is a
  *different* company from Copper CRM; the agent flagged it, a human confirmed.
- **The rate-limit reality** — the 100-way agent fleet hit an account session limit
  at app 11 (documented honestly on the page). A human decided to (a) keep the 11
  live records, (b) complete the rest via a model knowledge pass on the same rubric,
  and (c) run a live web sample to measure how trustworthy that pass is.

## Run it

```bash
pip install -r requirements.txt
export COMPOSIO_API_KEY=...   # free tier, 20k calls/mo: https://dashboard.composio.dev/settings
export ANTHROPIC_API_KEY=...

python agent/run_research.py --limit 5   # research first 5 missing apps → data/pass1/
python agent/verify.py --ids 1 2 3       # adversarially verify those → data/verified/
python agent/analyze.py --json           # recompute data/analysis.json
```

`run_research.py` is **idempotent/resumable**: it only researches apps that don't yet
have a `data/pass1/<id>.json`, so a rerun after a rate limit fills the gaps.

## Repo layout

| Path | What |
|---|---|
| `data/apps.json` | the 100-app research set |
| `data/dataset.json` | final merged 100-app dataset (source-tagged: `agent` / `model` / `verified`) |
| `data/pass1/` | raw research-agent records (11 produced live before the fleet rate-limited) |
| `data/verification.json` | the accuracy sample: hits, misses, corrections |
| `data/analysis.json` | computed cluster stats |
| `agent/schema.py` | shared JSON schema + rubric + prompts (single source of truth) |
| `agent/run_research.py` / `verify.py` / `analyze.py` | the three loops |
| `site/index.html` | the single-page case study |

## Honesty notes
- 11 apps ran through the full **live** agent research loop; the other 89 were labelled
  by the same rubric from model knowledge and then a live web sample was used to
  measure accuracy. Every row is source-tagged on the page.
- Low-confidence rows (e.g. `fanbasis`, `iPayX`, `Waterfall.io`, `Consensus`) are
  marked as such — "gated / no public API, with evidence" is a valid finding, not a
  failure.
