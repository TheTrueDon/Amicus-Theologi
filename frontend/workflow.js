/* Amicus Theologi 0.9: keyboard-oriented workflows. Runs entirely in the browser. */
(()=>{
'use strict';
const q=s=>document.querySelector(s);
const STORAGE='amicus-workflow-recent-v1';
let history=[], cursor=-1, navigatingHistory=false, filtered=[], activeItem=0;
const keyOf=r=>`${r.book} ${r.chapter},${r.verse}`;
function loadRecent(){try{const v=JSON.parse(localStorage.getItem(STORAGE)||'[]');return Array.isArray(v)?v.filter(x=>x&&typeof x.ref==='string'&&x.ref.length<70).slice(0,16):[]}catch{return []}}
let recent=loadRecent();
function storeRecent(){try{localStorage.setItem(STORAGE,JSON.stringify(recent.slice(0,16)))}catch{}}
// app.js defines global lexical `view` and `activeVerse`; use those directly rather than window properties.
function recordCurrent(){if(typeof view==='undefined'||!view)return;const ref=keyOf({book:view.book,chapter:view.chapter,verse:activeVerse});if(!navigatingHistory&&history[cursor]!==ref){history=history.slice(0,cursor+1);history.push(ref);if(history.length>80)history.shift();cursor=history.length-1}recent=[{ref,at:Date.now()},...recent.filter(x=>x.ref!==ref)].slice(0,16);storeRecent();refreshHistoryButtons()}
async function gotoRef(ref){try{const parsed=await api('/api/reference?q='+encodeURIComponent(ref));await go(parsed.book,parsed.chapter,parsed.verse)}catch(e){message(e.message)}}
async function moveHistory(delta){const target=cursor+delta;if(target<0||target>=history.length)return;const last=cursor;cursor=target;navigatingHistory=true;try{await gotoRef(history[target])}finally{navigatingHistory=false;if(typeof view==='undefined'||!view||keyOf({book:view.book,chapter:view.chapter,verse:activeVerse})!==history[target])cursor=last;refreshHistoryButtons()}}
function refreshHistoryButtons(){const back=q('#history-back'),next=q('#history-forward');if(back)back.disabled=cursor<=0;if(next)next.disabled=cursor>=history.length-1;renderRecent()}
function renderRecent(){const root=q('#recent-references');if(!root)return;root.replaceChildren();for(const item of recent.slice(0,7)){const b=document.createElement('button');b.className='workflow-recent';b.type='button';b.textContent=item.ref;b.title='Bibelstelle aufrufen';b.onclick=()=>gotoRef(item.ref);root.append(b)}if(!recent.length){const p=document.createElement('span');p.className='hint';p.textContent='Noch keine Bibelstellen besucht.';root.append(p)}}
const originalGo=go;
go=async (...args)=>{await originalGo(...args);if(view&&view.book===args[0]&&view.chapter===args[1])recordCurrent()};
const originalSelectVerse=selectVerse;
selectVerse=(v)=>{originalSelectVerse(v);recordCurrent()};
function isTyping(element){return !!element?.closest('input,textarea,select,[contenteditable="true"]')}
function openDialog(id){const d=q(id);if(d&&!d.open)d.showModal()}
function run(id){switch(id){
case 'reference':q('#reference').focus();q('#reference').select();break;
case 'search':q('#search').focus();q('#search').select();break;
case 'advanced':q('#advanced-box').open=true;q('#adv-lemma').focus();break;
case 'back':moveHistory(-1);break;
case 'forward':moveHistory(1);break;
case 'previous':q('#prev').click();break;
case 'next':q('#next').click();break;
case 'modules':q('#module-btn').click();break;
case 'projects':q('#projects-btn').click();break;
case 'textcrit':q('#textcrit-btn').click();break;
case 'settings':q('#settings-btn').click();break;
case 'help':q('#help-btn').click();break;
case 'zoom-in':q('#larger').click();break;
case 'zoom-out':q('#smaller').click();break;
case 'search-panel':q('#search').focus();break;
case 'text-panel':q('#verse-scroll').focus();break;
case 'analysis-panel':q('#word-analysis').focus();break;
}}
const commands=[
 ['reference','Bibelstelle aufrufen','Alt + R'],['search','Volltextsuche','/'],['advanced','Erweiterte Suche','Alt + S'],
 ['back','Besuchte Bibelstelle zurück','Alt + ←'],['forward','Besuchte Bibelstelle vor','Alt + →'],
 ['previous','Vorheriges Kapitel','Alt + ↑'],['next','Nächstes Kapitel','Alt + ↓'],
 ['modules','Textmodule / Bibliothek öffnen',''],['projects','Studienprojekte öffnen','Ctrl + Shift + P'],
 ['textcrit','Textkritik und Synopse öffnen',''],['settings','Einstellungen öffnen',''],
 ['help','Hilfe und Tastenkombinationen','F1'],['zoom-in','Schrift vergrößern',''],['zoom-out','Schrift verkleinern',''],
 ['search-panel','Zum Suchbereich wechseln','Alt + 1'],['text-panel','Zum Bibeltext wechseln','Alt + 2'],['analysis-panel','Zum Analysebereich wechseln','Alt + 3']
];
const dlg=q('#command-dialog'),inp=q('#command-filter'),results=q('#command-results');
function openPalette(){if(!dlg.open)dlg.showModal();inp.value='';updatePalette();inp.focus()}
function closePalette(){if(dlg.open)dlg.close()}
function updatePalette(){const needle=inp.value.trim().toLocaleLowerCase('de');filtered=commands.filter(x=>x[1].toLocaleLowerCase('de').includes(needle));if(!needle){for(const item of recent.slice(0,5))filtered.push(['go:'+item.ref,'Zu '+item.ref+' springen','Verlauf'])}activeItem=0;drawPalette()}
function drawPalette(){results.replaceChildren();for(const [idx,entry] of filtered.entries()){const b=document.createElement('button');b.type='button';b.className='command-item'+(idx===activeItem?' selected':'');b.setAttribute('role','option');b.setAttribute('aria-selected',idx===activeItem?'true':'false');const label=document.createElement('span');label.textContent=entry[1];const shortcut=document.createElement('kbd');shortcut.textContent=entry[2];b.append(label,shortcut);b.onclick=()=>execute(entry[0]);results.append(b)}if(!filtered.length){const hint=document.createElement('p');hint.className='hint';hint.textContent='Kein passender Befehl.';results.append(hint)}}
function execute(id){closePalette();if(id.startsWith('go:'))gotoRef(id.slice(3));else run(id)}
q('#palette-button').onclick=openPalette;q('#command-close').onclick=closePalette;
q('#history-back').onclick=()=>moveHistory(-1);q('#history-forward').onclick=()=>moveHistory(1);
inp.addEventListener('input',updatePalette);
inp.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();activeItem=Math.min(filtered.length-1,activeItem+1);drawPalette()}else if(e.key==='ArrowUp'){e.preventDefault();activeItem=Math.max(0,activeItem-1);drawPalette()}else if(e.key==='Enter'){e.preventDefault();if(filtered[activeItem])execute(filtered[activeItem][0])}});
document.addEventListener('keydown',e=>{
 if(e.defaultPrevented||e.isComposing)return;
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openPalette();return}
 if(e.key==='F1'){e.preventDefault();run('help');return}
 if(dlg.open||document.querySelector('dialog[open]'))return;
 if((e.ctrlKey||e.metaKey)&&e.shiftKey&&e.key.toLowerCase()==='p'){e.preventDefault();run('projects');return}
 if(e.altKey&&!e.ctrlKey&&!e.metaKey){const map={r:'reference',s:'advanced','1':'search-panel','2':'text-panel','3':'analysis-panel','ArrowLeft':'back','ArrowRight':'forward','ArrowUp':'previous','ArrowDown':'next'};const id=map[e.key]||map[e.key.toLowerCase()];if(id){e.preventDefault();run(id)}return}
 if(!e.ctrlKey&&!e.metaKey&&!isTyping(e.target)&&e.key==='/'){e.preventDefault();run('search')}
});
q('#verse-scroll').setAttribute('tabindex','-1');q('#word-analysis').setAttribute('tabindex','-1');
// Track initial application navigation even when it finishes before this listener runs.
setTimeout(()=>{recordCurrent();refreshHistoryButtons()},350);
})();
