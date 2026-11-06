// The stage a presentation plays on: one screen, never scrolled. A camera frames the whole diagram
// for the overview and glides to each step's boxes and line, zooming in as far as they allow, so a
// diagram of any size reads without scrolling. Drag pans and the wheel zooms; Overview resets.
//
//   page(html, scene, walk, theme)   Eraser's rendered page, wrapped as the presentation

const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

function css(t) {
  return `<style>
:root{--bg:${t.ground};--surface:${t.surface};--text:${t.strong};--dim:${t.muted};--focus:${t.focus};--line:${t.recessed};--er-ground:${t.ground}}
html,body{margin:0;height:100%;overflow:hidden;background:var(--bg)!important;color:var(--text);font-family:${t.font}}
main{height:100vh;display:grid;grid-template-rows:auto 1fr auto}
header{padding:18px 28px 10px;display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}
.eyebrow{color:var(--dim);font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0}
h1{font-size:24px;line-height:1.2;letter-spacing:-.4px;margin:0;font-weight:650}
#frame{position:relative;overflow:hidden;cursor:grab;touch-action:none;
  background-image:radial-gradient(var(--line) .7px,transparent .7px);background-size:24px 24px}
#frame.dragging{cursor:grabbing}
#eraser-scene{position:absolute;left:0;top:0;transform-origin:0 0;background:transparent!important;will-change:transform}
[data-mdp-id]{transition:opacity .5s ease}.muted-node{opacity:.13}
.active-node .er-shape{--er-border:var(--focus)!important}
.active-edge .er-rel{--er-stroke:var(--focus)!important;--er-label-ink:var(--focus)!important}
.active-edge .er-rel__label{color:var(--focus)!important}.active-edge .er-rel__line{stroke-width:2.6px}
#caption{position:absolute;left:24px;bottom:20px;max-width:min(760px,calc(100% - 48px));margin:0;padding:14px 18px;
  font-size:19px;line-height:1.4;background:color-mix(in srgb,var(--surface) 92%,transparent);border:1px solid var(--line);
  border-left:3px solid var(--focus);border-radius:4px;box-shadow:0 8px 30px rgba(0,0,0,.18)}
.controls{display:flex;gap:10px;align-items:center;border-top:1px solid var(--line);padding:12px 28px;flex-wrap:wrap}
.controls button{font:inherit;font-size:14px;background:var(--surface);color:var(--text);border:1px solid var(--line);border-radius:4px;padding:8px 14px;cursor:pointer}
.controls button:focus-visible{outline:2px solid var(--focus);outline-offset:3px}.controls button[aria-pressed=true]{color:var(--focus);border-color:var(--focus)}
#status{font-size:14px;color:var(--dim);margin-left:6px;font-variant-numeric:tabular-nums}
#progress{flex:1;min-width:80px;height:3px;background:var(--line);border-radius:2px;overflow:hidden}
#progress i{display:block;height:100%;width:0;background:var(--focus);transition:width .6s}
.source{font-size:12px;color:var(--dim)}
@media(prefers-reduced-motion:reduce){#eraser-scene,[data-mdp-id],#progress i{transition:none!important}}
</style>`;
}

// The camera, in the page: it reads every box from the DOM, so it needs no coordinates from Python.
const camera = `
const frame=document.getElementById('frame'),el=document.getElementById('eraser-scene');
const W=parseFloat(el.style.width)||scene.width,H=parseFloat(el.style.height)||scene.height;
let cam={x:0,y:0,s:1},active=-1,shot=null,move=0,timer=null;const n=walk.steps.length,PAD=60,MAXZOOM=1.6,DWELL=5200;
function apply(ms){el.style.transition=ms?'transform '+ms+'ms cubic-bezier(.65,0,.35,1)':'none';el.style.transform='translate('+cam.x+'px,'+cam.y+'px) scale('+cam.s+')'}
// The caption takes the bottom of the frame, so a shot is framed in what is left above it.
function camFor(b,zoom){const c=document.getElementById('caption'),fw=frame.clientWidth,fh=frame.clientHeight-c.offsetHeight-28;
  const s=Math.min(fw/(b.w+2*PAD),fh/(b.h+2*PAD),zoom);return{s,x:fw/2-(b.x+b.w/2)*s,y:fh/2-(b.y+b.h/2)*s}}
const union=(a,b)=>{const x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);return{x,y,w:Math.max(a.x+a.w,b.x+b.w)-x,h:Math.max(a.y+a.h,b.y+b.h)-y}};
// A cut between distant shots pulls back to frame both, then flies in, as a map's fly-to does.
function frameBox(b,glide,zoom){const id=++move,sx=(b.x+b.w/2)*cam.s+cam.x-frame.clientWidth/2,sy=(b.y+b.h/2)*cam.s+cam.y-frame.clientHeight/2,
  far=glide&&shot&&zoom<Infinity&&Math.hypot(sx,sy)>0.6*Math.min(frame.clientWidth,frame.clientHeight);
  const from=shot;shot=b;if(!glide){cam=camFor(b,zoom);return apply(0)}
  if(!far){cam=camFor(b,zoom);return apply(1100)}
  cam=camFor(union(from,b),zoom);apply(650);setTimeout(()=>{if(id!==move)return;cam=camFor(b,zoom);apply(950)},620)}
function sceneRect(r){const o=el.getBoundingClientRect(),k=o.width/W;return{x:(r.left-o.left)/k,y:(r.top-o.top)/k,w:r.width/k,h:r.height/k}}
function boundsOf(nodes){let b=null;for(const e of nodes){const rects=[...e.querySelectorAll('.er-shape,path,.er-rel__label')]
  .filter(x=>!x.closest('defs')).map(x=>x.getBoundingClientRect()).filter(r=>r.width+r.height>0);if(!e.querySelector('.er-shape')&&!rects.length)rects.push(e.getBoundingClientRect());
  for(const r of rects){const s=sceneRect(r);b=b?{x:Math.min(b.x,s.x),y:Math.min(b.y,s.y),w:Math.max(b.x+b.w,s.x+s.w)-Math.min(b.x,s.x),h:Math.max(b.y+b.h,s.y+s.h)-Math.min(b.y,s.y)}:s}}return b}
function show(i,glide=true){active=i;const step=walk.steps[i],on=[];document.querySelectorAll('[data-mdp-id]').forEach(e=>{const id=e.dataset.mdpId,rel=e.dataset.mdpTag==='Relationship',group=e.dataset.mdpTag==='Group';
  const hit=i>=0&&(rel?id===step.edge:step.nodes.includes(id));if(hit)on.push(e);e.classList.toggle('muted-node',i>=0&&!hit&&!group);e.classList.toggle('active-node',hit&&!rel);e.classList.toggle('active-edge',hit&&rel)});
  const c=document.getElementById('caption');c.textContent=i<0?walk.lead:step.caption;
  frameBox(i<0||!on.length?{x:0,y:0,w:W,h:H}:boundsOf(on),glide,i<0?Infinity:MAXZOOM);
  document.getElementById('status').textContent=i<0?'Overview · '+n+' steps':(i+1)+' / '+n;document.querySelector('#progress i').style.width=(i<0?0:(i+1)/n*100)+'%';
  document.getElementById('overview').setAttribute('aria-pressed',i<0);try{history.replaceState(null,'',i<0?'#':'#step-'+(i+1))}catch(e){}}
const playBtn=document.getElementById('play');
function play(on){clearInterval(timer);timer=on?setInterval(()=>{if(active>=n-1){play(false);show(-1)}else show(active+1)},DWELL):null;playBtn.setAttribute('aria-pressed',!!on);playBtn.textContent=on?'❚❚ Pause':'▶ Play';if(on&&active<0)show(0)}
const next=()=>show((active+1)%n),prev=()=>show(active<=0?n-1:active-1),stop=f=>()=>{play(false);f()};
document.getElementById('next').onclick=stop(next);document.getElementById('previous').onclick=stop(prev);document.getElementById('overview').onclick=stop(()=>show(-1));playBtn.onclick=()=>play(!timer);
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){stop(next)()}if(e.key==='ArrowLeft')stop(prev)();if(e.key==='Escape')stop(()=>show(-1))();if(e.key===' '||e.key==='p'){e.preventDefault();play(!timer)}});
let drag=null;frame.addEventListener('pointerdown',e=>{play(false);drag={x:e.clientX-cam.x,y:e.clientY-cam.y};frame.classList.add('dragging');frame.setPointerCapture(e.pointerId)});
frame.addEventListener('pointermove',e=>{if(!drag)return;cam.x=e.clientX-drag.x;cam.y=e.clientY-drag.y;apply(false)});
frame.addEventListener('pointerup',()=>{drag=null;frame.classList.remove('dragging')});
frame.addEventListener('wheel',e=>{e.preventDefault();const r=frame.getBoundingClientRect(),px=e.clientX-r.left,py=e.clientY-r.top,k=Math.exp(-e.deltaY*.0015);
  const s=Math.min(4,Math.max(.1,cam.s*k));cam.x=px-(px-cam.x)*s/cam.s;cam.y=py-(py-cam.y)*s/cam.s;cam.s=s;apply(false)},{passive:false});
addEventListener('resize',()=>show(active,false));
const start=(location.hash.match(/step-(\\d+)/)||[])[1];show(start&&start<=n?start-1:-1,false);`;

export function page(html, scene, walk, theme) {
  const nativeBody = html.match(/<body[^>]*>([\s\S]*)<\/body>/)[1];
  const body = `<body><main>
<header><p class="eyebrow">${esc(walk.eyebrow)}</p><h1>${esc(walk.title)}</h1></header>
<div id="frame" aria-label="Diagram: drag to pan, scroll to zoom">${nativeBody}<p id="caption" aria-live="polite"></p></div>
<nav class="controls" aria-label="Walkthrough"><button id="overview" aria-pressed="true">Overview</button><button id="previous">← Previous</button><button id="next">Next →</button><button id="play" aria-pressed="false">▶ Play</button>
<span id="status"></span><span id="progress"><i></i></span><span class="source">Generated from ${esc(walk.source)}; nothing placed by hand.</span></nav>
</main><script>const scene=${JSON.stringify(scene)},walk=${JSON.stringify(walk)};${camera}</script></body>`;
  return html.replace('</head>', css(theme) + '</head>').replace(/<body[^>]*>[\s\S]*<\/body>/, body)
    .replace(/<title>[\s\S]*?<\/title>/, `<title>${esc(walk.title)}</title>`);
}
