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
:root {
  --bg:#0b0f1a;--surf:#111827;--surf2:#1a2235;--surf3:#232d42;--bd:#273044;
  --blue:#5b9cf6;--purple:#9d71f0;--green:#34d399;--amber:#fbbf24;
  --red:#f87171;--cyan:#22d3ee;--text:#dde3f0;--muted:#5a6882;
  --sidew:260px;--rightw:295px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',sans-serif;
  background:var(--bg);color:var(--text);height:100vh;display:flex;
  flex-direction:column;overflow:hidden;font-size:13px}
header{flex-shrink:0;height:50px;background:var(--surf);border-bottom:1px solid var(--bd);
  display:flex;align-items:center;gap:12px;padding:0 18px}
header .logo{font-size:20px}
header h1{font-size:15px;font-weight:700;background:linear-gradient(90deg,var(--blue),var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.badge-sm{font-size:10px;color:var(--muted);padding:2px 8px;border:1px solid var(--bd);border-radius:20px;margin-left:2px}
#hdr-stats{margin-left:auto;font-size:11px;color:var(--muted);display:flex;gap:12px}
#hdr-stats b{color:var(--blue)}
#stat-gen{font-size:10px;color:var(--muted)}
.layout{display:flex;flex:1;overflow:hidden}
#sidebar{width:var(--sidew);min-width:var(--sidew);background:var(--surf);border-right:1px solid var(--bd);
  display:flex;flex-direction:column;overflow:hidden}
.stop{padding:10px;border-bottom:1px solid var(--bd);flex-shrink:0}
.slabel{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:6px}
#search{width:100%;padding:5px 10px;background:var(--surf2);border:1px solid var(--bd);
  border-radius:5px;color:var(--text);font-size:11px;outline:none;transition:border-color .15s}
#search:focus{border-color:var(--blue)}#search::placeholder{color:var(--muted)}
#tree{flex:1;overflow-y:auto;padding:4px 0 10px}
#tree::-webkit-scrollbar{width:3px}#tree::-webkit-scrollbar-thumb{background:var(--bd)}
.t-run{margin-bottom:1px}
.t-run-hdr{display:flex;align-items:center;gap:5px;padding:5px 8px;cursor:pointer;
  border-radius:5px;margin:0 3px;user-select:none;transition:background .1s}
.t-run-hdr:hover{background:var(--surf2)}
.chev{font-size:8px;color:var(--muted);transition:transform .15s;flex-shrink:0}
.open > .chev{transform:rotate(90deg)}
.s-badge{font-size:9px;font-weight:700;padding:1px 5px;border-radius:8px;flex-shrink:0}
.s-gurobi{background:#0a1f3d;color:var(--blue)}
.s-hexaly{background:#1a0d37;color:var(--purple)}
.s-ica_gurobi{background:#042a15;color:var(--green)}
.s-ica_concorde_gurobi{background:#2a1700;color:var(--amber)}
.t-run-name{font-size:11px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.t-cnt{font-size:10px;color:var(--muted);flex-shrink:0}
.t-run-body{margin-left:8px}
.t-pool-hdr{display:flex;align-items:center;gap:4px;padding:3px 8px;cursor:pointer;
  border-radius:4px;margin:0 3px;font-size:11px;color:var(--muted);transition:background .1s}
.t-pool-hdr:hover{background:var(--surf2);color:var(--text)}
.t-pool-body{margin-left:12px}
.t-file{display:flex;align-items:center;gap:5px;padding:3px 8px;border-radius:4px;
  margin:0 3px;cursor:pointer;font-size:11px;color:var(--muted);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;transition:background .1s,color .1s}
.t-file:hover{background:var(--surf2);color:var(--text)}
.t-file.active{background:rgba(91,156,246,.12);color:var(--blue);border-left:2px solid var(--blue);padding-left:6px}
#map-area{flex:1;display:flex;flex-direction:column;overflow:hidden;background:var(--bg);min-width:0}
#toolbar{flex-shrink:0;height:42px;border-bottom:1px solid var(--bd);display:flex;
  align-items:center;gap:6px;padding:0 12px;background:var(--surf)}
#toolbar-title{font-size:12px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tbtn{padding:3px 9px;border:1px solid var(--bd);border-radius:4px;background:var(--surf2);
  color:var(--muted);font-size:11px;cursor:pointer;transition:all .15s;white-space:nowrap}
.tbtn:hover{border-color:var(--blue);color:var(--blue)}
.tbtn.on{background:rgba(91,156,246,.12);border-color:var(--blue);color:var(--blue)}
#canvas-wrap{flex:1;position:relative;overflow:hidden;cursor:grab}
#canvas-wrap.panning{cursor:grabbing}
#map-svg{width:100%;height:100%;display:block}
#welcome{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:10px;pointer-events:none}
#welcome .w-ico{font-size:48px;opacity:.12}
#welcome h2{font-size:16px;color:var(--muted);font-weight:500}
#welcome p{font-size:12px;color:var(--muted);max-width:260px;text-align:center;line-height:1.5;opacity:.7}
#legend{position:absolute;top:10px;left:10px;z-index:10;display:none;
  background:rgba(11,15,26,.9);border:1px solid var(--bd);border-radius:8px;
  padding:9px 13px;backdrop-filter:blur(8px);font-size:11px}
.leg-row{display:flex;align-items:center;gap:8px;margin-bottom:5px}
.leg-row:last-child{margin-bottom:0}
.leg-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.leg-line{width:16px;height:2px;border-radius:1px;flex-shrink:0}
.leg-lbl{color:var(--muted)}
#right{width:var(--rightw);min-width:var(--rightw);background:var(--surf);
  border-left:1px solid var(--bd);display:flex;flex-direction:column;overflow:hidden}
.psec{padding:12px 14px;border-bottom:1px solid var(--bd);flex-shrink:0}
.psec h3{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:8px}
.kv{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
.kv-k{font-size:11px;color:var(--muted)}
.kv-v{font-size:11px;font-weight:600;color:var(--text)}
.kv-v.c-blue{color:var(--blue)}.kv-v.c-green{color:var(--green)}
.kv-v.c-amber{color:var(--amber)}.kv-v.c-red{color:var(--red)}.kv-v.big{font-size:15px}
.spill{display:inline-block;padding:1px 7px;border-radius:20px;font-size:9px;font-weight:700}
.st-OPTIMAL{background:rgba(52,211,153,.14);color:var(--green)}
.st-FEASIBLE,.st-TIME_LIMIT,.st-SOLUTION_LIMIT{background:rgba(251,191,36,.14);color:var(--amber)}
.st-INFEASIBLE,.st-ERROR{background:rgba(248,113,113,.14);color:var(--red)}
.prog-wrap{height:4px;background:var(--surf3);border-radius:2px;margin-top:3px;overflow:hidden}
.prog-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,var(--blue),var(--purple));transition:width .4s}
.prog-lbl{display:flex;justify-content:space-between;margin-top:2px;font-size:10px;color:var(--muted)}
#items-wrap{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0}
.items-hdr{flex-shrink:0;padding:8px 14px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:7px}
.items-hdr h3{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.items-cnt{font-size:9px;font-weight:700;background:rgba(91,156,246,.14);color:var(--blue);border-radius:9px;padding:1px 6px}
#tscroll{flex:1;overflow-y:auto;min-height:0}
#tscroll::-webkit-scrollbar{width:3px}#tscroll::-webkit-scrollbar-thumb{background:var(--bd)}
table{width:100%;border-collapse:collapse}
thead th{position:sticky;top:0;background:var(--surf);padding:5px 8px;font-size:9px;
  font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);
  text-align:right;border-bottom:1px solid var(--bd);cursor:pointer;user-select:none;white-space:nowrap}
thead th:first-child{text-align:left}thead th:hover{color:var(--blue)}
thead th.asc::after{content:' \u2191';color:var(--blue)}
thead th.desc::after{content:' \u2193';color:var(--blue)}
tbody tr{border-bottom:1px solid rgba(39,48,68,.5)}tbody tr:hover{background:var(--surf2)}
tbody td{padding:4px 8px;font-size:11px;color:var(--muted);text-align:right}
tbody td:first-child{color:var(--text);text-align:left;font-weight:500}
tbody td.c-blue{color:var(--blue)}
#tip{position:fixed;z-index:999;pointer-events:none;display:none;background:var(--surf2);
  border:1px solid var(--bd);border-radius:7px;padding:7px 11px;font-size:11px;
  min-width:130px;box-shadow:0 6px 20px rgba(0,0,0,.5)}
.tip-title{font-weight:700;color:var(--blue);margin-bottom:4px}
.tip-row{display:flex;justify-content:space-between;gap:12px;color:var(--muted);margin-bottom:1px}
.tip-val{color:var(--text);font-weight:600}
</style>
</head>
<body>
<header>
  <span class="logo">&#128506;</span>
  <h1>TTP Solution Explorer</h1>
  <span class="badge-sm">Traveling Thief Problem</span>
  <div id="hdr-stats">
    <span><b id="stat-runs">&#8212;</b> runs</span>
    <span><b id="stat-sols">&#8212;</b> solutions</span>
    <span id="stat-gen"></span>
  </div>
</header>
<div class="layout">
  <aside id="sidebar">
    <div class="stop">
      <div class="slabel">Solution Files</div>
      <input id="search" type="text" placeholder="&#128269;  Filter&#8230;">
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
        <button class="tbtn"    id="btn-fit">&#10227; Fit</button>
      </div>
    </div>
    <div id="canvas-wrap">
      <div id="welcome">
        <div class="w-ico">&#128230;</div>
        <h2>No solution loaded</h2>
        <p>Pick a <code style="background:var(--surf2);padding:1px 4px;border-radius:3px">_sol.json</code> file on the left.</p>
      </div>
      <div id="legend">
        <div class="leg-row"><div class="leg-dot" style="background:#f87171;border:1.5px solid #ff9999"></div><span class="leg-lbl">Depot</span></div>
        <div class="leg-row"><div class="leg-dot" style="background:#fbbf24;border:1.5px solid #fde68a"></div><span class="leg-lbl">City with items</span></div>
        <div class="leg-row"><div class="leg-dot" style="background:#2d3b5e;border:1.5px solid #4a5f8a"></div><span class="leg-lbl">Empty city</span></div>
        <div class="leg-row"><div class="leg-line" style="background:linear-gradient(90deg,#22d3ee,#9d71f0)"></div><span class="leg-lbl">Tour edge</span></div>
      </div>
      <svg id="map-svg"></svg>
    </div>
  </main>
  <aside id="right">
    <div class="psec" id="sec-meta"><h3>Solution</h3><div style="color:var(--muted);font-size:11px">No file loaded</div></div>
    <div class="psec" id="sec-metrics" style="display:none"></div>
    <div id="items-wrap" style="display:none">
      <div class="items-hdr"><h3>Picked Items</h3><span class="items-cnt" id="items-cnt">0</span></div>
      <div id="tscroll"></div>
    </div>
  </aside>
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

(function init(){
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
  mkr.appendChild(se('path',{d:'M0,0 L8,4 L0,8 z',fill:'#9aa3b0'}));
  defs.appendChild(mkr);svg.appendChild(defs);

  /* dot grid */
  var gg=se('g',{opacity:'0.06'});
  var gs=Math.round(CW/18);
  for(var gx=0;gx<=CW;gx+=gs)for(var gy=0;gy<=CH;gy+=gs)
    gg.appendChild(se('circle',{cx:gx,cy:gy,r:'1.2',fill:'#8099cc'}));
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
        stroke:'rgba(154,163,176,0.65)',
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
    var fill=isD?'#f87171':(showItems&&hp?'#fbbf24':'#2d3b5e');
    var str=isD?'#ff9999':(showItems&&hp?'#fde68a':'#4a5f8a');
    var c=se('circle',{cx:x,cy:y,r:r,fill:fill,stroke:str,'stroke-width':isD?'1.5':'1',style:'cursor:pointer'});
    (function(nd,it,dep){
      c.addEventListener('mouseenter',function(e){showTip(e,nd,it,dep);});
      c.addEventListener('mousemove',moveTip);
      c.addEventListener('mouseleave',hideTip);
    })(node,its,isD);
    cg.appendChild(c);
    if(showItems&&its.length>1){
      var tb=se('text',{x:x+r+1.5,y:y+r*0.9,'font-size':FS*0.82,'font-weight':'700',fill:'#fbbf24','pointer-events':'none'});
      tb.textContent='\u00d7'+its.length;cg.appendChild(tb);
    }
    if(showLabels){
      var tl=se('text',{x:x+r+1.5,y:y-r*0.8,'font-size':FS,
        fill:isD?'#f87171':(hp?'#fbbf24':'#5a7aa8'),'pointer-events':'none'});
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
    '<h3>Solution</h3>'+
    '<div class="kv"><span class="kv-k">Instance</span><span class="kv-v" style="font-size:10px;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+meta.instance_name+'">'+meta.instance_name+'</span></div>'+
    '<div class="kv"><span class="kv-k">Solver</span><span class="kv-v"><span class="s-badge s-'+sk+'">'+meta.solver+'</span></span></div>'+
    '<div class="kv"><span class="kv-k">Status</span><span class="kv-v"><span class="spill '+sc2+'">'+status.solver_status+'</span></span></div>'+
    '<div class="kv"><span class="kv-k">Solve time</span><span class="kv-v c-blue">'+((status.solve_time_seconds||0).toFixed(2))+' s</span></div>'+
    (status.mip_gap_percent!=null?'<div class="kv"><span class="kv-k">MIP gap</span><span class="kv-v '+(status.mip_gap_percent>5?'c-amber':'c-green')+'">'+status.mip_gap_percent.toFixed(3)+' %</span></div>':'')+
    '<div class="kv"><span class="kv-k">Solved at</span><span class="kv-v" style="font-size:10px">'+meta.solved_at+'</span></div>';
  var secM=document.getElementById('sec-metrics');secM.style.display='';
  var frac=metrics.capacity_used_fraction,pct=frac!=null?(frac*100).toFixed(1):'\u2014';
  secM.innerHTML=
    '<h3>'+inst.dimension+' cities \u00b7 '+inst.number_of_items+' items \u00b7 '+inst.knapsack_data_type+'</h3>'+
    '<div class="kv"><span class="kv-k">Objective</span><span class="kv-v c-blue big">'+((status.objective||0).toFixed(2))+'</span></div>'+
    '<div class="kv"><span class="kv-k">Total profit</span><span class="kv-v c-green">'+((metrics.total_profit||0).toFixed(2))+'</span></div>'+
    '<div class="kv"><span class="kv-k">Distance</span><span class="kv-v">'+((metrics.total_distance||0).toFixed(2))+'</span></div>'+
    '<div class="kv"><span class="kv-k">Weight / Cap</span><span class="kv-v">'+(metrics.total_weight||'\u2014')+' / '+inst.capacity_of_knapsack+'</span></div>'+
    '<div class="prog-wrap"><div class="prog-fill" style="width:'+(frac!=null?Math.min(frac*100,100):0)+'%"></div></div>'+
    '<div class="prog-lbl"><span>Capacity</span><span style="color:var(--blue)">'+pct+' %</span></div>'+
    '<div class="kv" style="margin-top:6px"><span class="kv-k">Items picked</span><span class="kv-v">'+metrics.num_items_picked+' / '+metrics.num_items_total+'</span></div>'+
    '<div class="kv"><span class="kv-k">Speed</span><span class="kv-v">['+inst.min_speed+', '+inst.max_speed+']</span></div>'+
    '<div class="kv"><span class="kv-k">Rent ratio</span><span class="kv-v">'+inst.renting_ratio+'</span></div>'+
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
