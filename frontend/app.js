"use strict";
const $=x=>document.querySelector(x), $$=x=>document.querySelectorAll(x);
let currentProjectId=null,studyHighlights={},allProjects=[];
let settings={},saving=Promise.resolve(),modules=[],view=null,activeVerse=1,books=[],searchState={offset:0,total:0,limit:50},activeSearch='normal';
async function api(path,opts={}){const r=await fetch(path,opts);if(!r.ok){let j;try{j=await r.json()}catch{};throw new Error(typeof j?.detail==='string'?j.detail:`HTTP ${r.status}`)}return r.json()}
function save(p){Object.assign(settings,p);saving=saving.then(()=>api('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)})).catch(e=>message(e.message))}
function message(text){$('#error-msg').textContent=text;$('#error-msg').hidden=!text}
function show(id){$(id).showModal()}
function apply(){document.body.dataset.theme=settings.theme;document.body.style.setProperty('--verse-font',settings.font_size+'px');$('.search-panel').style.width=settings.search_width+'%';$('.analysis-panel').style.width=settings.analysis_width+'%';$('#theme').value=settings.theme;$('#font-size').value=settings.font_size;$('#font-output').textContent=settings.font_size+' px';for(const l of ['greek','german','latin'])$('#show-'+l).checked=settings['show_'+l];filterLanguages()}
function isShown(l){return l==='grc'?settings.show_greek:l==='de'?settings.show_german:l==='la'?settings.show_latin:true}
function filterLanguages(){for(const article of $$('.translation'))article.hidden=!isShown(article.dataset.language)}
function el(tag,cls,text){let node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node}
function selectVerse(v){activeVerse=v;for(const row of $$('.verse-line'))row.classList.toggle('active',Number(row.dataset.verse)===v);$('#current-ref').textContent=`${view.book} ${view.chapter},${v}`;$('#reference').value=`${view.book} ${view.chapter},${v}`;save({active_reference:`${view.book} ${view.chapter},${v}`});refreshStudyPane()}
function render(){message('');const out=$('#translations');out.replaceChildren();$('#current-ref').textContent=`${view.book} ${view.chapter},${activeVerse}`;$('#reference').value=`${view.book} ${view.chapter},${activeVerse}`;$('#book-choice').value=view.book;$('#chapter-choice').value=view.chapter;$('#chapter-title').textContent=`${view.book_name} · Kapitel ${view.chapter}`;$('#chapter-badge').textContent=String(view.chapter).padStart(2,'0');$('#chapter-subtitle').textContent='Mehrere Ausgaben · annotierte Wörter anklickbar';$('#prev').disabled=!view.previous;$('#next').disabled=!view.next;$('#verse-foot').textContent=view.available_verses.length+' vorhandene Versnummern';$('#text-notice').hidden=!!view.modules.length;if(view.modules.length===0)$('#text-notice').innerHTML='<b>Für dieses Kapitel sind keine Texte installiert.</b><br>Installiere ein Modul oder rufe ein Kapitel auf, das ein bestehendes Modul enthält.';
for(const mod of view.modules){const box=el('article','translation');box.dataset.language=mod.language;const head=el('div','translation-head'),title=el('span','',mod.title.toUpperCase()),tag=el('span','tag',mod.language+' · '+mod.id);head.append(title,tag);box.append(head);for(const v of mod.verses){let line=el('p','verse-line');line.dataset.verse=v.verse;line.lang=mod.language;if(mod.language==='he')line.dir='rtl';line.append(el('sup','',String(v.verse)));const words=(view.tokens||[]).filter(t=>t.module_id===mod.id&&t.verse===v.verse);if(words.length){for(const word of words){const btn=el('button','morph-word',word.surface);btn.type='button';btn.title='Wortanalyse: '+word.lemma;btn.onclick=(event)=>{event.stopPropagation();selectVerse(v.verse);showWord(word,mod)};line.append(btn,document.createTextNode(' '))}}else{line.append(document.createTextNode(v.text));if(['grc','he'].includes(mod.language)){const hint=el('span','annotation-warning','  ·  Keine Wortannotation importiert');hint.dir='ltr';hint.title='Textmodule öffnen und die passende *_morph.tsv-Datei für diese Ausgabe importieren';line.append(hint);line.classList.add('unannotated')}}line.onclick=()=>selectVerse(v.verse);box.append(line)}box.append(el('small','',`Quelle: ${mod.provenance} · Lizenz: ${mod.license}`));out.append(box)}filterLanguages();for(const row of $$('.verse-line'))row.classList.toggle('active',Number(row.dataset.verse)===activeVerse);
paintHighlights();refreshStudyPane();
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
 activeSearch='normal';
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
async function runAdvancedSearch(offset=0){
 activeSearch='advanced';
 const params=new URLSearchParams({limit:'50',offset:String(offset),distance:$('#adv-distance').value,order:$('#adv-order').value});
 for(const name of ['lemma','surface','morph','strong','second-lemma','second-surface','second-morph','second-strong']){
 const value=$('#adv-'+name).value.trim();if(value)params.set(name.replace(/-/g,'_'),value);
 }
 if($('#search-module').value)params.set('module_id',$('#search-module').value);
 if($('#search-book').value)params.set('book',$('#search-book').value);
 const button=$('#adv-search-btn');button.disabled=true;$('#search-error').hidden=true;
 try{const result=await api('/api/search/advanced?'+params);searchState=result;
 const list=$('#search-results');list.replaceChildren();$('#search-total').textContent=result.total+' Treffer';
 if(!result.results.length)list.append(el('p','hint','Keine passenden annotierten Verse gefunden. Bitte Module und Morphologie prüfen.'));
 for(const hit of result.results){const btn=el('button','search-hit');btn.type='button';
 btn.append(el('strong','',`${hit.book} ${hit.chapter},${hit.verse}`),el('small','',`${hit.module_title} · ${hit.language}`),el('span','hit-text',hit.text));
 btn.onclick=()=>go(hit.book,hit.chapter,hit.verse);list.append(btn)}
 $('#search-prev').hidden=offset===0;$('#search-next').hidden=offset+result.results.length>=result.total;
 $('#search-page').textContent=result.total?`${offset+1}–${offset+result.results.length} / ${result.total}`:'';
 $('#adv-note').textContent=result.note;
 }catch(e){$('#search-error').textContent=e.message;$('#search-error').hidden=false}
 finally{button.disabled=false}
}
function pageSearch(offset){return activeSearch==='advanced'?runAdvancedSearch(offset):runSearch(offset)}
$('#adv-search-btn').addEventListener('click',()=>runAdvancedSearch(0));
$('#search-btn').addEventListener('click',()=>runSearch(0));
$('#search').addEventListener('keydown',e=>{if(e.key==='Enter')runSearch(0)});
$('#search-prev').addEventListener('click',()=>pageSearch(Math.max(0,searchState.offset-50)));
$('#search-next').addEventListener('click',()=>pageSearch(searchState.offset+50));
for(const id of ['#search-mode','#search-module','#search-book'])$(id).addEventListener('change',()=>{if($('#search').value.trim())runSearch(0)});

async function showWord(word,mod){
 const box=$('#word-analysis');box.replaceChildren();box.append(el('h3','',word.surface));
 for(const [key,value] of [['Lemma',word.lemma],['Edition',mod.title],['Quelle',mod.provenance]]){
 const row=el('p','analysis-field');row.append(el('b','',key+': '),document.createTextNode(value));box.append(row)}
 const grammar=el('section','grammar-box');box.append(grammar);
 try {const info=await api('/api/morphology/decode?'+new URLSearchParams({morph:word.morph||'',language:mod.language}));
  if(info.recognized){grammar.append(el('h4','','Grammatische Analyse'));for(const f of info.features){const r=el('p','analysis-field');r.append(el('b','',f.name+': '),document.createTextNode(f.value));grammar.append(r)}}
  else grammar.append(el('p','hint',info.notice));
 }catch(e){grammar.append(el('p','hint','Grammatik-Code nicht übersetzt: '+e.message))}
 const technical=el('details','technical-codes');technical.append(el('summary','','Originalcodes / technische Angaben'));technical.append(el('p','','Morphologie: '+(word.morph||'–')),el('p','','Strong: '+(word.strong||'–')));box.append(technical);
 const lex=$('#lexicon-results');lex.replaceChildren(el('p','hint','Lexika werden abgefragt …'));
 try{
  const params=new URLSearchParams({language:mod.language,lemma:word.lemma});if(word.strong)params.set('strong',word.strong);
  const results=await api('/api/lexicon/lookup?'+params);
  lex.replaceChildren();
  if(!results.results.length)lex.append(el('p','hint','Kein Lexikoneintrag vorhanden. Importiere unter Textmodule ein passendes Wörterbuch.'));
  for(const item of results.results){const article=el('article','lexicon-card');
   article.append(el('b','',item.lemma+' · '+item.title));
   if(item.gloss)article.append(el('p','',item.gloss));
   article.append(el('p','lexicon-definition',item.definition));
   if(item.strong)article.append(el('small','',`Strong: ${item.strong}`));
   article.append(el('small','',`Quelle: ${item.provenance} · Lizenz: ${item.license}${item.reference?' · '+item.reference:''}`));
   lex.append(article)}
 }catch(e){lex.replaceChildren(el('p','hint','Lexikonabfrage fehlgeschlagen: '+e.message))}
 const btn=el('button','btn primary','Alle Vorkommen dieses Lemmas');box.append(btn);
 btn.onclick=async()=>{try{const data=await api('/api/morphology/lemma?module_id='+encodeURIComponent(mod.id)+'&lemma='+encodeURIComponent(word.lemma));const target=$('#lemma-results');target.replaceChildren(el('p','hint',data.results.length+' Treffer im annotierten Bestand'));for(const hit of data.results){const row=el('button','lemma-hit',`${hit.book} ${hit.chapter},${hit.verse} · ${hit.surface} · ${hit.morph}`);row.onclick=()=>go(hit.book,hit.chapter,hit.verse);target.append(row)}}catch(e){message(e.message)}};
}
$('#morph-import-form').onsubmit=async e=>{e.preventDefault();const form=e.target,status=$('#morph-import-status');status.textContent='Wortdatei wird geprüft…';try{const result=await api('/api/morphology/import',{method:'POST',body:new FormData(form)});status.textContent=`Erfolgreich: ${result.tokens} Wörter in ${result.annotated_verses} Versen. Die markierten Wörter sind jetzt anklickbar.`;await go(view.book,view.chapter,activeVerse)}catch(err){status.textContent='Fehler: '+err.message}};
async function refreshLexica(){
 const target=$('#lexicon-manage-list');target.replaceChildren();
 try{const data=await api('/api/lexica');if(!data.length)target.append(el('p','hint','Noch keine Wörterbücher installiert.'));
 for(const m of data){const row=el('div','manage-row'),detail=el('div');detail.append(el('b','',m.title),el('small','',`${m.language} · ${m.entry_count} Einträge · ${m.license}`));
 const btn=el('button','btn','Entfernen');btn.type='button';btn.onclick=async()=>{if(!confirm(`Lexikon „${m.title}“ löschen?`))return;
 try{await api('/api/lexica/'+encodeURIComponent(m.id),{method:'DELETE'});await refreshLexica()}catch(e){alert(e.message)}};
 row.append(detail,btn);target.append(row)}}catch(e){target.append(el('p','hint',e.message))}
}
$('#module-btn').addEventListener('click',refreshLexica);
$('#add-module-left').addEventListener('click',refreshLexica);
$('#lexicon-import-form').elements.namedItem('file').addEventListener('change',e=>{
 const file=e.target.files?.[0];if(!file)return;
 const form=$('#lexicon-import-form'),name=file.name.replace(/\.(csv|tsv|txt)$/i,'');
 form.elements.namedItem('module_id').value=(name.replace(/[^a-zA-Z0-9_-]/g,'-').slice(0,48)||'lexicon');
 form.elements.namedItem('title').value=name.replace(/[_-]/g,' ');
 const demo={demo_lexikon_grc:{id:'demo-lex-grc',title:'Griechisches Mini-Lexikon (Demo)',lang:'grc'},demo_lexikon_he:{id:'demo-lex-he',title:'Hebräisches Mini-Lexikon (Demo)',lang:'he'}}[name];
 if(demo){form.elements.namedItem('module_id').value=demo.id;form.elements.namedItem('title').value=demo.title;form.elements.namedItem('language').value=demo.lang;
 form.elements.namedItem('license_name').value='CC0 – selbst erstellte Demonstrationsdefinitionen';form.elements.namedItem('provenance').value='Amicus Theologi Demonstrationsmaterial, 2026';}
});
$('#lexicon-import-form').onsubmit=async e=>{e.preventDefault();const form=e.target,status=$('#lexicon-import-status'),button=form.querySelector('button[type=submit]');
 status.textContent='Lexikon wird geprüft …';button.disabled=true;
 try{const result=await api('/api/lexica/import',{method:'POST',body:new FormData(form)});status.textContent=`Lexikon importiert: ${result.entries} Einträge.`;form.reset();await refreshLexica()}
 catch(err){status.textContent='Fehler: '+err.message}finally{button.disabled=false}
};
start();

// 0.6.1 Scientific sources: one guided workflow, no manual column entry.
const scientificSource=$('#scientific-source'), scientificCorpus=$('#scientific-corpus');
function updateScientificGuide(){
 const source=scientificSource.value;
 $('#scientific-corpus-wrap').hidden=source!=='step';
 const guide={step:['STEPBible stellt annotierte Originalsprachen-Daten zur Verfügung. TAGNT verwendet hier bewusst nur Wörter der SBL-Edition; TAHOT ist zunächst experimentell.','https://github.com/STEPBible/STEPBible-Data'],oshb:['Open Scriptures enthält die hebräische Bibel mit Wortdaten und Morphologie. Dies ist der empfohlene hebräische Einstieg.','https://github.com/openscriptures/morphhb'],sword:['CrossWire/SWORD: Lade auf der Originalseite ein SWORD-Raw-ZIP herunter und wähle es hier aus. Nicht alle SWORD-Formate werden unterstützt; die Quelle bestimmt die Lizenz.','https://www.crosswire.org/sword/modules/ModDisp.jsp']}[source];
 $('#scientific-description').textContent=guide[0];$('#scientific-site').href=guide[1];
 $('#scientific-warning').textContent=source==='sword'?'SWORD benötigt ein heruntergeladenes Modul-ZIP und die optionale Python-Bibliothek pysword. Modul-Lizenz auf der Quellseite prüfen.':'Ohne ausgewählte Datei wird das offizielle Projektarchiv heruntergeladen. Internet erforderlich; später ist das installierte Modul offline nutzbar.';
 $('#scientific-file').value='';
}
scientificSource.addEventListener('change',updateScientificGuide);updateScientificGuide();
$('#scientific-form').addEventListener('submit',async e=>{
 e.preventDefault();const btn=$('#scientific-import-button'),status=$('#scientific-status');btn.disabled=true;
 status.textContent='Import läuft. Bitte diesen Dialog geöffnet lassen …';
 try{const source=scientificSource.value,corpus=scientificCorpus.value,file=$('#scientific-file').files[0];let result;
 if(file){const data=new FormData();data.set('source',source);data.set('corpus',corpus);data.set('file',file);result=await api('/api/scientific/import',{method:'POST',body:data});}
 else{if(source==='sword')throw new Error('Bitte zuerst ein SWORD-ZIP von CrossWire auswählen.');result=await api('/api/scientific/download?source='+encodeURIComponent(source)+'&corpus='+encodeURIComponent(corpus),{method:'POST'});}
 status.textContent=`Installiert: ${result.module_id} · ${result.verses} Verse · ${result.tokens} Wortannotationen. Die Ausgabe erscheint nun in der Bibelansicht.`;
 await refreshModules();await go(view.book,view.chapter,activeVerse);
 }catch(err){status.textContent='Import nicht abgeschlossen: '+err.message}finally{btn.disabled=false;}
});


// 0.6.3: curated one-click catalog; existing manual import remains available.
async function refreshCatalog(){
 const root=$('#catalog-items');root.replaceChildren();
 try{const items=await api('/api/catalog');
  for(const item of items){
   const row=el('div','manage-row'),detail=el('div');
   detail.append(el('b','',item.title),el('small','',item.kind+' · '+item.language+' · '+item.license));
   const btn=el('button','btn',item.installed?'Installiert':'Installieren');btn.type='button';btn.disabled=item.installed;
   btn.onclick=async()=>{btn.disabled=true;$('#catalog-status').textContent='Lade '+item.title+' von der Originalquelle und prüfe die Daten. Bitte den Dialog geöffnet lassen …';
    try{const res=await api('/api/catalog/'+encodeURIComponent(item.id)+'/install',{method:'POST'});
     $('#catalog-status').textContent=`Installiert: ${item.title} (${res.entries??res.tokens??0} ${res.entries!==undefined?'Lexikoneinträge':'Wortannotationen'}).`;
     await refreshModules();await refreshLexica();await go(view.book,view.chapter,activeVerse);await refreshCatalog();
    }catch(error){$('#catalog-status').textContent='Installation fehlgeschlagen: '+error.message;btn.disabled=false;}
   };
   row.append(detail,btn);root.append(row);
  }
 }catch(error){root.append(el('p','hint','Katalog nicht verfügbar: '+error.message))}
}
$('#module-btn').addEventListener('click',refreshCatalog);
$('#add-module-left').addEventListener('click',refreshCatalog);
$('#factory-reset-btn').addEventListener('click',async()=>{
 if(!confirm('ACHTUNG: Alle Bibeltexte, Lexika, Annotationen und Einstellungen werden gelöscht. Fortfahren?'))return;
 const entered=prompt('Zum endgültigen Löschen bitte WERKSRESET eingeben:');
 if(entered!=='WERKSRESET'){ $('#factory-reset-status').textContent='Abgebrochen – keine Daten gelöscht.';return;}
 const btn=$('#factory-reset-btn');btn.disabled=true;
 try{await api('/api/factory-reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({confirmation:entered})});
   $('#factory-reset-status').textContent='Werkseinstellungen wiederhergestellt.';location.reload();
 }catch(error){$('#factory-reset-status').textContent='Reset fehlgeschlagen: '+error.message;btn.disabled=false;}
});

// Studies and verse highlights (v0.7)
const refNow=()=>({book:view?.book,chapter:view?.chapter,verse:activeVerse});
const studyKey=(b,c,v)=>`${b}:${c}:${v}`;
async function refreshProjects(){
 allProjects=await api('/api/projects');
 if(currentProjectId&&!allProjects.some(p=>p.id===currentProjectId))currentProjectId=null;
 if(!currentProjectId&&allProjects.length)currentProjectId=allProjects[0].id;
 const list=$('#projects-list');list.replaceChildren();
 for(const project of allProjects){const btn=el('button','search-hit'+(currentProjectId===project.id?' chosen':''));btn.type='button';btn.append(el('b','',project.title),el('small','',project.description||'Ohne Beschreibung'));btn.onclick=async()=>{currentProjectId=project.id;await refreshProjects()};list.append(btn)}
 if(!allProjects.length)list.append(el('p','hint','Noch keine Studienprojekte angelegt.'));
 const active=allProjects.find(p=>p.id===currentProjectId);
 $('#current-project-name').textContent=active?`${active.title} · ${active.description||'Keine Beschreibung'}`:'Noch kein Projekt ausgewählt.';
 await refreshStudyPane();await refreshProjectNotes();
}
async function refreshProjectNotes(){
 const root=$('#project-notes-list');root.replaceChildren();if(!currentProjectId)return;
 try {const data=await api(`/api/projects/${currentProjectId}/annotations`);
 for(const note of data.notes){const wrap=el('div','module-entry');const jump=el('button','btn',`${note.book} ${note.chapter},${note.verse}`);jump.onclick=()=>{go(note.book,note.chapter,note.verse);$('#projects-dialog').close()};wrap.append(jump,el('p','',note.content));root.append(wrap)}
 if(!data.notes.length)root.append(el('p','hint','Noch keine Notizen.'));
 }catch(e){root.append(el('p','hint',e.message))}
}
async function refreshStudyPane(){
 const root=$('#study-pane');if(!root||!view)return;root.replaceChildren();
 if(!currentProjectId){root.append(el('p','hint','Lege über „Studienprojekte“ ein Projekt an.'));studyHighlights={};paintHighlights();return}
 const ref=refNow();const key=studyKey(ref.book,ref.chapter,ref.verse);
 const title=allProjects.find(p=>p.id===currentProjectId)?.title||'';
 root.append(el('p','hint',`${title} · ${ref.book} ${ref.chapter},${ref.verse}`));
 const form=el('form','study-note-form');const field=el('textarea');field.rows=4;field.maxLength=20000;field.placeholder='Eigene exegetische Beobachtung oder Notiz …';field.required=true;const add=el('button','btn primary','Notiz speichern');form.append(field,add);
 form.onsubmit=async e=>{e.preventDefault();try{await api(`/api/projects/${currentProjectId}/notes`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...ref,content:field.value})});field.value='';await refreshStudyPane();await refreshProjectNotes()}catch(e){alert(e.message)}};root.append(form);
 const colors=el('div','highlight-tools');colors.append(el('span','','Vers markieren: '));
 for(const [code,label] of [['yellow','Gelb'],['green','Grün'],['blue','Blau'],['pink','Rosa'],['orange','Orange'],['','Entfernen']]){
 const btn=el('button','btn mark-'+code,label);btn.type='button';btn.onclick=async()=>{try{await api(`/api/projects/${currentProjectId}/highlight`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({...ref,color:code||null})});await refreshStudyPane()}catch(e){alert(e.message)}};colors.append(btn)}root.append(colors);
 try{const data=await api(`/api/projects/${currentProjectId}/annotations?book=${encodeURIComponent(ref.book)}&chapter=${ref.chapter}`);
 studyHighlights=Object.fromEntries(data.highlights.map(h=>[studyKey(h.book,h.chapter,h.verse),h.color]));paintHighlights();
 const current=data.notes.filter(n=>n.verse===ref.verse);
 for(const note of current){const card=el('article','study-note');card.append(el('p','',note.content));const edit=el('button','btn','Bearbeiten'),del=el('button','btn','Löschen');edit.type=del.type='button';edit.onclick=async()=>{const value=prompt('Notiz bearbeiten:',note.content);if(value===null)return;try{await api(`/api/projects/${currentProjectId}/notes/${note.id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({content:value})});await refreshStudyPane();await refreshProjectNotes()}catch(e){alert(e.message)}};del.onclick=async()=>{if(!confirm('Diese Notiz wirklich löschen?'))return;await api(`/api/projects/${currentProjectId}/notes/${note.id}`,{method:'DELETE'});await refreshStudyPane();await refreshProjectNotes()};card.append(edit,del);root.append(card)}
 }catch(e){root.append(el('p','hint','Notizen konnten nicht geladen werden: '+e.message))}
}
function paintHighlights(){if(!view)return;for(const row of $$('.verse-line')){for(const c of ['yellow','green','blue','pink','orange'])row.classList.remove('highlight-'+c);const c=studyHighlights[studyKey(view.book,view.chapter,Number(row.dataset.verse))];if(c)row.classList.add('highlight-'+c)}}
$('#projects-btn').onclick=async()=>{await refreshProjects();show('#projects-dialog')};
$('#projects-close').onclick=()=>$('#projects-dialog').close();
$('#project-create-form').onsubmit=async e=>{e.preventDefault();const f=e.target;try{const result=await api('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:f.elements.title.value,description:f.elements.description.value})});currentProjectId=result.id;f.reset();await refreshProjects()}catch(e){$('#project-status').textContent=e.message}};
$('#project-edit').onclick=async()=>{const p=allProjects.find(x=>x.id===currentProjectId);if(!p)return;const title=prompt('Projekttitel:',p.title);if(title===null)return;const description=prompt('Beschreibung:',p.description);if(description===null)return;try{await api(`/api/projects/${p.id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,description})});await refreshProjects()}catch(e){alert(e.message)}};
$('#project-delete').onclick=async()=>{const p=allProjects.find(x=>x.id===currentProjectId);if(!p||!confirm(`Projekt „${p.title}“ mit ALLEN zugehörigen Notizen und Markierungen endgültig löschen?`))return;await api(`/api/projects/${p.id}`,{method:'DELETE'});currentProjectId=null;await refreshProjects()};
$('#project-export').onclick=async()=>{if(!currentProjectId)return;try{const data=await api(`/api/projects/${currentProjectId}/export`);const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=el('a');a.href=url;a.download=`amicus-projekt-${currentProjectId}.json`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}catch(e){alert(e.message)}};
refreshProjects().catch(e=>console.warn('Studienprojekte beim Start:',e));
