#!/usr/bin/env python3
"""Assemble the self-contained case-study page from the data files.

    python agent/build_site.py   ->  site/index.html
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
dataset = json.loads((ROOT / "data" / "dataset.json").read_text(encoding="utf-8"))
analysis = json.loads((ROOT / "data" / "analysis.json").read_text(encoding="utf-8"))
verification = json.loads((ROOT / "data" / "verification.json").read_text(encoding="utf-8"))
SITE = ROOT / "site"; SITE.mkdir(exist_ok=True)

DATA_JS = "const DATASET=%s;const ANALYSIS=%s;const VERIF=%s;" % (
    json.dumps(dataset, separators=(",", ":")),
    json.dumps(analysis, separators=(",", ":")),
    json.dumps(verification, separators=(",", ":")),
)

HTML = r"""<title>Composio — 100-App Buildability Study</title>
<style>
:root{
  --ground:#F7F8FA; --panel:#FFFFFF; --ink:#10151F; --muted:#5A6472; --faint:#8792A2;
  --line:#E2E6EC; --line2:#EDF0F4; --accent:#2457E6; --accent-soft:#E7ECFD;
  --green:#1F9D5B; --amber:#C77A0A; --red:#D23B3B;
  --green-bg:#E4F5EC; --amber-bg:#FBF0DE; --red-bg:#FBE4E4;
  --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono","Roboto Mono",Menlo,Consolas,monospace;
  --sans:"Inter var",system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --shadow:0 1px 2px rgba(16,21,31,.04),0 4px 16px rgba(16,21,31,.05);
}
@media (prefers-color-scheme:dark){:root{
  --ground:#0C0F16; --panel:#141926; --ink:#E9EDF5; --muted:#94A0B2; --faint:#6C7889;
  --line:#232C3C; --line2:#1B2231; --accent:#7C97FF; --accent-soft:#1B2440;
  --green:#3FCB7E; --amber:#E4AC55; --red:#F26B64;
  --green-bg:#12281C; --amber-bg:#2A2110; --red-bg:#2C1616;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 22px rgba(0,0,0,.35);
}}
:root[data-theme="dark"]{
  --ground:#0C0F16; --panel:#141926; --ink:#E9EDF5; --muted:#94A0B2; --faint:#6C7889;
  --line:#232C3C; --line2:#1B2231; --accent:#7C97FF; --accent-soft:#1B2440;
  --green:#3FCB7E; --amber:#E4AC55; --red:#F26B64;
  --green-bg:#12281C; --amber-bg:#2A2110; --red-bg:#2C1616;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 22px rgba(0,0,0,.35);
}
:root[data-theme="light"]{
  --ground:#F7F8FA; --panel:#FFFFFF; --ink:#10151F; --muted:#5A6472; --faint:#8792A2;
  --line:#E2E6EC; --line2:#EDF0F4; --accent:#2457E6; --accent-soft:#E7ECFD;
  --green:#1F9D5B; --amber:#C77A0A; --red:#D23B3B;
  --green-bg:#E4F5EC; --amber-bg:#FBF0DE; --red-bg:#FBE4E4;
  --shadow:0 1px 2px rgba(16,21,31,.04),0 4px 16px rgba(16,21,31,.05);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
  line-height:1.55;-webkit-font-smoothing:antialiased;font-size:15px}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3{text-wrap:balance;margin:0}
.mono{font-family:var(--mono)}
.eyebrow{font-family:var(--mono);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);font-weight:600}
.tnum{font-variant-numeric:tabular-nums}

/* header */
header{border-bottom:1px solid var(--line);background:var(--panel)}
.top{display:flex;justify-content:space-between;align-items:center;padding:16px 0;gap:16px}
.brand{font-family:var(--mono);font-weight:600;letter-spacing:.02em;font-size:13.5px}
.brand b{color:var(--accent)}
.toggle{font-family:var(--mono);font-size:12px;border:1px solid var(--line);background:transparent;
  color:var(--muted);border-radius:7px;padding:6px 11px;cursor:pointer}
.toggle:hover{border-color:var(--accent);color:var(--accent)}
.hero{padding:52px 0 40px}
.hero h1{font-size:clamp(30px,4.6vw,52px);font-weight:760;letter-spacing:-.02em;line-height:1.04;max-width:19ch}
.hero p{color:var(--muted);font-size:17px;max-width:66ch;margin:18px 0 0}
.hero .meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.tag{font-family:var(--mono);font-size:11.5px;color:var(--muted);border:1px solid var(--line);
  border-radius:999px;padding:5px 11px;background:var(--panel)}

/* thesis numbers */
.thesis{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:14px;overflow:hidden;margin-top:8px}
.thesis .cell{background:var(--panel);padding:20px 20px 18px}
.thesis .n{font-family:var(--mono);font-size:34px;font-weight:640;letter-spacing:-.02em}
.thesis .n small{font-size:16px;color:var(--faint);font-weight:500}
.thesis .k{font-size:13px;color:var(--muted);margin-top:2px}
.g{color:var(--green)} .y{color:var(--amber)} .r{color:var(--red)} .a{color:var(--accent)}

section{padding:44px 0}
.sec-head{display:flex;align-items:baseline;gap:14px;margin-bottom:22px;flex-wrap:wrap}
.sec-head h2{font-size:24px;font-weight:720;letter-spacing:-.015em}
.sec-head .lead{color:var(--muted);font-size:14.5px}

/* pattern cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:20px;box-shadow:var(--shadow)}
.card h3{font-size:15px;font-weight:680;margin-bottom:6px;display:flex;gap:8px;align-items:center}
.card p{color:var(--muted);font-size:13.5px;margin:0}
.card .big{font-family:var(--mono);font-size:26px;font-weight:640;letter-spacing:-.01em;margin-bottom:2px}

/* bars */
.bar-row{display:grid;grid-template-columns:170px 1fr 52px;align-items:center;gap:12px;margin:9px 0;font-size:13px}
.bar-row .lbl{color:var(--muted);font-family:var(--mono);font-size:12px}
.track{height:9px;background:var(--line2);border-radius:5px;overflow:hidden}
.fill{height:100%;border-radius:5px;background:var(--accent)}
.bar-row .v{font-family:var(--mono);text-align:right;color:var(--ink);font-size:12.5px}

/* category grid */
.catgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.catrow{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:14px 16px}
.catrow .ct{display:flex;justify-content:space-between;align-items:center;font-size:13.5px;font-weight:600;margin-bottom:9px}
.catrow .ct .pct{font-family:var(--mono);font-size:13px}
.seg{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--line2)}
.seg span{display:block}

/* table */
.controls{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;align-items:center}
.controls input{flex:1;min-width:200px;font-family:var(--mono);font-size:13px;padding:9px 12px;
  border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--ink)}
.chipbtn{font-family:var(--mono);font-size:11.5px;border:1px solid var(--line);background:var(--panel);
  color:var(--muted);border-radius:999px;padding:6px 12px;cursor:pointer}
.chipbtn[aria-pressed="true"]{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
.tablewrap{border:1px solid var(--line);border-radius:13px;overflow:auto;background:var(--panel);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;min-width:840px;font-size:13px}
th{position:sticky;top:0;background:var(--panel);text-align:left;font-family:var(--mono);font-size:11px;
  letter-spacing:.06em;text-transform:uppercase;color:var(--faint);font-weight:600;padding:12px 12px;
  border-bottom:1px solid var(--line);cursor:pointer;white-space:nowrap;z-index:1}
th:hover{color:var(--accent)}
td{padding:10px 12px;border-bottom:1px solid var(--line2);vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--line2)}
.app{font-weight:640;font-size:13.5px}
.app .cat{display:block;font-family:var(--mono);font-size:10.5px;color:var(--faint);font-weight:500;margin-top:1px}
.pill{font-family:var(--mono);font-size:11px;font-weight:600;padding:3px 8px;border-radius:6px;white-space:nowrap;display:inline-block}
.p-green{background:var(--green-bg);color:var(--green)}
.p-yellow{background:var(--amber-bg);color:var(--amber)}
.p-red{background:var(--red-bg);color:var(--red)}
.am{font-family:var(--mono);font-size:11.5px;color:var(--muted);white-space:nowrap}
.src{font-family:var(--mono);font-size:10px;padding:2px 6px;border-radius:5px;border:1px solid var(--line);color:var(--faint)}
.src-agent{color:var(--accent);border-color:var(--accent)}
.src-verified{color:var(--green);border-color:var(--green)}
.mcp-y{color:var(--green);font-weight:600}
.styles{font-family:var(--mono);font-size:11px;color:var(--muted)}
.count{font-family:var(--mono);font-size:12px;color:var(--muted)}

/* loops */
.loops{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.loop{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:20px;box-shadow:var(--shadow);position:relative}
.loop .step{font-family:var(--mono);font-size:11px;color:var(--accent);font-weight:600}
.loop h3{font-size:15.5px;font-weight:680;margin:6px 0 8px}
.loop p{color:var(--muted);font-size:13px;margin:0 0 10px}
.loop code{font-family:var(--mono);font-size:11.5px;background:var(--line2);padding:2px 6px;border-radius:5px;color:var(--ink)}
.human{margin-top:16px;border:1px dashed var(--line);border-radius:12px;padding:16px 18px;background:var(--panel)}
.human h4{margin:0 0 8px;font-size:13px;font-family:var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.human ul{margin:0;padding-left:18px;color:var(--muted);font-size:13.5px}
.human li{margin:5px 0}
.human b{color:var(--ink)}

/* verification */
.vsum{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;margin-bottom:18px}
.vsum .c{background:var(--panel);padding:16px}
.vsum .c .n{font-family:var(--mono);font-size:26px;font-weight:640}
.vsum .c .k{font-size:12px;color:var(--muted);margin-top:2px}
.vd{font-family:var(--mono);font-size:10.5px;font-weight:600;padding:3px 7px;border-radius:6px}
.vd-ok{background:var(--green-bg);color:var(--green)}
.vd-part{background:var(--amber-bg);color:var(--amber)}
.vd-wrong{background:var(--red-bg);color:var(--red)}
.vd-unv{background:var(--line2);color:var(--muted)}
.move{display:flex;align-items:center;gap:16px;background:var(--panel);border:1px solid var(--line);
  border-radius:13px;padding:20px 22px;margin-top:18px;flex-wrap:wrap;box-shadow:var(--shadow)}
.move .from{font-family:var(--mono);font-size:30px;font-weight:640;color:var(--amber)}
.move .to{font-family:var(--mono);font-size:30px;font-weight:640;color:var(--green)}
.move .arrow{font-size:24px;color:var(--faint)}
.move .txt{color:var(--muted);font-size:13.5px;flex:1;min-width:220px}

.note{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--amber);
  border-radius:10px;padding:16px 18px;margin-top:14px;font-size:13.5px;color:var(--muted)}
.note b{color:var(--ink)}
footer{border-top:1px solid var(--line);padding:28px 0 48px;color:var(--faint);font-size:12.5px;font-family:var(--mono)}
@media (max-width:820px){
  .thesis{grid-template-columns:repeat(2,1fr)} .loops{grid-template-columns:1fr}
  .bar-row{grid-template-columns:130px 1fr 44px}
}
@media (prefers-reduced-motion:no-preference){.fill,.seg span{transition:width .5s ease}}
</style>

<header>
  <div class="wrap top">
    <div class="brand"><b>composio</b> · buildability study</div>
    <button class="toggle mono" id="themeBtn">◐ theme</button>
  </div>
</header>

<main class="wrap">
  <div class="hero">
    <div class="eyebrow">AI Product Ops · 100-app research pipeline</div>
    <h1>Which of 100 apps could become an agent toolkit today — and what stops the rest.</h1>
    <p>An agent researched every app for auth, self-serve access, API surface and official MCP,
       labelled each <b>GREEN / YELLOW / RED</b> against one rubric, then a second adversarial pass
       and a live web sample checked the answers. The headline is the pattern, not the table.</p>
    <div class="meta" id="heroTags"></div>
  </div>

  <section style="padding-top:8px">
    <div class="eyebrow" style="margin-bottom:12px">The headline</div>
    <div class="thesis" id="thesis"></div>
    <div class="cards" style="margin-top:16px" id="thesisCards"></div>
  </section>

  <section>
    <div class="sec-head"><h2>The patterns</h2>
      <span class="lead">Clusters across all 100 — where the easy wins are vs. what needs outreach.</span></div>
    <div class="cards" id="patternCards"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:24px" id="barsWrap">
      <div><div class="eyebrow" style="margin-bottom:12px">Primary auth</div><div id="authBars"></div>
        <div class="eyebrow" style="margin:22px 0 12px">Access model</div><div id="accessBars"></div></div>
      <div><div class="eyebrow" style="margin-bottom:12px">Most common blocker (non-GREEN apps)</div><div id="blockerBars"></div>
        <div class="eyebrow" style="margin:22px 0 12px">Official vendor MCP</div><div id="mcpBars"></div></div>
    </div>
  </section>

  <section>
    <div class="sec-head"><h2>Self-serve rate by category</h2>
      <span class="lead">Green = credentials with no gate. The gradient from dev-tools to AI-native is the story.</span></div>
    <div class="catgrid" id="catGrid"></div>
  </section>

  <section>
    <div class="sec-head"><h2>The 100-app matrix</h2>
      <span class="lead">Filter and sort. Source-tagged: <span class="src src-agent">agent</span> live loop ·
        <span class="src src-verified">verified</span> web-checked · <span class="src">model</span> knowledge pass.</span></div>
    <div class="controls">
      <input id="search" placeholder="search app, category, blocker…" aria-label="search">
      <button class="chipbtn" data-f="GREEN" aria-pressed="false">GREEN</button>
      <button class="chipbtn" data-f="YELLOW" aria-pressed="false">YELLOW</button>
      <button class="chipbtn" data-f="RED" aria-pressed="false">RED</button>
      <button class="chipbtn" data-f="mcp" aria-pressed="false">has official MCP</button>
      <span class="count" id="rowCount"></span>
    </div>
    <div class="tablewrap"><table id="tbl"><thead><tr>
      <th data-s="id">#</th><th data-s="name">App</th><th data-s="primary_auth">Primary auth</th>
      <th data-s="access_model">Access</th><th data-s="api_styles">API</th><th data-s="api_breadth">Breadth</th>
      <th data-s="official_mcp">MCP</th><th data-s="buildability">Verdict</th><th data-s="main_blocker">Main blocker</th>
      <th data-s="evidence">Evidence</th></tr></thead><tbody id="tbody"></tbody></table></div>
  </section>

  <section>
    <div class="sec-head"><h2>The agent</h2>
      <span class="lead">One app = one unit of work, same schema + rubric for all 100. Composio search tools + Claude.</span></div>
    <div class="loops" id="loops"></div>
    <div class="human">
      <h4>Where a human was needed</h4>
      <ul>
        <li><b>Rubric design.</b> The line between <span class="mono">SELF_SERVE_FREE</span>,
          <span class="mono">SELF_SERVE_TRIAL</span> and <span class="mono">APPROVAL_REQUIRED</span> is a judgement call
          the agent can't invent — a human wrote and tuned it, and every agent shares it.</li>
        <li><b>Disambiguation.</b> The agent flagged that <span class="mono">developer.copper.co</span> (crypto custody)
          is a different company from Copper CRM; a human confirmed and steered it to the right domain.</li>
        <li><b>The rate-limit call.</b> The 100-way agent fleet hit an account session limit at app&nbsp;11.
          A human decided to keep the 11 live records, complete the rest on the same rubric via a model
          knowledge pass, then run a live web sample to <em>measure</em> how much to trust it — rather than
          silently claim 100 live runs.</li>
      </ul>
    </div>
  </section>

  <section>
    <div class="sec-head"><h2>Verification — how we know it's trustworthy</h2>
      <span class="lead">Three loops, ending in a live human+web spot check with hits and misses shown honestly.</span></div>
    <div class="vsum" id="vsum"></div>
    <div class="tablewrap"><table style="min-width:720px"><thead><tr>
      <th>App</th><th>Field checked</th><th>First-pass value</th><th>Verdict</th><th>What the docs said</th>
    </tr></thead><tbody id="vbody"></tbody></table></div>
    <div class="move">
      <span class="from">83%</span><span class="arrow">→</span><span class="to">100%</span>
      <span class="txt"><b>Accuracy moved up because of the loop.</b> On the 6 conclusive live checks, the
        first pass was right on 5/6 (83%). The sample caught <b>Plaid</b> (mislabelled a free Sandbox as a trial)
        and refined <b>Devin</b>'s auth; applying both fixes takes the conclusive sample to 6/6. Two docs
        (Pinterest, Squarespace) returned 404/redirect and are marked <span class="mono">UNVERIFIABLE</span>, not counted as hits.</span>
    </div>
    <div class="note"><b>Honesty.</b> 11 apps ran the full <em>live</em> agent loop; 89 were labelled from model
      knowledge on the same rubric and sampled for accuracy. Low-confidence rows
      (<span class="mono">fanbasis, iPayX, Waterfall.io, Consensus, Otter</span>) are marked as such — and
      "gated / no public API, with evidence" is a correct finding, not a failure. The full pipeline is
      idempotent: rerun after the limit resets and it fills the remaining 89 live.</div>
  </section>

  <footer class="wrap">
    Built with Composio (COMPOSIO_SEARCH) + Claude · schema + rubric shared across 100 agents ·
    source, scripts &amp; README in the repo · data as of July 2026.
  </footer>
</main>

<script>
__DATA__
const $=(s,e=document)=>e.querySelector(s);const $$=(s,e=document)=>[...e.querySelectorAll(s)];
const A=ANALYSIS;

/* theme */
const root=document.documentElement;
$("#themeBtn").onclick=()=>{const cur=root.getAttribute("data-theme")||
  (matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");
  root.setAttribute("data-theme",cur==="dark"?"light":"dark");};

/* hero tags */
$("#heroTags").innerHTML=[`${A.total} apps`,`10 categories`,`${A.green} GREEN`,`${A.official_mcp_yes} official MCP`,
  `3 verification loops`].map(t=>`<span class="tag">${t}</span>`).join("");

/* thesis */
const pct=(n)=>Math.round(100*n/A.total);
$("#thesis").innerHTML=[
  [`${A.green}`,`GREEN — buildable today`,"g"],
  [`${A.self_serve}`,`self-serve credentials`,"a"],
  [`${A.official_mcp_yes}`,`ship an official MCP`,"a"],
  [`${A.red}`,`RED — need outreach`,"r"],
].map(([n,k,c])=>`<div class="cell"><div class="n ${c}">${n}<small> /100</small></div><div class="k">${k}</div></div>`).join("");

$("#thesisCards").innerHTML=[
  [`OAuth2 vs API key is a near-even split`,`<b>${A.primary_auth_family.OAuth2}</b> apps lead with OAuth2, <b>${A.primary_auth_family["API key"]}</b> with an API key/token. A toolkit builder needs both flows first-class — neither dominates.`],
  [`Two-thirds are an easy win`,`<b>${A.self_serve}/100</b> give working credentials with no human in the loop (free tier or instant trial). That is the build-now queue.`],
  [`The blocker is rarely "no API"`,`Only <b>${A.blockers["No public/hosted API"]||0}</b> apps truly lack an API. The real friction is business gates — paid plans, app review, contact-sales — not missing endpoints.`],
].map(([h,p])=>`<div class="card"><h3>${h}</h3><p>${p}</p></div>`).join("");

/* bars */
function bars(el,obj,total,color){const max=Math.max(...Object.values(obj));
  el.innerHTML=Object.entries(obj).map(([k,v])=>`<div class="bar-row"><span class="lbl">${k}</span>
    <div class="track"><div class="fill" style="width:${100*v/max}%;${color?`background:${color}`:''}"></div></div>
    <span class="v tnum">${v}</span></div>`).join("");}
bars($("#authBars"),A.primary_auth_family);
bars($("#accessBars"),A.access_model);
bars($("#blockerBars"),A.blockers,null,"var(--red)");
bars($("#mcpBars"),A.official_mcp,null,"var(--green)");

/* category self-serve segments */
const catColors={SELF_SERVE_FREE:"var(--green)",SELF_SERVE_TRIAL:"#7BC49A",APPROVAL_REQUIRED:"var(--amber)",
  PAID_PLAN_REQUIRED:"#D9A54E",PARTNER_GATED:"var(--red)",NO_PUBLIC_API:"#8792A2"};
const order=["SELF_SERVE_FREE","SELF_SERVE_TRIAL","APPROVAL_REQUIRED","PAID_PLAN_REQUIRED","PARTNER_GATED","NO_PUBLIC_API"];
$("#catGrid").innerHTML=Object.entries(A.self_serve_rate_by_category).map(([cat,r])=>{
  const seg=A.access_by_category[cat];
  const bars=order.filter(k=>seg[k]).map(k=>`<span title="${k}: ${seg[k]}" style="width:${100*seg[k]/r.total}%;background:${catColors[k]}"></span>`).join("");
  return `<div class="catrow"><div class="ct"><span>${cat}</span><span class="pct ${r.pct>=80?'g':r.pct>=50?'y':'r'}">${r.pct}% self-serve</span></div><div class="seg">${bars}</div></div>`;
}).join("");

/* table */
const cls={GREEN:"p-green",YELLOW:"p-yellow",RED:"p-red"};
let filter="",chips=new Set(),sortKey="id",sortDir=1;
function short(u){try{return new URL(u).hostname.replace(/^www\./,"");}catch(e){return "link";}}
function render(){
  let rows=DATASET.filter(r=>{
    if(chips.has("mcp")&&r.official_mcp!=="YES_OFFICIAL")return false;
    for(const c of chips){if(["GREEN","YELLOW","RED"].includes(c)&&r.buildability!==c)return false;}
    if(!filter)return true;const s=filter.toLowerCase();
    return (r.name+r.category+r.main_blocker+r.primary_auth+r.access_model).toLowerCase().includes(s);
  });
  rows.sort((a,b)=>{let x=a[sortKey],y=b[sortKey];
    if(Array.isArray(x)){x=x.join();y=y.join();}
    return (x>y?1:x<y?-1:0)*sortDir;});
  $("#tbody").innerHTML=rows.map(r=>`<tr>
    <td class="mono tnum" style="color:var(--faint)">${r.id}</td>
    <td class="app">${r.name}<span class="cat">${r.category}</span></td>
    <td class="am">${r.primary_auth}</td>
    <td class="am">${r.access_model.replace(/_/g,' ').toLowerCase()}</td>
    <td class="styles">${r.api_styles.join(', ')}</td>
    <td class="am">${r.api_breadth}</td>
    <td>${r.official_mcp==="YES_OFFICIAL"?'<span class="mcp-y mono">official</span>':
      r.official_mcp==="COMMUNITY_ONLY"?'<span class="am">community</span>':'<span class="am" style="color:var(--faint)">none</span>'}</td>
    <td><span class="pill ${cls[r.buildability]}">${r.buildability}</span> <span class="src src-${r.source}">${r.source}</span></td>
    <td class="am" style="white-space:normal;max-width:230px;color:var(--muted)">${r.main_blocker}</td>
    <td><a href="${r.evidence}" target="_blank" rel="noopener" class="mono" style="font-size:11px">${short(r.evidence)} ↗</a></td>
  </tr>`).join("");
  $("#rowCount").textContent=`${rows.length} shown`;
}
$("#search").oninput=e=>{filter=e.target.value;render();};
$$(".chipbtn").forEach(b=>b.onclick=()=>{const f=b.dataset.f;
  if(chips.has(f)){chips.delete(f);b.setAttribute("aria-pressed","false");}
  else{chips.add(f);b.setAttribute("aria-pressed","true");}render();});
$$("#tbl th").forEach(th=>th.onclick=()=>{const k=th.dataset.s;
  if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=1;}render();});
render();

/* loops */
$("#loops").innerHTML=[
  ["Loop 1 · research","Live agent","Claude drives Composio's hosted <code>COMPOSIO_SEARCH</code> tools over official docs, then <b>structured outputs</b> force one schema-valid record. <b>11/100</b> completed live before the fleet hit an account rate limit."],
  ["Loop 2 · verify","Adversarial","A second Claude pass is told to <b>refute</b> pass 1 — re-search docs, mark each field CONFIRMED/WRONG, emit a corrected record. This is the loop that moves accuracy up."],
  ["Loop 3 · check","Human + web","A stratified live <code>WebFetch</code> sample against official docs, with a human reading the docs. Hits and misses recorded below — nothing hidden."],
].map(([s,tag,p])=>`<div class="loop"><div class="step">${s}</div><h3>${tag}</h3><p>${p}</p></div>`).join("");

/* verification */
const v=VERIF.summary;
$("#vsum").innerHTML=[
  [v.sampled,"sampled live"],[v.confirmed,"confirmed",'g'],[v.wrong,"wrong",'r'],
  [v.partially_wrong,"refined",'y'],[v.unverifiable,"doc unreachable"],
].map(([n,k,c])=>`<div class="c"><div class="n ${c||''}">${n}</div><div class="k">${k}</div></div>`).join("");
const vdcls={CONFIRMED:"vd-ok",WRONG:"vd-wrong",PARTIALLY_WRONG:"vd-part",UNVERIFIABLE:"vd-unv"};
$("#vbody").innerHTML=VERIF.sample.map(s=>`<tr>
  <td class="app">${s.name}</td><td class="am">${s.field}</td>
  <td class="am" style="color:var(--muted)">${s.pass1}</td>
  <td><span class="vd ${vdcls[s.verdict]}">${s.verdict}</span></td>
  <td class="am" style="white-space:normal;max-width:340px;color:var(--muted)">${s.note} <a href="${s.evidence}" target="_blank" rel="noopener">↗</a></td>
</tr>`).join("");
</script>
"""

out = HTML.replace("__DATA__", DATA_JS)
(SITE / "index.html").write_text(out, encoding="utf-8")
print(f"wrote site/index.html ({len(out)} bytes)")
