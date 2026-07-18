"""Stage 1: build the two composition spikes (radial + folded-axis) from the real export.

Reads board_viz_export.json, trims it to what a static composition needs (per-node
health + equity along each trace, terminal class, weight), and writes two SELF-CONTAINED
HTML files with the data inlined so each works standalone (and as an Artifact). Same real
export feeds both; only the geometry differs. House tokens, mono type, midnight ground.

Run:  python build_spikes.py
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPORT = json.loads((HERE / "board_viz_export.json").read_text(encoding="utf-8"))


def classify(term: str) -> str:
    if term == "RING":
        return "ring"
    if term.startswith("CONVERT"):
        return "convert"
    if term == "REQUESTED":
        return "requested"
    if term == "EXPOSE":
        return "expose"
    if term.startswith("leaf-committed"):
        return "committed"
    return "leaf"


def trim():
    """Compact payload: forks -> traces [{w, cls, term, pts:[[t,h,e],...]}], plus
    node_health, terminals, nodes, meta."""
    out = {"meta": EXPORT["meta"], "nodes": EXPORT["nodes"], "forks": {}}
    for fk, F in EXPORT["forks"].items():
        traces = []
        for tr in F["traces"]:
            pts = [[nd["t"], nd["health"], nd["equity"]] for nd in tr["path"]]
            traces.append({"w": tr["weight"], "cls": classify(tr["terminal"]),
                           "term": tr["terminal"], "pts": pts})
        out["forks"][fk] = {"traces": traces, "node_health": F["node_health"],
                            "terminals": F["terminals"], "root": F["root_value"]}
    return out


DATA = trim()
DATA_JS = json.dumps(DATA, separators=(",", ":"))

TOKENS_CSS = """
:root{
  --midnight:#0A1120; --panel:#0E1626; --panel-2:#111C30;
  --teal:#35C9C0; --teal-dim:#1c5f5c; --gold:#F2C14E; --red:#E24B4A; --rose:#C4788C;
  --ink:#C9D4E3; --ink-dim:#6B7A8F; --line:#1b2740;
  --mono:ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--midnight);color:var(--ink);font-family:var(--mono);
  -webkit-font-smoothing:antialiased;overflow:hidden}
#stage{position:fixed;inset:0}
canvas{display:block;width:100%;height:100%}
.chyron{position:fixed;top:0;left:0;right:0;height:52px;display:flex;align-items:center;
  gap:18px;padding:0 18px;background:linear-gradient(180deg,rgba(10,17,32,.92),rgba(10,17,32,0));
  z-index:5;pointer-events:none}
.chyron .brand{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--ink)}
.chyron .brand b{color:var(--gold);font-weight:600}
.chyron .sub{font-size:11px;color:var(--ink-dim);letter-spacing:.04em}
.toggle{margin-left:auto;display:flex;gap:2px;pointer-events:auto;border:1px solid var(--line);
  border-radius:2px;overflow:hidden}
.toggle button{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  background:var(--panel);color:var(--ink-dim);border:0;padding:7px 13px;cursor:pointer}
.toggle button[aria-pressed=true]{background:var(--panel-2);color:var(--teal)}
.toggle button:focus-visible{outline:2px solid var(--teal);outline-offset:-2px}
.legend{position:fixed;left:18px;bottom:56px;z-index:5;display:flex;flex-direction:column;gap:6px;
  font-size:11px;color:var(--ink-dim);letter-spacing:.03em;pointer-events:none}
.legend .row{display:flex;align-items:center;gap:8px}
.legend .sw{width:16px;height:3px;border-radius:2px}
.badge{position:fixed;right:18px;bottom:14px;z-index:6;font-size:10.5px;color:var(--ink-dim);
  letter-spacing:.04em;text-align:right;line-height:1.5;background:rgba(14,22,38,.7);
  border:1px solid var(--line);border-radius:3px;padding:7px 10px;pointer-events:none}
.badge b{color:var(--ink)}
.badge .src{color:var(--teal);font-weight:600}
.readout{position:fixed;left:18px;bottom:14px;z-index:5;font-size:11px;color:var(--ink-dim);
  letter-spacing:.03em;pointer-events:none}
.readout b{color:var(--ink);font-variant-numeric:tabular-nums}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:640px){.legend{display:none}.chyron .sub{display:none}}
"""

CHROME_HTML = """
<div id="stage"><canvas id="c"></canvas></div>
<div class="chyron">
  <span class="brand">ONE FOR ALL &nbsp;/&nbsp; <b>__TITLE__</b></span>
  <span class="sub">__SUBTITLE__</span>
  <span class="toggle" role="group" aria-label="Metric fork">
    <button id="fk-box" aria-pressed="true">box</button>
    <button id="fk-rapm" aria-pressed="false">rapm</button>
  </span>
</div>
<div class="legend" aria-hidden="true">
  <div class="row"><span class="sw" style="background:var(--gold)"></span> championship ring</div>
  <div class="row"><span class="sw" style="background:var(--teal)"></span> a live future (Ant a Wolf)</div>
  <div class="row"><span class="sw" style="background:var(--red)"></span> proactive reset (dead branch)</div>
  <div class="row"><span class="sw" style="background:var(--rose)"></span> Ant departs (requested)</div>
</div>
<div class="readout" id="ro"></div>
<div class="badge" id="badge"></div>
"""

# ---------------- shared JS prelude (data, colors, badge, fork toggle) --------------
PRELUDE_JS = """
const EXPORT = __DATA__;
const C = {midnight:'#0A1120',teal:'#35C9C0',tealDim:'#1c5f5c',gold:'#F2C14E',
  red:'#E24B4A',rose:'#C4788C',ink:'#C9D4E3',inkDim:'#6B7A8F',line:'#1b2740'};
const clsColor = {ring:C.gold, committed:C.teal, leaf:C.tealDim, convert:C.red, requested:C.rose, expose:C.rose};
let FORK = 'box';
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
let W=0,H=0,DPR=1;
function resize(){DPR=Math.min(window.devicePixelRatio||1,2);
  W=cv.clientWidth;H=cv.clientHeight;cv.width=W*DPR;cv.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0);draw();}
window.addEventListener('resize',resize);
function badge(){
  const m=EXPORT.meta, f=EXPORT.forks[FORK];
  document.getElementById('badge').innerHTML =
    `<span class="src">${m.source}</span> · cliff · forks <b>rapm ${m.fork_weights.rapm} / box ${m.fork_weights.box}</b>`+
    `<br>cap <b>${m.salvage_cap}</b> · P(east) <b>${m.p_east}</b> · ${EXPORT.meta.n_traces_per_fork} traces/fork`+
    `<br>export <b>${m.generated.replace('T',' ').replace('+00:00','Z')}</b>`;
  const t=f.terminals, conv=Object.entries(t).filter(([k])=>k.startsWith('CONVERT')).reduce((a,[,v])=>a+v,0);
  document.getElementById('ro').innerHTML =
    `<b>${FORK}</b> · P(ring) <b>${((t.RING||0)*100).toFixed(1)}%</b> · reset <b>${(conv*100).toFixed(0)}%</b> · Ant departs <b>${((t.REQUESTED||0)*100).toFixed(0)}%</b>`;
}
function setFork(fk){FORK=fk;
  document.getElementById('fk-box').setAttribute('aria-pressed',fk==='box');
  document.getElementById('fk-rapm').setAttribute('aria-pressed',fk==='rapm');
  badge();draw();}
document.getElementById('fk-box').onclick=()=>setFork('box');
document.getElementById('fk-rapm').onclick=()=>setFork('rapm');
// draw order: dead first (background), live/gold last (foreground) so survivors read on top
function ordered(traces){const rank={convert:0,requested:1,leaf:2,expose:1,committed:3,ring:4};
  return [...traces].sort((a,b)=>rank[a.cls]-rank[b.cls]);}
function hexA(hex,a){const n=parseInt(hex.slice(1),16);return `rgba(${n>>16&255},${n>>8&255},${n&255},${a})`;}
"""

# ---------------- RADIAL render ----------------
RADIAL_JS = """
const NODES = EXPORT.nodes;                 // 0..14
const TMAX = 14;
function draw(){
  ctx.clearRect(0,0,W,H);
  const cx=W/2, cy=(H+52)/2;
  const Rout=Math.min(W,H)*0.44, Rin=Math.min(W,H)*0.075;   // node0 outer .. node14 inner
  const rOf = t => Rin + (Rout-Rin)*( (TMAX-t)/TMAX );        // NOW outer, GATE inner
  // concentric calendar rings + labels
  ctx.lineWidth=1;
  for(const nd of NODES){
    const r=rOf(nd.t);
    ctx.strokeStyle=hexA(C.line,0.9); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.stroke();
  }
  // angle assignment: spread traces deterministically, survivors cluster toward a 'corridor'
  const traces=ordered(EXPORT.forks[FORK].traces);
  const n=traces.length;
  traces.forEach((tr,i)=>{
    // corridor angle: title/committed converge near top (the 'way in'); dead fan out
    const base = (i/n)*Math.PI*2;
    const conv = (tr.cls==='ring'||tr.cls==='committed')?0.82:(tr.cls==='leaf'?0.5:0.0);
    const target = -Math.PI/2;                                // 12 o'clock corridor
    const jitter = ((i*97)%100/100-0.5)*0.5;
    const ang = base*(1-conv) + target*conv + jitter*(1-conv);
    const col = clsColor[tr.cls];
    ctx.lineWidth = tr.cls==='ring'?1.6:(tr.cls==='committed'?1.1:0.7);
    ctx.strokeStyle = hexA(col, tr.cls==='ring'?0.9:(tr.cls==='convert'?0.16:0.28));
    ctx.beginPath();
    let last=null;
    tr.pts.forEach((p,k)=>{
      const t=p[0], h=p[1];
      let r=rOf(Math.min(t,TMAX));
      // spiral inward; healthier hugs the corridor angle, weaker drifts off it
      const a = ang + (1-h)*0.6*Math.sin(t*0.7);
      const x=cx+Math.cos(a)*r, y=cy+Math.sin(a)*r;
      if(k===0)ctx.moveTo(x,y); else ctx.lineTo(x,y);
      last={x,y,r,a,t};
    });
    // terminal glyph
    if(tr.cls==='ring'||tr.cls==='committed'){ ctx.lineTo(cx,cy); }         // reach the center
    ctx.stroke();
    if(tr.cls==='convert'&&last){ // dead end freezes as a short red arc at its radius
      ctx.strokeStyle=hexA(C.red,0.5);ctx.lineWidth=2;ctx.beginPath();
      ctx.arc(cx,cy,last.r,last.a-0.05,last.a+0.05);ctx.stroke();
    }
    if(tr.cls==='requested'&&last){ // departure spirals off-canvas (outward)
      ctx.strokeStyle=hexA(C.rose,0.35);ctx.lineWidth=0.8;ctx.beginPath();
      ctx.moveTo(last.x,last.y);
      for(let s=0;s<14;s++){const r=last.r+s*8,a=last.a+s*0.25;ctx.lineTo(cx+Math.cos(a)*r,cy+Math.sin(a)*r);}
      ctx.stroke();
    }
  });
  // the one timeless gold ring at dead center
  ctx.save();
  ctx.strokeStyle=C.gold;ctx.lineWidth=2.5;ctx.beginPath();ctx.arc(cx,cy,Rin*0.62,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle=hexA(C.gold,0.35);ctx.lineWidth=1;ctx.beginPath();ctx.arc(cx,cy,Rin*0.62+5,0,Math.PI*2);ctx.stroke();
  ctx.fillStyle=C.gold;ctx.font='600 10px ui-monospace,Menlo,Consolas,monospace';ctx.textAlign='center';
  ctx.fillText('TITLE',cx,cy+3);
  ctx.restore();
  // ring labels (NOW outer, GATE inner)
  ctx.fillStyle=C.inkDim;ctx.font='10px ui-monospace,Menlo,Consolas,monospace';ctx.textAlign='left';
  const label=(t,txt)=>{const r=rOf(t);ctx.fillText(txt,cx+4,cy-r+12);};
  label(0,'NOW • Jul 2026'); label(7,'2027 playoffs'); label(9,'Jul 2027 gate'); label(14,'2028 GATE');
}
resize();badge();
"""

# ---------------- FOLDED-AXIS render ----------------
FOLDED_JS = """
const NODES=EXPORT.nodes;const TMAX=14;
function draw(){
  ctx.clearRect(0,0,W,H);
  const padL=70,padR=40,padT=76,padB=64;
  const x0=padL,x1=W-padR,yc=(padT+(H-padB))/2, amp=(H-padT-padB)/2*0.92;
  const xOf=t=>x0+(x1-x0)*(t/TMAX);
  const yOf=(h,side)=>yc - side*(1-h)*amp;                 // center=healthy, trouble folds outward
  // faint calendar columns
  ctx.strokeStyle=hexA(C.line,0.8);ctx.lineWidth=1;
  for(const nd of NODES){const x=xOf(nd.t);ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,H-padB);ctx.stroke();}
  // center lane guide
  ctx.strokeStyle=hexA(C.line,1.2);ctx.setLineDash([2,5]);ctx.beginPath();ctx.moveTo(x0,yc);ctx.lineTo(x1,yc);ctx.stroke();ctx.setLineDash([]);
  const RINGS=[{t:7,label:'2027'},{t:14,label:'2028'}];
  const ringR=Math.min(46,amp*0.34);
  const traces=ordered(EXPORT.forks[FORK].traces);
  traces.forEach((tr,i)=>{
    const side = (i%2===0)?1:-1;                            // symmetric fold up/down
    const converge = (tr.cls==='ring'||tr.cls==='committed');
    const col=clsColor[tr.cls];
    ctx.lineWidth=tr.cls==='ring'?1.6:(tr.cls==='committed'?1.05:0.7);
    ctx.strokeStyle=hexA(col,tr.cls==='ring'?0.9:(tr.cls==='convert'?0.15:0.26));
    ctx.beginPath();
    tr.pts.forEach((p,k)=>{
      const t=p[0],h=p[1];const x=xOf(Math.min(t,TMAX));
      let y=yOf(h,side);
      // title paths converge INTO the ring at ring columns; others bend AROUND
      for(const R of RINGS){ const d=Math.abs(t-R.t);
        if(d<1.4){ const pull=(1.4-d)/1.4;
          if(converge) y = y*(1-pull)+yc*pull;
          else { const push=side*ringR*1.5*pull; y = y*(1-pull)+(yc+push)*pull; } } }
      if(k===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    });
    ctx.stroke();
  });
  // gold rings vertically centered at their moments
  for(const R of RINGS){const x=xOf(R.t);
    ctx.strokeStyle=C.gold;ctx.lineWidth=2.4;ctx.beginPath();ctx.arc(x,yc,ringR,0,Math.PI*2);ctx.stroke();
    ctx.strokeStyle=hexA(C.gold,0.3);ctx.lineWidth=1;ctx.beginPath();ctx.arc(x,yc,ringR+5,0,Math.PI*2);ctx.stroke();
    ctx.fillStyle=C.gold;ctx.font='600 10px ui-monospace,Menlo,Consolas,monospace';ctx.textAlign='center';ctx.fillText(R.label,x,yc+3);}
  // axis labels
  ctx.fillStyle=C.inkDim;ctx.font='10px ui-monospace,Menlo,Consolas,monospace';ctx.textAlign='center';
  [[0,'NOW'],[6,'deadline'],[7,'playoffs'],[9,'Jul27 gate'],[14,'2028 GATE']].forEach(([t,l])=>ctx.fillText(l,xOf(t),H-padB+18));
  ctx.save();ctx.translate(20,yc);ctx.rotate(-Math.PI/2);ctx.textAlign='center';ctx.fillStyle=C.inkDim;
  ctx.fillText('← trouble • healthy • trouble →',0,0);ctx.restore();
}
resize();badge();
"""


def page(title, subtitle, render_js):
    # Content-only (no doctype/html/head/body): the Artifact host wraps it, and browsers
    # render the bare fragment fine when the file is opened standalone.
    body = CHROME_HTML.replace("__TITLE__", title).replace("__SUBTITLE__", subtitle)
    js = (PRELUDE_JS.replace("__DATA__", DATA_JS)) + render_js
    return f"""<title>{title} — ONE FOR ALL board</title>
<style>{TOKENS_CSS}</style>
{body}
<script>{js}</script>"""


def main():
    (HERE / "spike_radial.html").write_text(
        page("Radial", "time flows inward · NOW outer ring → the title at dead center", RADIAL_JS),
        encoding="utf-8")
    (HERE / "spike_folded_axis.html").write_text(
        page("Folded axis", "time left → right · health folds around the center lane · rings at 2027 & 2028",
             FOLDED_JS),
        encoding="utf-8")
    for f in ("spike_radial.html", "spike_folded_axis.html"):
        print(f"wrote {HERE/f} ({(HERE/f).stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
