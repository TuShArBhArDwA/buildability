"""Shared schema, rubric and prompts for the app-research agent.

Every researcher and verifier works against the same rubric so that 100
independent runs produce comparable labels.
"""

APP_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "one_liner": {"type": "string", "description": "What the product does, one sentence"},
        "auth_methods": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["OAuth2", "API key", "Basic", "Personal access token", "JWT",
                         "Session/other token", "AWS SigV4", "None/local", "Other"],
            },
        },
        "primary_auth": {"type": "string", "description": "Auth a third-party integration would use"},
        "access_model": {
            "type": "string",
            "enum": ["SELF_SERVE_FREE", "SELF_SERVE_TRIAL", "APPROVAL_REQUIRED",
                     "PAID_PLAN_REQUIRED", "PARTNER_GATED", "NO_PUBLIC_API"],
        },
        "access_notes": {"type": "string"},
        "api_styles": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["REST", "GraphQL", "SOAP", "gRPC", "Websocket/RTM",
                         "SDK-only", "CLI-only", "None"],
            },
        },
        "api_breadth": {"type": "string", "enum": ["BROAD", "MODERATE", "NARROW", "NONE"]},
        "api_notes": {"type": "string"},
        "webhooks": {"type": "boolean"},
        "official_mcp": {"type": "string", "enum": ["YES_OFFICIAL", "COMMUNITY_ONLY", "NONE_FOUND"]},
        "mcp_notes": {"type": "string"},
        "buildability": {"type": "string", "enum": ["GREEN", "YELLOW", "RED"]},
        "main_blocker": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"claim": {"type": "string"}, "url": {"type": "string"}},
                "required": ["claim", "url"],
                "additionalProperties": False,
            },
        },
        "confidence": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
        "open_questions": {"type": "string"},
    },
    "required": ["id", "name", "one_liner", "auth_methods", "primary_auth", "access_model",
                 "access_notes", "api_styles", "api_breadth", "api_notes", "webhooks",
                 "official_mcp", "mcp_notes", "buildability", "main_blocker", "evidence",
                 "confidence", "open_questions"],
    "additionalProperties": False,
}

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "field_checks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "pass1_value": {"type": "string"},
                    "verdict": {"type": "string",
                                "enum": ["CONFIRMED", "WRONG", "PARTIALLY_WRONG", "UNVERIFIABLE"]},
                    "correct_value": {"type": "string"},
                    "evidence_url": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["field", "pass1_value", "verdict", "correct_value", "evidence_url", "note"],
                "additionalProperties": False,
            },
        },
        "overall_verdict": {"type": "string", "enum": ["CLEAN", "MINOR_ERRORS", "MAJOR_ERRORS"]},
        "corrected": APP_SCHEMA,
    },
    "required": ["id", "name", "field_checks", "overall_verdict", "corrected"],
    "additionalProperties": False,
}

RUBRIC = """\
access_model rubric (pick exactly one):
- SELF_SERVE_FREE: a free account / free dev tier / free sandbox gets WORKING API credentials
  with no payment and no human approval. Includes free-forever developer editions and test
  modes (e.g. payment sandbox keys).
- SELF_SERVE_TRIAL: credentials require starting a product trial of a paid SaaS, but still
  instant and no human approval (e.g. 14-day trial).
- APPROVAL_REQUIRED: an app-review, access-request form, or business-verification step gates
  real API usage (typical for ad platforms and marketplace APIs), even if a sandbox exists.
- PAID_PLAN_REQUIRED: API access exists only on a paid plan and there is no trial/sandbox
  path to credentials.
- PARTNER_GATED: contact-sales, partnership agreement, or existing-enterprise-customer status
  required to get any API access.
- NO_PUBLIC_API: no documented public API at all.

api_breadth rubric: BROAD = most product objects exposed, roughly 100+ endpoints/operations.
MODERATE = the main objects, roughly 20-100. NARROW = a handful of endpoints or a single
function. NONE = no public API.

buildability rubric:
- GREEN: documented public API + self-serve credentials (free or trial) -> a Composio-style
  agent toolkit could be built today.
- YELLOW: buildable, but a real gate slows it down: approval/review process, paid plan
  needed, narrow API, or awkward/unusual auth.
- RED: no public API, or partner/contact-sales gate -> needs business outreach or cannot
  be built.

Special cases: open-source self-hosted apps or CLI tools have no cloud API; auth may be
None/local or instance-level tokens; note in api_notes whether it is still agent-callable
(e.g. as a local CLI skill or against a self-hosted instance). Use NO_PUBLIC_API only if
there is genuinely no HTTP API even when self-hosted.
"""


def research_prompt(app: dict) -> str:
    return f"""\
You are a product-research analyst at Composio, which turns app APIs into tools AI agents
can call. Research ONE app using web search and by fetching OFFICIAL documentation
(developer portals, API references, pricing/access pages). Prefer official docs over blogs.
Aim for roughly 5-12 web operations - be efficient but do not guess.

APP: {app['name']} (id {app['id']})
CATEGORY: {app['category']}
HINT: {app['hint']}

Capture, following the rubric exactly:
1. one_liner - what it does.
2. auth_methods - ALL auth methods its public API supports; primary_auth - the one a
   third-party integration would use.
3. access_model + access_notes - how a developer gets credentials.
4. api_styles + api_breadth + api_notes - documented public API surface.
5. webhooks - outbound webhooks/events offered?
6. official_mcp + mcp_notes - does the VENDOR ship an official MCP server
   (search "{app['name']} MCP server")? COMMUNITY_ONLY if only third-party ones exist.
7. buildability + main_blocker.
8. evidence - 2 to 5 claim+URL pairs covering at minimum: auth docs, API reference, and the
   access/pricing gate. Only use URLs you actually visited or saw in search results.
   NEVER invent a URL.
9. confidence - HIGH only if official docs confirm auth, access_model and API surface.
   MEDIUM if partly inferred. LOW if authoritative docs could not be found.
10. open_questions - anything you could not confirm.

{RUBRIC}

HONESTY RULES: "gated" or "no public API" is a VALID finding, not a failure. If you cannot
confidently identify the product from the hint, do NOT guess - set confidence LOW and
explain in open_questions. Wrong-but-confident is the worst outcome.

End with a complete summary of all findings, with the evidence URLs you used."""


def verify_prompt(app: dict, pass1: dict) -> str:
    import json
    return f"""\
You are an adversarial fact-checker at Composio. Another analyst produced the research
record below about {app['name']} ({app['hint']}). Your job is to try to REFUTE it:
independently verify the key fields against OFFICIAL documentation using web search and by
opening doc pages yourself. Do NOT trust the record or its evidence URLs blindly - open
them or find better ones. Assume it may contain plausible-but-wrong claims.

RECORD TO CHECK:
{json.dumps(pass1, indent=1)}

Fields to check (each needs a verdict CONFIRMED / WRONG / PARTIALLY_WRONG / UNVERIFIABLE
plus an evidence URL you actually consulted):
- auth_methods + primary_auth
- access_model (common error: SELF_SERVE_FREE when the API actually needs a paid plan or
  an approval step, or vice versa)
- api_styles + api_breadth
- official_mcp (search "{app['name']} MCP server" yourself; common error: missing an
  official vendor MCP, or calling a community server official)
- buildability + main_blocker (must follow the rubric given the other fields)
- evidence URLs: spot-check that they are real pages that support their claims

{RUBRIC}

End with (a) a per-field verdict list, (b) the CORRECTED full record (same shape as the
input, keeping confirmed values, fixing refuted ones, improving evidence URLs), and (c) an
overall verdict: CLEAN = nothing wrong; MINOR_ERRORS = small fixes (notes, breadth off by
one level, an extra auth method); MAJOR_ERRORS = access_model, primary_auth, buildability
or official_mcp was wrong."""
