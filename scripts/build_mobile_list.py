#!/usr/bin/env python3
"""Emit report/prospects_mobile.html - a phone-friendly companies+stands
checklist from data/simulation_prospects.csv (companies only, no orgs)."""
import csv, html, re

TOP20 = ["Vertical Aerospace","ZeroAvia","Rolls-Royce Plc","GKN Aerospace","Evolito",
"Intelligent Energy Ltd","MBDA (UK) / MBDA Corporate","BAE Systems","GCAP Agency and Edgewing",
"Airbus","Leonardo SpA","Hewland Engineering","Helix",
"RTX (Pratt & Whitney | Collins | Raytheon)","ITP Aero","Drive System Design",
"Greenjets Ltd","PMW Dynamics","Nema Ltd","Avvron Ltd"]

rows = list(csv.DictReader(open("data/simulation_prospects.csv", encoding="utf-8")))
companies = [r for r in rows if not r["Category"].startswith("UK organisation")]

def bucket(r):
    t = int(r["Tier (5=hot)"])
    if t == 5: return "t5"
    if t == 4: return "t4"
    if t == 3: return "t3"
    if r["Category"].startswith("UK-based distribution"): return "svc"
    return "low"

groups = {"t5": [], "t4": [], "t3": [], "low": [], "svc": []}
for r in companies:
    groups[bucket(r)].append(r)
groups["t5"].sort(key=lambda r: TOP20.index(r["Company"]) if r["Company"] in TOP20 else 99)
for k in ("t4", "t3", "low", "svc"):
    groups[k].sort(key=lambda r: r["Company"].lower())

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def row_html(r):
    name = html.escape(r["Company"]); stand = html.escape(r["Stand"])
    return (f'<li class="row" data-k="{slug(r["Company"])}" data-s="{html.escape(r["Company"].lower())} {html.escape(r["Stand"].lower())}">'
            f'<button type="button" class="hit" aria-pressed="false">'
            f'<span class="name">{name}</span><span class="stand">{stand}</span></button></li>')

def section(sid, eyebrow, title, items, open_=True):
    body = "\n".join(row_html(r) for r in items)
    if open_:
        return (f'<section class="grp" id="{sid}"><header class="ghead"><span class="eyebrow">{eyebrow}</span>'
                f'<h2>{title}</h2><span class="count">{len(items)}</span></header><ul>{body}</ul></section>')
    return (f'<details class="grp tail" id="{sid}"><summary><span class="eyebrow">{eyebrow}</span>'
            f'<h2>{title}</h2><span class="count">{len(items)}</span></summary><ul>{body}</ul></details>')

sections = "\n".join([
    section("t5", "Tier 5 - walk first", "Hot prospects", groups["t5"]),
    section("t4", "Tier 4", "Strong", groups["t4"]),
    section("t3", "Tier 3", "If time allows", groups["t3"]),
    section("low", "Lower priority", "Other engineering companies", groups["low"], open_=False),
    section("svc", "Not simulation targets", "Distribution & services", groups["svc"], open_=False),
])
total = sum(len(v) for v in groups.values())

page = """<title>FIA2026 — Prospect Stands</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --ground:#F4F6F7; --surface:#FFFFFF; --ink:#14212B; --muted:#5E7079;
  --line:#DCE3E6; --accent:#0E7C86; --accent-ink:#FFFFFF; --done:#9AA9B0;
}
@media (prefers-color-scheme: dark){:root{
  --ground:#0F171E; --surface:#16222B; --ink:#E6EDF1; --muted:#8FA1AB;
  --line:#243541; --accent:#43BCC4; --accent-ink:#0B1418; --done:#4E626D;
}}
:root[data-theme="dark"]{
  --ground:#0F171E; --surface:#16222B; --ink:#E6EDF1; --muted:#8FA1AB;
  --line:#243541; --accent:#43BCC4; --accent-ink:#0B1418; --done:#4E626D;
}
:root[data-theme="light"]{
  --ground:#F4F6F7; --surface:#FFFFFF; --ink:#14212B; --muted:#5E7079;
  --line:#DCE3E6; --accent:#0E7C86; --accent-ink:#FFFFFF; --done:#9AA9B0;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;}
.wrap{max-width:40rem;margin:0 auto;padding:0 0.875rem 4rem}
.top{position:sticky;top:0;z-index:5;background:var(--ground);padding:0.75rem 0 0.625rem;
  border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:0.5rem}
h1{font-size:1.0625rem;margin:0;letter-spacing:-0.01em}
h1 small{display:block;font-size:0.75rem;font-weight:400;color:var(--muted);margin-top:0.125rem}
#q{width:100%;padding:0.625rem 0.75rem;font-size:1rem;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:0.5rem}
#q:focus{outline:2px solid var(--accent);outline-offset:1px}
.grp{margin-top:1.25rem}
.ghead, summary{display:flex;align-items:baseline;gap:0.5rem;padding:0.25rem 0.125rem}
summary{cursor:pointer;list-style:none}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";margin-left:auto;color:var(--muted);font-weight:600}
details[open] summary::after{content:"–"}
details[open] summary .count{color:var(--muted)}
.eyebrow{font-size:0.6875rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--accent)}
.tail .eyebrow{color:var(--muted)}
.ghead h2, summary h2{font-size:0.9375rem;margin:0;font-weight:650}
.count{margin-left:auto;font-size:0.75rem;color:var(--muted);
  font-variant-numeric:tabular-nums}
summary .count{margin-left:0}
ul{list-style:none;margin:0.375rem 0 0;padding:0;display:flex;flex-direction:column;gap:0.375rem}
.hit{display:flex;width:100%;align-items:center;gap:0.75rem;text-align:left;
  padding:0.6875rem 0.75rem;background:var(--surface);color:var(--ink);
  border:1px solid var(--line);border-radius:0.5rem;font:inherit;cursor:pointer;min-height:2.875rem}
.hit:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.name{flex:1 1 auto;min-width:0;overflow-wrap:break-word}
.stand{flex:0 0 auto;max-width:45%;text-align:right;color:var(--accent);font-weight:650;
  font-family:ui-monospace,"SF Mono","Roboto Mono",Menlo,Consolas,monospace;
  font-size:0.875rem;font-variant-numeric:tabular-nums;overflow-wrap:break-word;white-space:normal}
#t5 .hit{border-left:3px solid var(--accent)}
.row.done .hit{opacity:0.55}
.row.done .name{text-decoration:line-through;text-decoration-color:var(--done);color:var(--muted)}
.row.done .name::after{content:" ✓";text-decoration:none;color:var(--accent)}
.row.hide{display:none}
.foot{margin-top:2rem;font-size:0.75rem;color:var(--muted)}
@media (prefers-reduced-motion: no-preference){.hit{transition:opacity 120ms ease}}
</style>
<div class="wrap">
  <div class="top">
    <h1>FIA2026 — prospect stands<small>__TOTAL__ companies · tap a row to mark visited · Farnborough, 20–24 July 2026</small></h1>
    <input id="q" type="search" placeholder="Search company or stand…" aria-label="Search company or stand">
  </div>
  __SECTIONS__
  <p class="foot">Ranked for simulation-tools interest (Tier 5 first, in priority order; others A–Z). Stands verbatim from the official FIA2026 exhibitor listing, all 65 pages. Visited marks are saved on this device.</p>
</div>
<script>
(function(){
  var KEY="fia26-visited", store={};
  try{store=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(store))}catch(e){}}
  document.querySelectorAll(".row").forEach(function(li){
    var k=li.getAttribute("data-k"), btn=li.querySelector(".hit");
    if(store[k]){li.classList.add("done");btn.setAttribute("aria-pressed","true");}
    btn.addEventListener("click",function(){
      var on=li.classList.toggle("done");
      btn.setAttribute("aria-pressed",on?"true":"false");
      if(on){store[k]=1}else{delete store[k]}
      save();
    });
  });
  var q=document.getElementById("q");
  q.addEventListener("input",function(){
    var v=q.value.trim().toLowerCase();
    document.querySelectorAll(".row").forEach(function(li){
      li.classList.toggle("hide", v!=="" && li.getAttribute("data-s").indexOf(v)===-1);
    });
    document.querySelectorAll("details.grp").forEach(function(d){
      if(v!==""){d.setAttribute("open","")}
    });
  });
})();
</script>"""

page = page.replace("__SECTIONS__", sections).replace("__TOTAL__", str(total))
open("report/prospects_mobile.html", "w", encoding="utf-8").write(page)
print("written report/prospects_mobile.html:", len(page), "chars;",
      {k: len(v) for k, v in groups.items()}, "total", total)
