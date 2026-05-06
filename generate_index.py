#!/usr/bin/env python3
"""
generate_index.py — scan solution JSON files, produce a SELF-CONTAINED index.html.
All data embedded as JS — open index.html directly in any browser (no server needed).

Usage:
    python generate_index_new.py
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def js_safe(obj):
    s = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    s = s.replace("</", "<\\/").replace("<!--", "<\\!--")
    return s


HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TTP Solution Explorer</title>
<style>
:root{
  --bg:#f0f4f8;--bg2:#e8eef5;--bg3:#dde6f0;
  --surf:#ffffff;--surf2:#f5f8fc;--surf3:#edf2f7;
  --bd:rgba(180,200,225,0.7);--bd2:rgba(37,99,235,0.35);
  --blue:#2563eb;--blue2:#1d4ed8;--purple:#7c3aed;--green:#059669;
  --amber:#d97706;--red:#dc2626;--cyan:#0891b2;
  --text:#0f172a;--text2:#334155;--muted:#94a3b8;
  --sidew:268px;--rightw:305px;--r:8px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--bg);color:var(--text);height:100vh;display:flex;
  flex-direction:column;overflow:hidden;font-size:13px;
  background-image:
    radial-gradient(ellipse 100% 60% at 15% -5%,rgba(37,99,235,0.05) 0%,transparent 55%),
    radial-gradient(ellipse 70% 50% at 85% 105%,rgba(124,58,237,0.04) 0%,transparent 55%);
}
header{
  flex-shrink:0;height:52px;background:rgba(255,255,255,0.98);
  border-bottom:1px solid var(--bd);display:flex;align-items:center;
  gap:14px;padding:0 18px;position:relative;
  box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
header::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent 0%,rgba(37,99,235,0.45) 30%,rgba(124,58,237,0.35) 70%,transparent 100%);
}
.logo-wrap{display:flex;align-items:center;gap:10px}
.logo-ico{
  width:32px;height:32px;border-radius:9px;flex-shrink:0;
  background:linear-gradient(135deg,rgba(37,99,235,0.12),rgba(124,58,237,0.1));
  border:1px solid rgba(37,99,235,0.25);font-size:16px;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 2px 8px rgba(37,99,235,0.12);
}
.logo-text h1{
  font-size:14px;font-weight:800;letter-spacing:-0.025em;
  background:linear-gradient(90deg,var(--blue),var(--cyan) 50%,var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.logo-text .sub{font-size:9px;color:var(--muted);font-weight:500;letter-spacing:0.08em;text-transform:uppercase;margin-top:1px}
.hdr-div{width:1px;height:22px;background:var(--bd)}
#hdr-stats{margin-left:auto;display:flex;align-items:center;gap:6px}
.stat-chip{display:flex;align-items:center;gap:5px;padding:4px 10px;
  background:rgba(37,99,235,0.05);border:1px solid rgba(37,99,235,0.18);border-radius:20px;
  font-size:10px;color:var(--text2);font-weight:500;
}
.stat-chip b{color:var(--blue);font-weight:700}
#stat-gen{font-size:10px;color:var(--muted)}
.layout{display:flex;flex:1;overflow:hidden}
#sidebar{width:var(--sidew);min-width:var(--sidew);background:var(--surf);border-right:1px solid var(--bd);
  display:flex;flex-direction:column;overflow:hidden}
.stop{padding:10px 12px;border-bottom:1px solid var(--bd);flex-shrink:0}
.slabel{
  font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;
  color:var(--muted);margin-bottom:7px;display:flex;align-items:center;gap:7px;
}
.slabel::after{content:'';flex:1;height:1px;background:var(--bd)}
.search-wrap{position:relative}
.search-ico{position:absolute;left:9px;top:50%;transform:translateY(-52%);color:var(--muted);font-size:12px;pointer-events:none}
#search{
  width:100%;padding:6px 10px 6px 28px;
  background:var(--bg3);border:1px solid var(--bd);
  border-radius:var(--r);color:var(--text);font-size:11px;
  outline:none;transition:border-color .2s,box-shadow .2s;font-family:inherit;
}
#search:focus{border-color:var(--blue2);box-shadow:0 0 0 3px rgba(96,165,250,0.1)}
#search::placeholder{color:var(--muted)}
#tree{flex:1;overflow-y:auto;padding:4px 0 10px}
#tree::-webkit-scrollbar{width:3px}#tree::-webkit-scrollbar-thumb{background:var(--bd)}
.t-run{margin-bottom:2px}
.t-run-hdr{
  display:flex;align-items:center;gap:6px;padding:6px 8px;cursor:pointer;
  border-radius:var(--r);margin:0 5px;user-select:none;transition:background .15s;
}
.t-run-hdr:hover{background:var(--surf2)}
.chev{font-size:7px;color:var(--muted);transition:transform .2s;flex-shrink:0}
.open>.chev{transform:rotate(90deg)}
.s-badge{font-size:9px;font-weight:700;padding:2px 7px;border-radius:9px;flex-shrink:0;letter-spacing:0.02em}
.s-gurobi{background:rgba(37,99,235,0.08);color:#1d4ed8;border:1px solid rgba(37,99,235,0.2)}
.s-hexaly{background:rgba(124,58,237,0.08);color:#6d28d9;border:1px solid rgba(124,58,237,0.2)}
.s-ica_gurobi{background:rgba(5,150,105,0.08);color:#047857;border:1px solid rgba(5,150,105,0.2)}
.s-ica_concorde_gurobi{background:rgba(217,119,6,0.08);color:#b45309;border:1px solid rgba(217,119,6,0.2)}
.t-run-name{font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text2)}
.t-cnt{font-size:9px;color:var(--muted);flex-shrink:0;background:rgba(0,0,0,0.04);border:1px solid var(--bd);padding:1px 6px;border-radius:8px}
.t-run-body{margin-left:6px}
.t-pool-hdr{
  display:flex;align-items:center;gap:5px;padding:4px 8px;cursor:pointer;
  border-radius:6px;margin:1px 5px;font-size:11px;color:var(--muted);transition:background .15s,color .15s;
}
.t-pool-hdr:hover{background:var(--surf2);color:var(--text2)}
.t-pool-body{margin-left:10px}
.t-file{
  display:flex;align-items:center;gap:6px;padding:4px 8px;border-radius:6px;
  margin:1px 5px;cursor:pointer;font-size:11px;color:var(--muted);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  transition:background .15s,color .15s;border:1px solid transparent;
}
.t-file:hover{background:rgba(37,99,235,0.06);color:var(--text2)}
.t-file.active{background:rgba(37,99,235,0.08);color:var(--blue);border-color:rgba(37,99,235,0.3);border-left:2px solid var(--blue);padding-left:6px}
#map-area{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
#toolbar{
  flex-shrink:0;height:44px;border-bottom:1px solid var(--bd);
  display:flex;align-items:center;gap:8px;padding:0 14px;
  background:rgba(255,255,255,0.97);box-shadow:0 1px 3px rgba(0,0,0,0.04);
}
#toolbar-title{font-size:12px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text2)}
.tbtn-group{display:flex;gap:4px;margin-left:auto}
.tbtn{
  padding:4px 11px;border:1px solid var(--bd);border-radius:6px;background:transparent;
  color:var(--muted);font-size:11px;font-weight:500;cursor:pointer;
  transition:all .15s;white-space:nowrap;font-family:inherit;
}
.tbtn:hover{border-color:var(--bd2);color:var(--blue);background:rgba(37,99,235,0.04)}
.tbtn.on{background:rgba(37,99,235,0.08);border-color:rgba(37,99,235,0.3);color:var(--blue)}
#btn-fit{background:linear-gradient(135deg,rgba(37,99,235,0.08),rgba(124,58,237,0.06));border-color:rgba(37,99,235,0.25);color:var(--blue)}
#btn-fit:hover{background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(124,58,237,0.1))}
#canvas-wrap{flex:1;position:relative;overflow:hidden;cursor:grab;background:linear-gradient(145deg,#eef3fa 0%,#e6edf7 100%)}
#canvas-wrap.panning{cursor:grabbing}
#map-svg{width:100%;height:100%;display:block}
#welcome{
  position:absolute;inset:0;display:flex;align-items:center;
  justify-content:center;pointer-events:none;
}
.w-card{
  display:flex;flex-direction:column;align-items:center;gap:12px;
  padding:36px 48px;border-radius:16px;
  background:rgba(255,255,255,0.92);border:1px solid rgba(180,200,225,0.7);
  backdrop-filter:blur(20px);box-shadow:0 8px 32px rgba(0,0,0,0.08);
}
.w-ico{font-size:40px;opacity:0.55;animation:float 3s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
#welcome h2{font-size:15px;font-weight:700;color:var(--text2)}
#welcome p{font-size:12px;color:var(--muted);max-width:220px;text-align:center;line-height:1.6;margin-top:2px}
#legend{
  position:absolute;bottom:14px;left:14px;z-index:10;display:none;
  background:rgba(255,255,255,0.96);border:1px solid var(--bd);
  border-radius:10px;padding:11px 15px;backdrop-filter:blur(16px);
  box-shadow:0 4px 20px rgba(0,0,0,0.1);
}
.leg-title{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-bottom:9px}
.leg-row{display:flex;align-items:center;gap:9px;margin-bottom:6px}
.leg-row:last-child{margin-bottom:0}
.leg-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.leg-line{width:18px;height:2px;border-radius:1px;flex-shrink:0}
.leg-lbl{font-size:10px;color:var(--text2)}
#right{width:var(--rightw);min-width:var(--rightw);background:var(--surf);
  border-left:1px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
.psec{padding:12px 14px;border-bottom:1px solid var(--bd);flex-shrink:0}
.sec-lbl{
  font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;
  color:var(--muted);margin-bottom:9px;display:flex;align-items:center;gap:7px;
}
.sec-lbl::after{content:'';flex:1;height:1px;background:var(--bd)}
.kv{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
.kv-k{font-size:11px;color:var(--muted)}
.kv-v{font-size:11px;font-weight:600;color:var(--text)}
.kv-v.c-blue{color:var(--blue)}.kv-v.c-green{color:var(--green)}
.kv-v.c-amber{color:var(--amber)}.kv-v.c-red{color:var(--red)}
.mc-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px}
.mc{
  background:var(--surf2);border:1px solid var(--bd);border-radius:var(--r);
  padding:8px 10px;transition:border-color .2s,box-shadow .2s;
}
.mc:hover{border-color:rgba(37,99,235,0.35);box-shadow:0 2px 8px rgba(37,99,235,0.08)}
.mc.full{grid-column:1/-1}
.mc-lbl{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:var(--muted);margin-bottom:3px}
.mc-val{font-size:17px;font-weight:800;letter-spacing:-0.03em;color:var(--text)}
.mc-val.c-blue{color:var(--blue);text-shadow:none}
.mc-val.c-green{color:var(--green);text-shadow:none}
.spill{
  display:inline-flex;align-items:center;gap:5px;padding:3px 9px;
  border-radius:20px;font-size:9px;font-weight:700;letter-spacing:0.04em;
}
.spill::before{content:'';width:5px;height:5px;border-radius:50%;flex-shrink:0}
.st-OPTIMAL{background:rgba(5,150,105,0.07);color:#047857;border:1px solid rgba(5,150,105,0.2)}
.st-OPTIMAL::before{background:#059669;box-shadow:0 0 5px rgba(5,150,105,0.4);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.45}}
.st-FEASIBLE,.st-TIME_LIMIT,.st-SOLUTION_LIMIT{background:rgba(217,119,6,0.07);color:#b45309;border:1px solid rgba(217,119,6,0.2)}
.st-FEASIBLE::before,.st-TIME_LIMIT::before,.st-SOLUTION_LIMIT::before{background:#d97706}
.st-INFEASIBLE,.st-ERROR{background:rgba(220,38,38,0.07);color:#b91c1c;border:1px solid rgba(220,38,38,0.2)}
.st-INFEASIBLE::before,.st-ERROR::before{background:#dc2626}
.prog-wrap{height:5px;background:rgba(0,0,0,0.07);border-radius:3px;margin:6px 0 3px;overflow:hidden}
.prog-fill{
  height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1);
  background:linear-gradient(90deg,var(--blue2),var(--cyan),var(--purple));
  position:relative;overflow:hidden;
}
.prog-fill::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.2),transparent);
  animation:shimmer 2.5s infinite;
}
@keyframes shimmer{0%{transform:translateX(-200%)}100%{transform:translateX(200%)}}
.prog-lbl{display:flex;justify-content:space-between;font-size:10px;color:var(--muted)}
#items-wrap{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0}
.items-hdr{
  flex-shrink:0;padding:8px 14px 7px;border-bottom:1px solid var(--bd);
  display:flex;align-items:center;gap:8px;background:var(--surf2);
}
.items-hdr h3{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted)}
.items-cnt{font-size:9px;font-weight:700;background:rgba(37,99,235,0.07);color:var(--blue);border-radius:9px;padding:2px 7px;border:1px solid rgba(37,99,235,0.2)}
#tscroll{flex:1;overflow-y:auto;min-height:0}
#tscroll::-webkit-scrollbar{width:3px}#tscroll::-webkit-scrollbar-thumb{background:rgba(0,0,0,0.12);border-radius:2px}
table{width:100%;border-collapse:collapse}
thead th{position:sticky;top:0;background:var(--surf);padding:5px 8px;font-size:9px;
  font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:var(--muted);
  text-align:right;border-bottom:1px solid var(--bd);cursor:pointer;user-select:none;white-space:nowrap;transition:color .15s}
thead th:first-child{text-align:left}thead th:hover{color:var(--blue)}
thead th.asc::after{content:' \u2191';color:var(--blue)}
thead th.desc::after{content:' \u2193';color:var(--blue)}
tbody tr{border-bottom:1px solid rgba(0,0,0,0.05);transition:background .1s}
tbody tr:hover{background:rgba(37,99,235,0.04)}
tbody td{padding:5px 8px;font-size:11px;color:var(--muted);text-align:right}
tbody td:first-child{color:var(--text2);text-align:left;font-weight:600}
tbody td.c-blue{color:var(--blue);font-weight:600}
#tip{
  position:fixed;z-index:999;pointer-events:none;display:none;
  background:rgba(255,255,255,0.98);border:1px solid rgba(37,99,235,0.25);
  border-radius:10px;padding:10px 14px;font-size:11px;min-width:140px;
  box-shadow:0 6px 24px rgba(0,0,0,0.12);backdrop-filter:blur(12px);
}
.tip-title{font-weight:700;color:var(--blue);margin-bottom:6px;font-size:12px}
.tip-row{display:flex;justify-content:space-between;gap:14px;color:var(--muted);margin-bottom:2px}
.tip-val{color:var(--text);font-weight:600}
.code-tag{background:var(--bg3);padding:2px 6px;border-radius:4px;font-size:11px;color:var(--text2)}
/* ── Dark theme ─────────────────────────────────────────── */
body.dark{
  --bg:#0a111e;--bg2:#0d1525;--bg3:#111d2e;
  --surf:#0b1424;--surf2:#0d1828;--surf3:#111f30;
  --bd:rgba(37,70,120,0.45);--bd2:rgba(96,165,250,0.35);
  --blue:#60a5fa;--blue2:#3b82f6;--purple:#a78bfa;--green:#34d399;
  --amber:#fbbf24;--red:#f87171;--cyan:#22d3ee;
  --text:#e2e8f0;--text2:#cbd5e1;--muted:#4a6080;
}
body.dark{background-image:
  radial-gradient(ellipse 100% 60% at 15% -5%,rgba(37,99,235,0.15) 0%,transparent 55%),
  radial-gradient(ellipse 70% 50% at 85% 105%,rgba(124,58,237,0.12) 0%,transparent 55%)}
body.dark header{background:rgba(9,14,26,0.98);box-shadow:0 1px 6px rgba(0,0,0,0.5)}
body.dark .logo-ico{background:linear-gradient(135deg,rgba(96,165,250,0.18),rgba(167,139,250,0.14));border-color:rgba(96,165,250,0.3);box-shadow:0 2px 12px rgba(96,165,250,0.18)}
body.dark .stat-chip{background:rgba(96,165,250,0.08);border-color:rgba(96,165,250,0.2)}
body.dark #toolbar{background:rgba(9,17,30,0.97);box-shadow:none}
body.dark #canvas-wrap{background:radial-gradient(ellipse at 50% 50%,#0d1e36 0%,#060f1c 100%)}
body.dark .w-card{background:rgba(11,20,36,0.88);border-color:rgba(48,70,110,0.45);box-shadow:none}
body.dark #legend{background:rgba(10,17,30,0.94);box-shadow:0 6px 24px rgba(0,0,0,0.5)}
body.dark #tip{background:rgba(11,19,34,0.97);border-color:rgba(96,165,250,0.28);box-shadow:0 8px 32px rgba(0,0,0,0.7)}
body.dark .tbtn:hover{background:rgba(255,255,255,0.03);color:var(--text2);border-color:var(--bd)}
body.dark .tbtn.on{background:rgba(96,165,250,0.1);border-color:rgba(96,165,250,0.3)}
body.dark #btn-fit{background:linear-gradient(135deg,rgba(96,165,250,0.12),rgba(167,139,250,0.08));border-color:rgba(96,165,250,0.28)}
body.dark #btn-fit:hover{background:linear-gradient(135deg,rgba(96,165,250,0.2),rgba(167,139,250,0.15))}
body.dark .mc:hover{border-color:var(--bd2);box-shadow:0 0 0 1px rgba(96,165,250,0.06)}
body.dark .mc-val.c-blue{text-shadow:0 0 18px rgba(96,165,250,0.25)}
body.dark .mc-val.c-green{text-shadow:0 0 18px rgba(52,211,153,0.2)}
body.dark .prog-wrap{background:rgba(255,255,255,0.04)}
body.dark #tscroll::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08)}
body.dark tbody tr{border-bottom-color:rgba(255,255,255,0.04)}
body.dark tbody tr:hover{background:rgba(96,165,250,0.05)}
body.dark .t-cnt{background:rgba(255,255,255,0.04)}
body.dark .t-file:hover{background:rgba(96,165,250,0.06)}
body.dark .t-file.active{background:rgba(96,165,250,0.1);border-color:rgba(96,165,250,0.25)}
body.dark .items-cnt{background:rgba(96,165,250,0.1);border-color:rgba(96,165,250,0.2)}
body.dark .s-gurobi{background:rgba(96,165,250,0.1);color:var(--blue);border-color:rgba(96,165,250,0.22)}
body.dark .s-hexaly{background:rgba(167,139,250,0.1);color:var(--purple);border-color:rgba(167,139,250,0.22)}
body.dark .s-ica_gurobi{background:rgba(52,211,153,0.08);color:var(--green);border-color:rgba(52,211,153,0.2)}
body.dark .s-ica_concorde_gurobi{background:rgba(251,191,36,0.08);color:var(--amber);border-color:rgba(251,191,36,0.2)}
body.dark .st-OPTIMAL{background:rgba(52,211,153,0.1);color:var(--green);border-color:rgba(52,211,153,0.22)}
body.dark .st-OPTIMAL::before{background:var(--green);box-shadow:0 0 6px rgba(52,211,153,0.6)}
body.dark .st-FEASIBLE,body.dark .st-TIME_LIMIT,body.dark .st-SOLUTION_LIMIT{background:rgba(251,191,36,0.1);color:var(--amber);border-color:rgba(251,191,36,0.22)}
body.dark .st-INFEASIBLE,body.dark .st-ERROR{background:rgba(248,113,113,0.1);color:var(--red);border-color:rgba(248,113,113,0.22)}
/* Theme toggle */
#btn-theme{
  flex-shrink:0;width:32px;height:32px;border-radius:8px;border:1px solid var(--bd);
  background:transparent;cursor:pointer;font-size:15px;
  display:flex;align-items:center;justify-content:center;
  transition:all .2s;color:var(--muted);margin-left:6px;
}
#btn-theme:hover{background:var(--surf2);border-color:var(--bd2)}
/* Footer */
#footer{
  flex-shrink:0;height:26px;background:var(--surf);border-top:1px solid var(--bd);
  display:flex;align-items:center;justify-content:center;
  font-size:10px;color:var(--muted);gap:4px;letter-spacing:0.02em;
}
#footer strong{color:var(--text2);font-weight:600}
#footer a{color:var(--blue);text-decoration:none;font-weight:600}
#footer a:hover{text-decoration:underline}
</style>
</head>
<body>
<header>
  <div class="logo-wrap">
    <div class="logo-ico">&#128506;</div>
    <div class="logo-text">
      <h1>TTP Solution Explorer</h1>
      <div class="sub">Traveling Thief Problem</div>
    </div>
  </div>
  <div class="hdr-div"></div>
  <div id="hdr-stats">
    <div class="stat-chip"><b id="stat-runs">&#8212;</b> runs</div>
    <div class="stat-chip"><b id="stat-sols">&#8212;</b> solutions</div>
    <span id="stat-gen"></span>
  </div>
  <button id="btn-theme" onclick="toggleTheme()" title="Toggle dark / light mode">&#127769;</button>
</header>
<div class="layout">
  <aside id="sidebar">
    <div class="stop">
      <div class="slabel">Solutions</div>
      <div class="search-wrap">
        <span class="search-ico">&#128269;</span>
        <input id="search" type="text" placeholder="Filter&#8230;">
      </div>
    </div>
    <div id="tree"></div>
  </aside>
  <main id="map-area">
    <div id="toolbar">
      <span id="toolbar-title" style="color:var(--muted)">Select a solution &#8594;</span>
      <div style="display:flex;gap:5px;margin-left:auto">
        <button class="tbtn on" id="btn-tour">Tour</button>
        <button class="tbtn on" id="btn-items">Items</button>
        <button class="tbtn on" id="btn-labels">Labels</button>
        <button class="tbtn" id="btn-fit">&#10227; Fit</button>
      </div>
    </div>
    <div id="canvas-wrap">
      <div id="welcome">
        <div class="w-card">
          <div class="w-ico">&#128230;</div>
          <h2>No solution loaded</h2>
          <p>Pick a <code class="code-tag">_sol.json</code> from the sidebar.</p>
        </div>
      </div>
      <div id="legend">
        <div class="leg-title">Legend</div>
        <div class="leg-row"><div class="leg-dot" id="leg-depot"></div><span class="leg-lbl">Depot</span></div>
        <div class="leg-row"><div class="leg-dot" id="leg-item"></div><span class="leg-lbl">City with picked item(s)</span></div>
        <div class="leg-row"><div class="leg-dot" id="leg-empty"></div><span class="leg-lbl">City with no picked item(s)</span></div>
        <div class="leg-row"><div class="leg-line" id="leg-edge"></div><span class="leg-lbl">Tour edge</span></div>
      </div>
      <svg id="map-svg"></svg>
    </div>
  </main>
  <aside id="right">
    <div class="psec" id="sec-meta"><div class="sec-lbl">Solution</div><div style="color:var(--muted);font-size:11px">No file loaded</div></div>
    <div class="psec" id="sec-metrics" style="display:none"></div>
    <div id="items-wrap" style="display:none">
      <div class="items-hdr"><h3>Picked Items</h3><span class="items-cnt" id="items-cnt">0</span></div>
      <div id="tscroll"></div>
    </div>
  </aside>
</div>
<div id="footer">
  Powered by&ensp;<strong>Dr. Mahdi Khemakhem</strong>&ensp;&middot;&ensp;University of Sfax, Tunisia&ensp;&middot;&ensp;with the kind help of&ensp;<a href="https://claude.ai" target="_blank" rel="noopener">Claude.ai</a>
</div>
<div id="tip"></div>
<script>
const IDX=__INDEX__;
const SOLS=__SOLUTIONS__;
const CW=900,CH=700,PAD=50;
let sol=null,mapped=null,showTour=true,showItems=true,showLabels=true;
let sortCol='profit',sortDir=-1;
let vb={x:0,y:0,w:CW,h:CH};
let pan={on:false,sx:0,sy:0,ox:0,oy:0};

function isDark(){return document.body.classList.contains('dark');}
function updateLegend(){
  var dk=isDark();
  var depot=document.getElementById('leg-depot');
  var item=document.getElementById('leg-item');
  var empty=document.getElementById('leg-empty');
  var edge=document.getElementById('leg-edge');
  if(!depot)return;
  depot.style.cssText=dk?'background:#f87171;box-shadow:0 0 7px rgba(248,113,113,0.5)'
                        :'background:#ef4444;box-shadow:0 0 5px rgba(239,68,68,0.4)';
  item.style.cssText=dk?'background:#fbbf24;box-shadow:0 0 5px rgba(251,191,36,0.5)'
                       :'background:#f59e0b;box-shadow:0 0 4px rgba(245,158,11,0.4)';
  empty.style.cssText=dk?'background:#2d3b5e;border:1px solid #4a5f8a'
                        :'background:#dbeafe;border:1px solid #93c5fd';
  edge.style.cssText=dk?'background:#9aa3b0':'background:#64748b';
}
function toggleTheme(){
  var dark=document.body.classList.toggle('dark');
  document.getElementById('btn-theme').innerHTML=dark?'&#9728;&#65039;':'&#127769;';
  try{localStorage.setItem('ttp-theme',dark?'dark':'light');}catch(e){}
  updateLegend();
  if(sol)drawMap();
}

(function init(){
  try{
    if(localStorage.getItem('ttp-theme')==='dark'){
      document.body.classList.add('dark');
      document.getElementById('btn-theme').innerHTML='&#9728;&#65039;';
    }
  }catch(e){}
  updateLegend();
  var tot=IDX.runs.reduce(function(s,r){return s+r.pools.reduce(function(s2,p){return s2+p.files.length},0)},0);
  document.getElementById('stat-runs').textContent=IDX.runs.length;
  document.getElementById('stat-sols').textContent=tot;
  document.getElementById('stat-gen').textContent='generated '+IDX.generated_at;
  buildTree();
})();

function buildTree(){
  var tree=document.getElementById('tree');tree.innerHTML='';
  IDX.runs.forEach(function(run){
    var sk=run.solver.replace(/-/g,'_');
    var rd=mk('div','t-run');
    var hdr=mk('div','t-run-hdr open');
    hdr.innerHTML='<span class="chev">&#9658;</span>'
      +'<span class="s-badge s-'+sk+'">'+run.solver+'</span>'
      +'<span class="t-run-name">'+run.run_id+'</span>'
      +'<span class="t-cnt">'+run.pools.reduce(function(s,p){return s+p.files.length},0)+'</span>';
    var body=mk('div','t-run-body');
    hdr.onclick=function(){tog(hdr,body);};
    run.pools.forEach(function(pool){
      var pd=mk('div');
      var ph=mk('div','t-pool-hdr open');
      ph.innerHTML='<span class="chev">&#9658;</span><span>&#128193;</span><span style="flex:1">'+pool.pool+'</span><span class="t-cnt">'+pool.files.length+'</span>';
      var pb=mk('div','t-pool-body');
      ph.onclick=function(e){e.stopPropagation();tog(ph,pb);};
      pool.files.forEach(function(fp){
        var name=fp.split('/').pop().replace(/_sol$/,'');
        var fe=mk('div','t-file');
        fe.innerHTML='<span>&#128196;</span><span title="'+fp+'">'+name+'</span>';
        fe.onclick=function(){loadKey(fp,fe);};
        pb.appendChild(fe);
      });
      pd.appendChild(ph);pd.appendChild(pb);body.appendChild(pd);
    });
    rd.appendChild(hdr);rd.appendChild(body);tree.appendChild(rd);
  });
}

function tog(hdr,body){var o=hdr.classList.toggle('open');body.style.display=o?'':'none';}

document.getElementById('search').oninput=function(e){
  var q=e.target.value.toLowerCase();
  document.querySelectorAll('.t-file').forEach(function(el){
    var s=el.querySelector('span:last-child');
    el.style.display=(!q||(el.textContent+(s?s.title:'')).toLowerCase().includes(q))?'':'none';
  });
};

function loadKey(key,el){
  document.querySelectorAll('.t-file').forEach(function(e){e.classList.remove('active');});
  el.classList.add('active');
  var p=key.split('/');
  sol=SOLS[p[0]]&&SOLS[p[0]][p[1]]&&SOLS[p[0]][p[1]][p[2]];
  if(!sol){alert('Not found: '+key);return;}
  document.getElementById('toolbar-title').textContent=p[2].replace(/_sol$/,'');
  document.getElementById('welcome').style.display='none';
  document.getElementById('legend').style.display='block';
  updateLegend();
  mapped=mapCoords(sol.instance_summary.nodes);
  vb={x:0,y:0,w:CW,h:CH};applyVB();drawMap();renderRight(sol);
}

function mapCoords(nodes){
  var xs=nodes.map(function(n){return n.x;}),ys=nodes.map(function(n){return n.y;});
  var x0=Math.min.apply(null,xs),x1=Math.max.apply(null,xs);
  var y0=Math.min.apply(null,ys),y1=Math.max.apply(null,ys);
  var dx=x1-x0||1,dy=y1-y0||1;
  var W=CW-2*PAD,H=CH-2*PAD,sc=Math.min(W/dx,H/dy);
  var ox=PAD+(W-dx*sc)/2,oy=PAD+(H-dy*sc)/2;
  return nodes.map(function(n){
    return Object.assign({},n,{sx:ox+(n.x-x0)*sc,sy:CH-oy-(n.y-y0)*sc});
  });
}

var NS='http://www.w3.org/2000/svg';
function se(tag,a){var e=document.createElementNS(NS,tag);if(a)for(var k in a)e.setAttribute(k,a[k]);return e;}

function drawMap(){
  if(!sol||!mapped)return;
  var dk=isDark();
  var svg=document.getElementById('map-svg');svg.innerHTML='';
  var tour=sol.solution.tour||[],picked=sol.solution.picked_items||[],n=mapped.length;
  var R=Math.max(3.5,Math.min(8,220/Math.sqrt(n)));
  var RD=R*1.45,RI=R*1.22,RH=R*2.1;
  var SW=Math.max(1.2,Math.min(2.5,70/Math.sqrt(n)));
  var FS=Math.max(7,Math.min(11,260/Math.sqrt(n)));
  var cm={};mapped.forEach(function(nd){cm[nd.index]=nd;});
  var ps={};picked.forEach(function(it){ps[it.city_index]=true;});
  var ia={};picked.forEach(function(it){if(!ia[it.city_index])ia[it.city_index]=[];ia[it.city_index].push(it);});

  /* defs: arrowhead */
  var defs=se('defs');
  var mkr=se('marker',{id:'arr',viewBox:'0 0 8 8',refX:'6',refY:'4',markerWidth:'4',markerHeight:'4',orient:'auto-start-reverse'});
  mkr.appendChild(se('path',{d:'M0,0 L8,4 L0,8 z',fill:dk?'#9aa3b0':'#64748b'}));
  defs.appendChild(mkr);svg.appendChild(defs);

  /* dot grid */
  var gg=se('g',{opacity:dk?'0.06':'0.35'});
  var gs=Math.round(CW/18);
  for(var gx=0;gx<=CW;gx+=gs)for(var gy=0;gy<=CH;gy+=gs)
    gg.appendChild(se('circle',{cx:gx,cy:gy,r:'1.2',fill:dk?'#8099cc':'#c8d5e8'}));
  svg.appendChild(gg);

  /* tour edges */
  if(showTour&&tour.length>1){
    var tc=tour.slice();if(tc[0]!==tc[tc.length-1])tc.push(tc[0]);
    var ne=tc.length-1,eg=se('g');
    for(var i=0;i<ne;i++){
      var a=cm[tc[i]],b=cm[tc[i+1]];if(!a||!b)continue;
      var ax=a.sx,ay=a.sy,bx=b.sx,by=b.sy;
      var ddx=bx-ax,ddy=by-ay,len=Math.sqrt(ddx*ddx+ddy*ddy);if(len<0.5)continue;
      var sh=Math.min(R*0.85,len*0.32);
      var ex=bx-ddx/len*sh,ey=by-ddy/len*sh;
      eg.appendChild(se('line',{x1:ax,y1:ay,x2:ex,y2:ey,
        stroke:dk?'rgba(154,163,176,0.65)':'rgba(71,85,105,0.6)',
        'stroke-width':SW,'stroke-linecap':'round','marker-end':'url(#arr)'}));
    }
    svg.appendChild(eg);
  }

  /* cities */
  var cg=se('g');
  mapped.forEach(function(node){
    var x=node.sx,y=node.sy,isD=(node.index===1),hp=!!ps[node.index],its=ia[node.index]||[];
    if(showItems&&hp)
      cg.appendChild(se('circle',{cx:x,cy:y,r:RH,
        fill:'rgba(251,191,36,.1)',stroke:'rgba(251,191,36,.25)','stroke-width':'0.6'}));
    var r=isD?RD:(showItems&&hp?RI:R);
    var fill=isD?(dk?'#f87171':'#ef4444'):(showItems&&hp?(dk?'#fbbf24':'#f59e0b'):(dk?'#2d3b5e':'#dbeafe'));
    var str=isD?(dk?'#ff9999':'#b91c1c'):(showItems&&hp?(dk?'#fde68a':'#d97706'):(dk?'#4a5f8a':'#93c5fd'));
    var c=se('circle',{cx:x,cy:y,r:r,fill:fill,stroke:str,'stroke-width':isD?'1.5':'1',style:'cursor:pointer'});
    (function(nd,it,dep){
      c.addEventListener('mouseenter',function(e){showTip(e,nd,it,dep);});
      c.addEventListener('mousemove',moveTip);
      c.addEventListener('mouseleave',hideTip);
    })(node,its,isD);
    cg.appendChild(c);
    if(showItems&&its.length>1){
      var tb=se('text',{x:x+r+1.5,y:y+r*0.9,'font-size':FS*0.82,'font-weight':'700',fill:dk?'#fbbf24':'#d97706','pointer-events':'none'});
      tb.textContent='\u00d7'+its.length;cg.appendChild(tb);
    }
    if(showLabels){
      var tl=se('text',{x:x+r+1.5,y:y-r*0.8,'font-size':FS,
        fill:isD?(dk?'#f87171':'#ef4444'):(hp?(dk?'#fbbf24':'#f59e0b'):(dk?'#5a7aa8':'#475569')),'pointer-events':'none'});
      tl.textContent=node.index;cg.appendChild(tl);
    }
  });
  svg.appendChild(cg);
}

/* pan & zoom */
var wrap=document.getElementById('canvas-wrap');
wrap.addEventListener('wheel',function(e){
  if(!sol)return;e.preventDefault();
  var f=e.deltaY>0?1.10:0.91,rect=wrap.getBoundingClientRect();
  var mx=(e.clientX-rect.left)/rect.width*vb.w+vb.x,my=(e.clientY-rect.top)/rect.height*vb.h+vb.y;
  vb.w*=f;vb.h*=f;vb.x=mx-(mx-vb.x)*f;vb.y=my-(my-vb.y)*f;applyVB();
},{passive:false});
wrap.addEventListener('mousedown',function(e){
  if(e.button!==0)return;
  pan.on=true;pan.sx=e.clientX;pan.sy=e.clientY;pan.ox=vb.x;pan.oy=vb.y;
  wrap.classList.add('panning');
});
window.addEventListener('mousemove',function(e){
  if(!pan.on)return;var rect=wrap.getBoundingClientRect();
  vb.x=pan.ox-(e.clientX-pan.sx)/rect.width*vb.w;
  vb.y=pan.oy-(e.clientY-pan.sy)/rect.height*vb.h;applyVB();
});
window.addEventListener('mouseup',function(){pan.on=false;wrap.classList.remove('panning');});
function applyVB(){document.getElementById('map-svg').setAttribute('viewBox',vb.x+' '+vb.y+' '+vb.w+' '+vb.h);}

document.getElementById('btn-tour').onclick=function(e){showTour=!showTour;e.currentTarget.classList.toggle('on',showTour);if(sol)drawMap();};
document.getElementById('btn-items').onclick=function(e){showItems=!showItems;e.currentTarget.classList.toggle('on',showItems);if(sol)drawMap();};
document.getElementById('btn-labels').onclick=function(e){showLabels=!showLabels;e.currentTarget.classList.toggle('on',showLabels);if(sol)drawMap();};
document.getElementById('btn-fit').onclick=function(){vb={x:0,y:0,w:CW,h:CH};applyVB();};

function showTip(e,node,items,isD){
  var tip=document.getElementById('tip');
  var h='<div class="tip-title">City '+node.index+(isD?' (depot)':'')+'</div>';
  h+='<div class="tip-row"><span>Coords</span><span class="tip-val">('+node.x+', '+node.y+')</span></div>';
  if(items.length){
    var tp=items.reduce(function(s,i){return s+i.profit;},0),tw=items.reduce(function(s,i){return s+i.weight;},0);
    h+='<div class="tip-row"><span>Items</span><span class="tip-val">'+items.length+'</span></div>';
    h+='<div class="tip-row"><span>Profit</span><span class="tip-val">'+tp.toFixed(1)+'</span></div>';
    h+='<div class="tip-row"><span>Weight</span><span class="tip-val">'+tw+'</span></div>';
  }
  tip.innerHTML=h;moveTip(e);tip.style.display='block';
}
function moveTip(e){var t=document.getElementById('tip');t.style.left=(e.clientX+14)+'px';t.style.top=(e.clientY-10)+'px';}
function hideTip(){document.getElementById('tip').style.display='none';}

function renderRight(s){
  var meta=s.meta,status=s.status,inst=s.instance_summary,metrics=s.solution.metrics,picked=s.solution.picked_items||[];
  var sk=meta.solver.replace(/-/g,'_'),sc2='st-'+status.solver_status;
  document.getElementById('sec-meta').innerHTML=
    '<div class="sec-lbl">Solution</div>'+
    '<div class="kv"><span class="kv-k">Instance</span><span class="kv-v" style="font-size:10px;max-width:155px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+meta.instance_name+'">'+meta.instance_name+'</span></div>'+
    '<div class="kv"><span class="kv-k">Solver</span><span class="kv-v"><span class="s-badge s-'+sk+'">'+meta.solver+'</span></span></div>'+
    '<div class="kv"><span class="kv-k">Status</span><span class="kv-v"><span class="spill '+sc2+'">'+status.solver_status+'</span></span></div>'+
    '<div class="kv"><span class="kv-k">Solve time</span><span class="kv-v c-blue">'+((status.solve_time_seconds||0).toFixed(2))+' s</span></div>'+
    (status.mip_gap_percent!=null?'<div class="kv"><span class="kv-k">MIP gap</span><span class="kv-v '+(status.mip_gap_percent>5?'c-amber':'c-green')+'">'+status.mip_gap_percent.toFixed(3)+' %</span></div>':'')+
    '<div class="kv"><span class="kv-k">Solved at</span><span class="kv-v" style="font-size:10px">'+meta.solved_at+'</span></div>';
  var secM=document.getElementById('sec-metrics');secM.style.display='';
  var frac=metrics.capacity_used_fraction,pct=frac!=null?(frac*100).toFixed(1):'\u2014';
  secM.innerHTML=
    '<div class="sec-lbl">'+inst.dimension+' cities \u00b7 '+inst.number_of_items+' items</div>'+
    '<div class="mc-grid">'+
      '<div class="mc full"><div class="mc-lbl">Objective</div><div class="mc-val c-blue">'+((status.objective||0).toFixed(2))+'</div></div>'+
      '<div class="mc"><div class="mc-lbl">Profit</div><div class="mc-val c-green">'+((metrics.total_profit||0).toFixed(1))+'</div></div>'+
      '<div class="mc"><div class="mc-lbl">Distance</div><div class="mc-val">'+((metrics.total_distance||0).toFixed(1))+'</div></div>'+
    '</div>'+
    '<div class="kv"><span class="kv-k">Weight / Cap</span><span class="kv-v">'+(metrics.total_weight||'\u2014')+' / '+inst.capacity_of_knapsack+'</span></div>'+
    '<div class="prog-wrap"><div class="prog-fill" style="width:'+(frac!=null?Math.min(frac*100,100):0)+'%"></div></div>'+
    '<div class="prog-lbl"><span>Capacity used</span><span style="color:var(--blue)">'+pct+' %</span></div>'+
    '<div class="kv" style="margin-top:6px"><span class="kv-k">Items picked</span><span class="kv-v">'+metrics.num_items_picked+' / '+metrics.num_items_total+'</span></div>'+
    '<div class="kv"><span class="kv-k">Speed range</span><span class="kv-v">['+inst.min_speed+', '+inst.max_speed+']</span></div>'+
    '<div class="kv"><span class="kv-k">Rent ratio</span><span class="kv-v">'+inst.renting_ratio+'</span></div>'+
    '<div class="kv"><span class="kv-k">Type</span><span class="kv-v" style="font-size:10px">'+inst.knapsack_data_type+'</span></div>'+
    (status.upper_bound!=null&&status.upper_bound!==status.objective?'<div class="kv"><span class="kv-k">Upper bound</span><span class="kv-v c-amber">'+status.upper_bound.toFixed(2)+'</span></div>':'');
  var iw=document.getElementById('items-wrap');iw.style.display=picked.length?'':'none';
  document.getElementById('items-cnt').textContent=picked.length;
  renderTable(picked);
}

var COLS=[{k:'city_index',l:'City'},{k:'item_index',l:'Item'},{k:'profit',l:'Profit'},{k:'weight',l:'Weight'},{k:'density',l:'p/w'}];
function renderTable(items){
  var sc=document.getElementById('tscroll');if(!items.length){sc.innerHTML='';return;}
  var sorted=items.slice().sort(function(a,b){
    var va=sortCol==='density'?a.profit/a.weight:a[sortCol];
    var vb2=sortCol==='density'?b.profit/b.weight:b[sortCol];
    return sortDir*(va-vb2);
  });
  var h='<table><thead><tr>';
  COLS.forEach(function(c){h+='<th class="'+(sortCol===c.k?(sortDir>0?'asc':'desc'):'')+'" data-col="'+c.k+'">'+c.l+'</th>';});
  h+='</tr></thead><tbody>';
  sorted.forEach(function(it){
    var d=it.weight>0?(it.profit/it.weight).toFixed(2):'\u2014';
    h+='<tr><td>'+it.city_index+'</td><td>'+it.item_index+'</td>'
      +'<td class="c-blue">'+(typeof it.profit==='number'?it.profit.toFixed(1):it.profit)+'</td>'
      +'<td>'+it.weight+'</td><td>'+d+'</td></tr>';
  });
  h+='</tbody></table>';sc.innerHTML=h;
  sc.querySelectorAll('thead th').forEach(function(th){
    th.onclick=function(){
      var col=th.dataset.col;
      if(sortCol===col)sortDir*=-1;else{sortCol=col;sortDir=-1;}
      renderTable(items);
    };
  });
}

function mk(tag,cls){var e=document.createElement(tag);if(cls)e.className=cls;return e;}
</script>
</body>
</html>
"""


def main():
    base = Path(__file__).parent
    EXCLUDED = {"solutions_index.json"}
    sol_files = sorted(f for f in base.rglob("*.json") if f.name not in EXCLUDED)

    solutions: dict = {}
    runs_dict: dict = {}

    for f in sol_files:
        parts = f.relative_to(base).parts
        if len(parts) < 3:
            continue
        run_id, pool = parts[0], parts[1]
        sol_key = parts[2].replace(".json", "")
        solver = re.split(r"_\d{8}_\d{6}$", run_id)[0]
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  skipped {f.name}: {e}", file=sys.stderr)
            continue

        # Normalise tour to 1-based if solver stored it 0-based (starts at 0)
        raw_tour = data.get("solution", {}).get("tour", [])
        if raw_tour and raw_tour[0] == 0:
            data["solution"]["tour"] = [c + 1 for c in raw_tour]

        solutions.setdefault(run_id, {}).setdefault(pool, {})[sol_key] = data
        rd = runs_dict.setdefault(run_id, {"run_id": run_id, "solver": solver, "pools": {}})
        rd["pools"].setdefault(pool, []).append(f"{run_id}/{pool}/{sol_key}")

    runs = [
        {
            "run_id": rd["run_id"],
            "solver": rd["solver"],
            "pools": [
                {"pool": p, "files": sorted(fs)}
                for p, fs in sorted(rd["pools"].items())
            ],
        }
        for rd in (runs_dict[k] for k in sorted(runs_dict))
    ]

    index = {"generated_at": datetime.now().isoformat(timespec="seconds"), "runs": runs}

    # Backward-compat JSON index
    (base / "solutions_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    # Build fully self-contained HTML
    html = HTML.replace("__INDEX__", js_safe(index)).replace("__SOLUTIONS__", js_safe(solutions))

    out = base / "index.html"
    out.write_text(html, encoding="utf-8")

    total = sum(len(p["files"]) for r in runs for p in r["pools"])
    print(f"Done: {out}  ({len(html) // 1024} KB, self-contained)")
    print(f"  {len(runs)} run(s)  |  {total} solution(s)")
    print("  Open index.html directly in browser — no server needed!")


if __name__ == "__main__":
    main()
