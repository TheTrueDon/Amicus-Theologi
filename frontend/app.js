"use strict";
const $=x=>document.querySelector(x), $$=x=>document.querySelectorAll(x);
let settings={},saving=Promise.resolve(),modules=[],view=null,activeVerse=1,books=[],searchState={offset:0,total:0,limit:50};
async function api(path,opts={}){const r=await fetch(path,opts);if(!r.ok){let j;try{j=await r.json()}catch{};throw new Error(typeof j?.detail==='string'?j.detail:`HTTP ${r.status}`)}return r.json()}
function save(p){Object.assign(settings,p);saving=saving.then(()=>api('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)})).catch(e=>message(e.message))}
function message(text){$('#error-msg').textContent=text;$('#error-msg').hidden=!text}
function show(id){$(id).showModal()}
function apply(){document.body.dataset.theme=settings.theme;document.body.style.setProperty('--verse-font',settings.font_size+'px');$('.search-panel').style.width=settings.search_width+'%';$('.analysis-panel').style.width=settings.analysis_width+'%';$('#theme').value=settings.theme;$('#font-size').value=settings.font_size;$('#font-output').textContent=settings.font_size+' px';for(const l of ['greek','german','latin'])$('#show-'+l).checked=settings['show_'+l];filterLanguages()}
function isShown(l){return l==='grc'?settings.show_greek:l==='de'?settings.show_german:l==='la'?settings.show_latin:true}
function filterLanguages(){for(const article of $$('.translation'))article.hidden=!isShown(article.dataset.language)}
function el(tag,cls,text){let node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node}
function selectVerse(v){activeVerse=v;for(const row of $$('.verse-line'))row.classList.toggle('active',Number(row.dataset.verse)===v);$('#current-ref').textContent=`${view.book} ${view.chapter},${v}`;$('#reference').value=`${view.book} ${view.chapter},${v}`;save({active_reference:`${view.book} ${view.chapter},${v}`})}
function render(){message('');const out=$('#translations');out.replaceChildren();$('#current-ref').textContent=`${view.book} ${view.chapter},${activeVerse}`;$('#reference').value=`${view.book} ${view.chapter},${activeVerse}`;$('#book-choice').value=view.book;$('#chapter-choice').value=view.chapter;$('#chapter-title').textContent=`${view.book_name} · Kapitel ${view.chapter}`;$('#chapter-badge').textContent=String(view.chapter).padStart(2,'0');$('#chapter-subtitle').textContent='Mehrere Ausgaben · annotierte Wörter anklickbar';$('#prev').disabled=!view.previous;$('#next').disabled=!view.next;$('#verse-foot').textContent=view.available_verses.length+' vorhandene Versnummern';$('#text-notice').hidden=!!view.modules.length;if(view.modules.length===0)$('#text-notice').innerHTML='<b>Für dieses Kapitel sind keine Texte installiert.</b><br>Installiere ein Modul oder rufe ein Kapitel auf, das ein bestehendes Modul enthält.';
for(const mod of view.modules){const box=el('article','translation');box.dataset.language=mod.language;const head=el('div','translation-head'),title=el('span','',mod.title.toUpperCase()),tag=el('span','tag',mod.language+' · '+mod.id);head.append(title,tag);box.append(head);for(const v of mod.verses){let line=el('p','verse-line');line.dataset.verse=v.verse;line.lang=mod.language;if(mod.language==='he')line.dir='rtl';line.append(el('sup','',String(v.verse)));const words=(view.tokens||[]).filter(t=>t.module_id===mod.id&&t.verse===v.verse);if(words.length){for(const word of words){const btn=el('button','morph-word',word.surface);btn.type='button';btn.title='Wortanalyse: '+word.lemma;btn.onclick=(event)=>{event.stopPropagation();selectVerse(v.verse);showWord(word,mod)};line.append(btn,document.createTextNode(' '))}}else{line.append(document.createTextNode(v.text));if(['grc','he'].includes(mod.language)){const hint=el('span','annotation-warning','  ·  Keine Wortannotation importiert');hint.dir='ltr';hint.title='Textmodule öffnen und die passende *_morph.tsv-Datei für diese Ausgabe importieren';line.append(hint);line.classList.add('unannotated')}}line.onclick=()=>selectVerse(v.verse);box.append(line)}box.append(el('small','',`Quelle: ${mod.provenance} · Lizenz: ${mod.license}`));out.append(box)}filterLanguages();for(const row of $$('.verse-line'))row.classList.toggle('active',Number(row.dataset.verse)===activeVerse);
const first=out.querySelector(`.verse-line[data-verse="${activeVerse}"]`);if(first)first.scrollIntoView({block:'nearest'});
}
async function go(b,c,v=1){try{const data=await api(`/api/chapter?book=${encodeURIComponent(b)}&chapter=${c}`);view=data;activeVerse=v;render();save({active_reference:`${b} ${c},${v}`})}catch(e){message(e.message)}}
async function navigate(){try{const r=await api('/api/reference?q='+encodeURIComponent($('#reference').value));await go(r.book,r.chapter,r.verse)}catch(e){message(e.message)}}
function moduleText(m){let row=el('div','module-entry');row.append(el('b','',m.title),el('small','',`${m.language} · ${m.verse_count} Verse · ${m.license}`));return row}
async function refreshModules(){modules=await api('/api/modules');refreshSearchFilters();$('#module-counter').textContent=modules.length+' Module';const morphSel=$('#morph-module');const before=morphSel.value;morphSel.replaceChildren();for(const mod of modules.filter(x=>['grc','he'].includes(x.language))){const opt=el('option','',mod.title+' ('+mod.id+')');opt.value=mod.id;morphSel.append(opt)}if([...morphSel.options].some(x=>x.value===before))morphSel.value=before;for(const id of ['#module-summary','#module-list','#manage-list'])$(id).replaceChildren();if(!modules.length){for(const id of ['#module-summary','#module-list','#manage-list'])$(id).append(el('p','hint','Noch keine Module installiert.'))}for(const m of modules){$('#module-summary').append(moduleText(m));$('#module-list').append(moduleText(m));let row=el('div','manage-row'),detail=el('div');detail.append(el('b','',m.title),el('small','',`${m.id} · ${m.verse_count} Verse · ${m.license}`));const btn=el('button','btn','Entfernen');btn.type='button';btn.onclick=async()=>{if(!confirm(`Modul „${m.title}“ und alle zugehörigen Verse löschen?`))return;try{await api('/api/modules/'+encodeURIComponent(m.id),{method:'DELETE'});await refreshModules();await go(view.book,view.chapter,activeVerse)}catch(e){alert(e.message)}};row.append(detail,btn);$('#manage-list').append(row)}}
async function start(){try{settings=await api('/api/settings');books=await api('/api/books');for(const b of books){const sb=el('option','',b.name);sb.value=b.id;$('#search-book').append(sb);const o=el('option','',b.name);o.value=b.id;$('#book-choice').append(o)}apply();await refreshModules();try{const r=await api('/api/reference?q='+encodeURIComponent(settings.active_reference));await go(r.book,r.chapter,r.verse)}catch{await go('Joh',1,1)}}catch(e){message('Lokaler Start fehlgeschlagen: '+e.message)}}
$('#navigate').onclick=navigate;$('#reference').onkeydown=e=>{if(e.key==='Enter')navigate()};$('#book-choice').onchange=e=>go(e.target.value,1,1);$('#chapter-choice').onchange=e=>go($('#book-choice').value,Number(e.target.value),1);$('#prev').onclick=()=>view?.previous&&go(...view.previous,1);$('#next').onclick=()=>view?.next&&go(...view.next,1);
$('#settings-btn').onclick=()=>show('#settings-dialog');$('#help-btn').onclick=()=>show('#help-dialog');$('#module-btn').onclick=()=>show('#module-dialog');$('#add-module-left').onclick=()=>show('#module-dialog');$('#modules-close').onclick=()=>$('#module-dialog').close();$('#reset').onclick=()=>{save({search_width:25,analysis_width:27});apply()};$('#theme').onchange=e=>{save({theme:e.target.value});apply()};$('#font-size').oninput=e=>{save({font_size:Number(e.target.value)});apply()};for(const l of ['greek','german','latin'])$('#show-'+l).onchange=e=>{save({['show_'+l]:e.target.checked});apply()};$('#larger').onclick=()=>{save({font_size:Math.min(28,settings.font_size+1)});apply()};$('#smaller').onclick=()=>{save({font_size:Math.max(12,settings.font_size-1)});apply()};
// Bei Auswahl einer Demo-Datei alle Importfelder passend vorbelegen.
// Für andere Dateien nur ID/Titel vorschlagen; Lizenz und Herkunft bleiben Nutzereingaben.
$('#import-form').elements.namedItem('file').addEventListener('change',e=>{
  const file=e.target.files?.[0];if(!file)return;
  const form=$('#import-form'),name=file.name.replace(/\.(csv|tsv|txt)$/i,'');
  const fill=(field,value)=>{const input=form.elements.namedItem(field);if(input)input.value=value};
  const id=name.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-zA-Z0-9_-]+/g,'-').replace(/^-+|-+$/g,'').slice(0,48);
  fill('module_id',id.length>=2?id:'modul');
  fill('title',name.replace(/[_-]+/g,' '));
  const demo={
    johannes_demo_de:{id:'joh-demo-de',title:'Luther 1912 – Johannes 1,1–5 (Demonstration)',language:'de',license:'Public Domain (historische Vorlage; bitte prüfen)',source:'Kurzer Demonstrationsauszug nach Luther 1912'},
    johannes_demo_la:{id:'joh-demo-la',title:'Vulgata – Johannes 1,1–5 (Demonstration)',language:'la',license:'Public Domain (historische Vorlage; bitte prüfen)',source:'Kurzer Demonstrationsauszug aus lateinischer Vulgata'},
    johannes_1_1_grc:{id:'grc-joh-demo',title:'Griechisch – Johannes 1,1 (Demo)',language:'grc',license:'Antiker Text – Nutzungsrechte der Transkription prüfen',source:'Demonstration: Johannes 1,1, griechischer Text'},
    genesis_1_1_he:{id:'he-gen-demo',title:'Hebräisch – Genesis 1,1 (Demo)',language:'he',license:'Antiker Text – Nutzungsrechte der Transkription prüfen',source:'Demonstration: Genesis 1,1, hebräischer Text'}
  }[name.toLowerCase()];
  if(demo){fill('module_id',demo.id);fill('title',demo.title);fill('language',demo.language);fill('license_name',demo.license);fill('provenance',demo.source)}
  else{fill('license_name','');fill('provenance','');}
  $('#import-status').textContent=demo?'Demo-Modul erkannt: Angaben wurden automatisch ausgefüllt. Bitte prüfen und importieren.':'Modul-ID und Titel vorgeschlagen. Bitte Lizenz und Herkunft ergänzen.';
});
$('#import-form').onsubmit=async e=>{e.preventDefault();const form=e.target,status=$('#import-status'),btn=form.querySelector('button[type=submit]');btn.disabled=true;status.textContent='Import wird geprüft…';try{const response=await api('/api/modules/import',{method:'POST',body:new FormData(form)});status.textContent=`Import erfolgreich: ${response.verses} Verse.`;form.reset();await refreshModules();await go(view.book,view.chapter,activeVerse)}catch(err){status.textContent='Fehler: '+err.message}finally{btn.disabled=false}};
for(const splitter of $$('.splitter'))splitter.addEventListener('pointerdown',e=>{if(innerWidth<850)return;splitter.setPointerCapture(e.pointerId);const box=$('#panels');function move(ev){const b=box.getBoundingClientRect(),pct=(ev.clientX-b.left)/b.width*100;if(splitter.dataset.resize==='left')settings.search_width=Math.max(17,Math.min(40,pct));else settings.analysis_width=Math.max(17,Math.min(40,100-pct));if(settings.search_width+settings.analysis_width>75)return;apply()}function end(){splitter.removeEventListener('pointermove',move);splitter.removeEventListener('pointerup',end);save({search_width:Math.round(settings.search_width),analysis_width:Math.round(settings.analysis_width)})}splitter.addEventListener('pointermove',move);splitter.addEventListener('pointerup',end)});

function refreshSearchFilters(){
 const select=$('#search-module'); const old=select.value;select.replaceChildren(el('option','','Alle Module'));select.firstChild.value='';
 for(const mod of modules){const o=el('option','',mod.title);o.value=mod.id;select.append(o)}
 if([...select.options].some(o=>o.value===old))select.value=old;
}
async function runSearch(offset=0){
 const term=$('#search').value.trim();if(!term){$('#search-error').hidden=true;$('#search-results').replaceChildren(el('p','hint','Bitte einen Suchausdruck eingeben.'));return}
 const params=new URLSearchParams({q:term,mode:$('#search-mode').value,limit:'50',offset:String(offset)});
 if($('#search-module').value)params.set('module_id',$('#search-module').value);
 if($('#search-book').value)params.set('book',$('#search-book').value);
 const button=$('#search-btn');button.disabled=true;$('#search-error').hidden=true;
 try{const result=await api('/api/search?'+params);searchState=result;const list=$('#search-results');list.replaceChildren();
  $('#search-total').textContent=result.total+' Treffer';
  if(!result.results.length)list.append(el('p','hint',result.total?'Keine weiteren Treffer.':'Keine Treffer für diesen Suchausdruck.'));
  for(const hit of result.results){const btn=el('button','search-hit');btn.type='button';
   btn.append(el('strong','',`${hit.book} ${hit.chapter},${hit.verse}`),el('small','',`${hit.module_title} · ${hit.language}`),el('span','hit-text',hit.text));
   btn.addEventListener('click',()=>go(hit.book,hit.chapter,hit.verse));list.append(btn)}
  $('#search-prev').hidden=offset===0;$('#search-next').hidden=offset+result.results.length>=result.total;
  $('#search-page').textContent=result.total?`${offset+1}–${offset+result.results.length} / ${result.total}`:'';
 }catch(e){$('#search-error').textContent=e.message;$('#search-error').hidden=false}
 finally{button.disabled=false}
}
$('#search-btn').addEventListener('click',()=>runSearch(0));
$('#search').addEventListener('keydown',e=>{if(e.key==='Enter')runSearch(0)});
$('#search-prev').addEventListener('click',()=>runSearch(Math.max(0,searchState.offset-50)));
$('#search-next').addEventListener('click',()=>runSearch(searchState.offset+50));
for(const id of ['#search-mode','#search-module','#search-book'])$(id).addEventListener('change',()=>{if($('#search').value.trim())runSearch(0)});

async function showWord(word,mod){
 const box=$('#word-analysis');box.replaceChildren();box.append(el('h3','',word.surface));
 for(const [key,value] of [['Lemma',word.lemma],['Morphologie',word.morph],['Strong',word.strong||'Nicht angegeben'],['Edition',mod.title],['Quelle',mod.provenance]]){
 const row=el('p','analysis-field');row.append(el('b','',key+': '),document.createTextNode(value));box.append(row)}
 const btn=el('button','btn primary','Alle Vorkommen dieses Lemmas');box.append(btn);
 btn.onclick=async()=>{try{const data=await api('/api/morphology/lemma?module_id='+encodeURIComponent(mod.id)+'&lemma='+encodeURIComponent(word.lemma));const target=$('#lemma-results');target.replaceChildren(el('p','hint',data.results.length+' Treffer im annotierten Bestand'));for(const hit of data.results){const row=el('button','lemma-hit',`${hit.book} ${hit.chapter},${hit.verse} · ${hit.surface} · ${hit.morph}`);row.onclick=()=>go(hit.book,hit.chapter,hit.verse);target.append(row)}}catch(e){message(e.message)}};
}
$('#morph-import-form').onsubmit=async e=>{e.preventDefault();const form=e.target,status=$('#morph-import-status');status.textContent='Wortdatei wird geprüft…';try{const result=await api('/api/morphology/import',{method:'POST',body:new FormData(form)});status.textContent=`Erfolgreich: ${result.tokens} Wörter in ${result.annotated_verses} Versen. Die markierten Wörter sind jetzt anklickbar.`;await go(view.book,view.chapter,activeVerse)}catch(err){status.textContent='Fehler: '+err.message}};
start();
