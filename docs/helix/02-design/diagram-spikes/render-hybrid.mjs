import {readFile,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const modules=process.env.SPIKE_NODE_MODULES||resolve(here,'node_modules');
const {createRenderer,eraserFonts}=await import(pathToFileURL(resolve(modules,'@eraserlabs/diagrams/dist/index.js')));
const fonts=eraserFonts();fonts.faces=fonts.faces.map(f=>({...f,inline:true}));
const renderer=await createRenderer({chromiumPath:process.env.CHROMIUM_PATH,fonts,deviceScaleFactor:2});
try{
 const diagram=JSON.parse(await readFile(resolve(here,'06-hybrid.json'),'utf8'));
 const result=await renderer.render({...diagram,outputs:{html:true,json:true}});
 if(!result.ok)throw Error(JSON.stringify(result.errors));
 await writeFile(resolve(here,'06-hybrid-measured.json'),JSON.stringify(result.json,null,2));
 await writeFile(resolve(here,'06-hybrid-result.json'),JSON.stringify({ok:result.ok,warnings:result.warnings},null,2));
 const scene=result.json.scene;
 let document=result.html;
 const nativeBody=document.match(/<body[^>]*>([\s\S]*)<\/body>/)[1];
 const css=`<style>
 :root{--bg:#0d1520;--surface:#132031;--text:#e3ecf5;--dim:#a4b7cb;--accent:#ffb547;--er-ground:#0d1520}
 html,body{margin:0;background:var(--bg)!important;color:var(--text);font-family:Inter,sans-serif}
 main{max-width:1440px;margin:0 auto;padding:36px 48px 24px}h1{font-size:42px;line-height:1.15;letter-spacing:-1.2px;margin:12px 0 14px;font-weight:650}.eyebrow{color:var(--dim);font-size:14px;letter-spacing:2px;margin:0}.explanation{font-size:21px;color:var(--dim);margin:0;min-height:62px;line-height:1.4}
 #frame{position:relative;background-image:radial-gradient(#34455c .65px,transparent .65px);background-size:24px 24px;margin:12px 0 24px;overflow:hidden}
 #eraser-scene{transform-origin:0 0;--er-ground:#0d1520;background:transparent!important}
 [data-mdp-id]{transition:opacity .18s}.muted-node{opacity:.18}.active-node .er-shape{--er-border:#ffb547!important}.active-edge .er-rel{--er-stroke:#ffb547!important;--er-label-ink:#ffb547!important}.active-edge .er-rel__label{color:#ffb547!important}.active-edge .er-rel__line{stroke-width:2.5px}
 .controls{display:flex;gap:10px;align-items:center;border-top:1px solid #34455c;padding-top:18px;flex-wrap:wrap}.controls button{font:inherit;font-size:16px;background:var(--surface);color:var(--text);border:1px solid #596b87;border-radius:4px;padding:10px 16px;cursor:pointer}.controls button:focus-visible{outline:2px solid var(--accent);outline-offset:3px}.controls button[aria-pressed=true]{color:var(--accent);border-color:var(--accent)}#status{font-size:16px;color:var(--dim);margin:0 0 0 12px}footer{font-size:14px;color:var(--dim);line-height:1.5;margin-top:18px;max-width:980px}a{color:#a9cfff}
 @media(prefers-reduced-motion:reduce){[data-mdp-id]{transition:none}}@media(max-width:800px){main{padding:24px 20px}h1{font-size:30px}.explanation{font-size:18px}#frame{overflow-x:auto}#status{margin:0}.controls{gap:8px}}
 </style>`;
 document=document.replace('</head>',css+'</head>');
 const captions=['The software team asks through an agent runtime.','The runtime loads the HELIX routing skill.','The artifact catalog guides the skill.','The project marker bounds the skill’s scope.','The skill authors and reconciles project documents.','The documents govern the runtime’s authorized execution.'];
 const pairs=[['team','runtime'],['runtime','skill'],['catalog','skill'],['scope','skill'],['skill','docs'],['docs','runtime']];
 const script=`<script>
 const scene=${JSON.stringify(scene)},captions=${JSON.stringify(captions)},pairs=${JSON.stringify(pairs)},edges=['asks','loads','guides','bounds','authors','governs'];let active=-1;
 function fit(){const frame=document.getElementById('frame');const width=Math.max(800,frame.clientWidth);const scale=width/scene.width;document.getElementById('eraser-scene').style.transform='scale('+scale+')';frame.style.height=(scene.height*scale)+'px'}
 function show(index){active=index;document.querySelectorAll('[data-mdp-id]').forEach(e=>{const id=e.dataset.mdpId,relationship=e.dataset.mdpTag==='Relationship';const selected=index>=0&&(relationship?id===edges[index]:pairs[index].includes(id));e.classList.toggle('muted-node',index>=0&&!selected&&id!=='helix');e.classList.toggle('active-node',selected&&!relationship);e.classList.toggle('active-edge',selected&&relationship)});document.getElementById('explanation').textContent=index<0?'Follow how team intent becomes governing project documents.':captions[index];document.getElementById('status').textContent=index<0?'Overview · all six relationships':(index+1)+' / 6';document.getElementById('overview').setAttribute('aria-pressed',index<0)}
 document.getElementById('next').onclick=()=>show((active+1)%6);document.getElementById('previous').onclick=()=>show(active<=0?5:active-1);document.getElementById('overview').onclick=()=>show(-1);document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')show((active+1)%6);if(e.key==='ArrowLeft')show(active<=0?5:active-1)});window.addEventListener('resize',fit);document.fonts.ready.then(fit);fit();show(-1);
 </script>`;
 const body=`<body><main><header><p class="eyebrow">HELIX / INTEGRATION SPIKE</p><h1>HELIX gives the runtime a document discipline.</h1><p class="explanation" id="explanation" aria-live="polite"></p></header><div id="frame" role="img" aria-label="HELIX architecture: six entities and six relationships. Eraser-generated components and routes.">${nativeBody}</div><div class="controls" aria-label="Architecture walkthrough"><button id="overview" aria-pressed="true">Overview</button><button id="previous">← Previous</button><button id="next">Next →</button><p id="status" aria-live="polite"></p></div><footer>Solid arrows show actions or information; dashed arrows show guidance or constraints. The HELIX boundary contains the catalog and routing skill. Positions are authored; Eraser owns measurement and routing. <a href="06-hybrid.json">Editable source</a> · <a href="06-hybrid-measured.json">Measured geometry</a></footer></main>${script}</body>`;
 document=document.replace(/<body[^>]*>[\s\S]*<\/body>/,body).replace(/<title>[\s\S]*?<\/title>/,'<title>HELIX · integrated diagram spike</title>');
 await writeFile(resolve(here,'06-hybrid.html'),document);
 console.log('Hybrid rendered',JSON.stringify({scene,warnings:result.warnings}));
}finally{await renderer.close()}
