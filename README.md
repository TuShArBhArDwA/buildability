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

**Result:** 46/100 apps carry a live agent record (`source=agent`); the fleet kept
tripping a rolling account session limit, so the remaining 52 were labelled on the
identical rubric via a model knowledge pass (`source=model`) and a live web sample
verified both groups. Rerun after a reset and the idempotent pipeline fills the rest.

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
- **The rate-limit reality** — the ~100-way agent fleet kept tripping a rolling
  account session limit, landing in waves (46 live so far; documented on the page).
  A human decided to (a) keep every live record, (b) label the rest via a model
  knowledge pass on the same rubric, and (c) run a live web sample to measure how
  trustworthy that pass is — rather than silently claim 100 live runs.

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

## Findings (computed by `analyze.py`, mid-2026 data)
- **69 GREEN** (buildable today) / 24 YELLOW / 7 RED
- **70/100 self-serve** credentials; only **3** truly lack a public API
- Primary auth splits **~52 OAuth2 / ~46 API-key** — a toolkit builder needs both
- Biggest blocker is **business gates** (paid plan / app review / contact-sales), not missing endpoints
- Self-serve gradient: Dev-tools & Productivity **100%** → AI/media-native ~**20%**
- **59/100 ship an official vendor MCP** — the 2026 MCP wave is real

## Honesty notes
- **46/100** apps ran through the full **live** agent research loop; the other **52** were
  labelled by the same rubric from model knowledge and then a live web sample verified
  both groups (all 5/5 conclusive knowledge-pass checks held up). Every row is
  source-tagged (`agent` / `model` / `verified`) on the page.
- Verification caught a real miss (**Plaid** — free Sandbox mislabelled as a trial) and
  refined **Devin**'s auth; conclusive-sample accuracy moved 82% → 100% after the fixes.
- Low-confidence rows (e.g. `fanbasis`, `iPayX`, `Waterfall.io`, `Consensus`, `Otter`) are
  marked as such — "gated / no public API, with evidence" is a valid finding, not a failure.
