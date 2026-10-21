"use strict";
const $=s=>document.querySelector(s);
const make=(tag,cls='',value)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=value;return e;};
const state={modules:[],active:'',ref:'',refs:[],passage:null,search:{offset:0,limit:50,total:0}};
const wordCache=new Map();
let tooltipRequest=0;
let hoverDelay=0;
function cacheKey(position){return [state.active,state.ref,position].join('::');}
async function fetchWord(position){
 const key=cacheKey(position);
 if(!wordCache.has(key)){
  if(wordCache.size>400)wordCache.clear();
  wordCache.set(key,api(url('/api/sources/word',{module_id:state.active,ref:state.ref,position}))
   .catch(e=>{wordCache.delete(key);throw e;}));
 }
 return wordCache.get(key);
}
function tooltipNode(){
 let node=$('#word-tooltip');
 if(!node){node=make('div','word-tooltip');node.id='word-tooltip';node.role='tooltip';node.hidden=true;document.body.append(node);}
 return node;
}
function hideTooltip(){clearTimeout(hoverDelay);tooltipRequest++;const node=$('#word-tooltip');if(node)node.hidden=true;}
function positionTooltip(button,node){
 const anchor=button.getBoundingClientRect(),box=node.getBoundingClientRect();
 const left=Math.max(9,Math.min(anchor.left+anchor.width/2-box.width/2,window.innerWidth-box.width-9));
 const top=anchor.top-box.height-10>=7?anchor.top-box.height-10:anchor.bottom+10;
 node.style.left=left+'px';node.style.top=Math.min(top,window.innerHeight-box.height-8)+'px';
}
async function showTooltip(button,position){
 const request=++tooltipRequest,node=tooltipNode();
 node.replaceChildren(make('strong','',button.textContent),make('small','','Lade Wortanalyse …'));
 node.hidden=false;positionTooltip(button,node);
 try{
  const w=await fetchWord(position);
  if(request!==tooltipRequest||!button.isConnected)return;
  const subtitle=w.has_annotation?'Lemma: '+w.lemma:(w.candidate_analyses?.length
   ?'Mögliche Grundform: '+w.candidate_analyses[0].lemma:'Keine Lemmadaten für diese Textstelle');
  node.replaceChildren(make('strong','',w.surface),make('span','',subtitle));
  if(w.has_annotation){
   node.append(make('small','',w.grammar));
   node.append(make('small','tooltip-provenance',({
    automatic:'Automatische Analyse · nicht redaktionell geprüft',
    mixed:'Gemischte Herkunft · einzelne Ergänzungen automatisch',
    edition:'Editionsgebundene Analyse · Originalcodes der Quelle',
    reviewed:'Redaktionell geprüft laut Quellenangabe',
    provided:'Importierte Analyse · Prüfstatus siehe Editionsangabe'
   })[w.annotation_quality]||'Importierte Wortanalyse'));
  }else if(w.candidate_analyses?.length){
   node.append(make('small','',w.candidate_analyses[0].grammar));
   node.append(make('small','tooltip-provenance','Nur Vergleichskorpus! Für diese Stelle nicht geprüft.'));
  }
  const translation=w.lexica?.find(entry=>String(entry.display_gloss||'').trim());
  if(translation){
   node.append(make('small','tooltip-gloss',translation.display_gloss.trim().slice(0,200)));
   node.append(make('small','tooltip-provenance','Übersetzung aus: '+translation.title));
  }
  positionTooltip(button,node);
 }catch(error){if(request===tooltipRequest){node.replaceChildren(make('small','',error.message));positionTooltip(button,node);}}
}
async function api(path,opts={}){
 const response=await fetch(path,opts);
 if(!response.ok){let obj;try{obj=await response.json();}catch{}
  throw new Error(typeof obj?.detail==='string'?obj.detail:'HTTP '+response.status);}
 return response.json();
}
const url=(path,data)=>path+'?'+new URLSearchParams(data);
const fmt=n=>Number(n||0).toLocaleString('de-DE');
function status(id,value,error=false){const e=document.getElementById(id);e.textContent=value;e.classList.toggle('error',error);}
function toast(value,error=false){const e=$('#toast');e.hidden=false;e.textContent=value;e.classList.toggle('error',error);clearTimeout(toast.timer);toast.timer=setTimeout(()=>e.hidden=true,5000);}
function activeModule(){return state.modules.find(m=>m.id===state.active);}
function dialog(id){document.getElementById(id).showModal();}
async function loadModules(preferred=state.active){
 state.modules=await api('/api/sources/modules');
 const select=$('#module-select');select.replaceChildren(new Option('Quelle wählen',''));
 const annotations=$('#annotation-module');annotations.replaceChildren(new Option('Quellentext wählen',''));
 const scope=$('#search-scope'),oldScope=scope.value;
 scope.replaceChildren(new Option('Alle Quellen',''));
 const list=$('#library');list.replaceChildren();
 const languageLabels={la:'Lateinische Quellen',grc:'Altgriechische Quellen',he:'Hebräische Quellen'};
 for(const language of ['la','grc','he']){
  const entries=state.modules.filter(m=>m.language===language);if(!entries.length)continue;
  const moduleGroup=document.createElement('optgroup');moduleGroup.label=languageLabels[language];select.append(moduleGroup);
  const scopeGroup=document.createElement('optgroup');scopeGroup.label=languageLabels[language];scope.append(scopeGroup);
  list.append(make('h4','source-group-title',languageLabels[language]));
  for(const m of entries){
  moduleGroup.append(new Option(m.title,m.id));annotations.add(new Option(m.title,m.id));
  scopeGroup.append(new Option(m.title,m.id));
  const row=make('div','library-item'),open=make('button','library-link',m.title);
  open.title=m.author+' · '+m.edition;open.onclick=()=>selectModule(m.id);
  row.append(open,make('small','',m.language+' · '+fmt(m.section_count)+' Abschnitte · '+fmt(m.annotated_tokens)+' Wörter mit Analyse'));
  const remove=make('button','remove','×');remove.title='Quellenmodul löschen';
  remove.onclick=async()=>{
   if(!confirm('„'+m.title+'“ inklusive Annotationen und Quellen-Notizen wirklich löschen?'))return;
   try{await api('/api/sources/modules/'+encodeURIComponent(m.id),{method:'DELETE'});
    await loadModules(state.active===m.id?'':state.active);toast('Quelle entfernt.');
   }catch(error){toast(error.message,true);}
  };row.append(remove);list.append(row);
  }
 }
 if(!state.modules.length)list.append(make('p','placeholder','Noch keine Quellen installiert.'));
 scope.value=state.modules.some(m=>m.id===oldScope)?oldScope:'';
 if(state.modules.some(m=>m.id===preferred))await selectModule(preferred);
 else if(state.modules.length)await selectModule(state.modules[0].id);
 else{
  state.active='';state.ref='';state.refs=[];state.passage=null;select.value='';
  $('#reader-title').textContent='Quellenbibliothek';$('#reader-lang').textContent='–';
  $('#source-reference').textContent='Noch keine Quelle gewählt';
  $('#source-text').replaceChildren(make('p','placeholder','Öffne den Katalog oder importiere einen eigenen Text.'));
  $('#word-analysis').replaceChildren(make('p','placeholder','Keine Wortauswahl.'));
  $('#lexicon-results').replaceChildren();$('#word-stats').replaceChildren();
  $('#note-text').disabled=true;$('#note-save').disabled=true;
 }
}
async function selectModule(id,requestedRef=''){
 hideTooltip();
 state.active=id;$('#module-select').value=id;
 const m=activeModule();if(!m)return;
 $('#reader-title').textContent=m.title;
 $('#reader-lang').textContent=({la:'Latein',grc:'Altgriechisch',he:'Hebräisch'})[m.language]||m.language;
 const annotation=m.package_metadata?.annotation_edition;
 $('#edition-note').textContent=m.author+' · '+m.edition+' · '+m.license+' · Quelle: '+m.provenance
  +' · '+fmt(m.annotated_tokens)+' Wörter mit positionsgenauen Annotationen'
  +(annotation?' · Morphologie: '+annotation.provider+' ('+annotation.method+'). '+annotation.coverage:'')
  +(m.package_metadata?.scope?' · Umfang: '+m.package_metadata.scope:'');
 state.refs=await api(url('/api/sources/sections',{module_id:id}));
 const dropdown=$('#ref-select');dropdown.replaceChildren(new Option('Abschnitt wählen',''));
 for(const row of state.refs)dropdown.add(new Option(row.ref,row.ref));
 if(state.refs.length)await selectPassage(state.refs.some(r=>r.ref===requestedRef)?requestedRef:state.refs[0].ref);
 else{$('#source-text').replaceChildren(make('p','placeholder','Keine Abschnitte vorhanden.'));}
 await displayStats();
}
async function selectPassage(ref){
 if(!state.active||!ref)return;
 hideTooltip();
 state.passage=await api(url('/api/sources/passage',{module_id:state.active,ref}));
 state.ref=ref;$('#ref-select').value=ref;
 $('#source-reference').textContent=(activeModule()?.author||'')+' · '+ref;
 $('#section-prev').disabled=!state.passage.previous;$('#section-next').disabled=!state.passage.next;
 const chars=Array.from(state.passage.text),out=$('#source-text');out.replaceChildren();
 const para=make('p','source-paragraph');para.lang=activeModule()?.language;if(para.lang==='he')para.dir='rtl';
 let offset=0;
 for(const t of state.passage.tokens){
  para.append(document.createTextNode(chars.slice(offset,t.start).join('')));
  const button=make('button','word-token',chars.slice(t.start,t.end).join(''));
  button.type='button';button.setAttribute('aria-label','Wort '+button.textContent+' analysieren');
  if(t.lemma)button.classList.add('annotated');
  button.addEventListener('pointerenter',e=>{if(e.pointerType!=='touch'){
   clearTimeout(hoverDelay);hoverDelay=setTimeout(()=>showTooltip(button,t.position),110);
  }});
  button.addEventListener('pointerleave',e=>{if(e.pointerType!=='touch')hideTooltip();});
  button.addEventListener('focus',()=>showTooltip(button,t.position));
  button.addEventListener('blur',hideTooltip);
  button.onclick=async()=>{
   for(const old of out.querySelectorAll('.word-token.selected'))old.classList.remove('selected');
   button.classList.add('selected');
   if(window.matchMedia('(hover: none)').matches)showTooltip(button,t.position);
   await selectWord(t.position);
  };
  para.append(button);offset=t.end;
 }
 para.append(document.createTextNode(chars.slice(offset).join('')));out.append(para);
 const translations=$('#source-translations');translations.replaceChildren();
 for(const edition of [...(state.passage.translations||[]),...(state.passage.work_translations||[])]){
  const card=make('article','translation-card'),heading=make('div','translation-heading');
  heading.append(make('h3','',edition.title),make('span','tag',({de:'Deutsch',en:'Englisch',it:'Italienisch',la:'Latein',grc:'Altgriechisch',he:'Hebräisch'})[edition.language]||edition.language));
  if(state.passage.work_translations?.some(item=>item.translation_id===edition.translation_id))heading.append(make('span','tag','Gesamtübersetzung'));
  card.append(heading,make('p','translation-text',edition.text),make('small','translation-credit',edition.author+' · '+edition.edition+' · '+edition.license+' · '+edition.provenance));
  translations.append(card);
 }
 $('#word-analysis').replaceChildren(make('p','placeholder','Klicke ein Wort, um es zu analysieren.'));
 $('#lexicon-results').replaceChildren(make('p','placeholder','Keine Wortauswahl.'));
 $('#note-text').disabled=false;$('#note-save').disabled=false;
 $('#note-text').value=(await api(url('/api/sources/note',{module_id:state.active,ref}))).content;
 status('note-status','');
}
async function selectWord(position){
 try{
  const w=await fetchWord(position);
  const pane=$('#word-analysis');pane.replaceChildren();
  pane.append(make('h3','',w.surface),
   make('p','','Grundform: '+(w.has_annotation?w.lemma:'Für diese Stelle nicht annotiert')),
   make('p','','Morphologie: '+w.grammar));
  if(w.has_annotation){
   pane.append(make('p','field-caption',w.annotation_status||({
    automatic:'Diese Analyse wurde automatisch erzeugt und nicht redaktionell geprüft.',
    mixed:'Dieses Paket kombiniert Quellanalysen mit automatisch ergänzten Wörtern; die Herkunft dieses einzelnen Tokens ist nicht separat ausgewiesen.',
    edition:'Die Analyse übernimmt die Morphologiecodes der genannten Edition.',
    reviewed:'Die Annotation wurde laut Quellenangabe redaktionell geprüft.',
    provided:'Die Analyse stammt aus dem importierten Datensatz; ein Prüfstatus ist nicht ausgewiesen.'
   })[w.annotation_quality]||'Die Analyse stammt aus dem importierten Datensatz.'));
  }else if(w.candidate_analyses?.length){
   const possibilities=make('div','candidate-analyses');
   possibilities.append(make('h4','','Mögliche Analysen aus anderen Texten'));
   possibilities.append(make('p','field-caption','Achtung: Das sind belegte Formen aus anderen Korpora – keine überprüfte Analyse dieser Textstelle.'));
   for(const c of w.candidate_analyses.slice(0,6)){
    const b=make('button','candidate-line');
    b.append(make('strong','',c.lemma),make('small','',c.grammar),
     make('small','','Belegt in: '+c.source_title+' ('+fmt(c.attestations)+'×)'));
    b.onclick=()=>{$('#lemma-query').value=c.lemma;$('#surface-query').value='';$('#q').value='';performSearch();};
    possibilities.append(b);
   }
   pane.append(possibilities);
  }else{
   const hint=make('p','field-caption','Für dieses Wort fehlen Wortannotationen und Belege in installierten Vergleichskorpora.');
   const open=make('button','','Annotierte Korpora installieren');
   open.onclick=()=>{$('#catalog-category').value='sprachen';$('#catalog-language').value=activeModule()?.language||'';
    dialog('catalog-dialog');loadCatalog().catch(e=>status('catalog-status',e.message,true));};
   pane.append(hint,open);
  }
  if(w.strong)pane.append(make('p','','Strong: '+w.strong));
  const buttons=make('div','word-actions'),form=make('button','','Schreibweise suchen');
  form.onclick=()=>{$('#q').value='';$('#lemma-query').value='';$('#surface-query').value=w.surface;performSearch();};
  buttons.append(form);
  if(w.has_annotation){
   const lemma=make('button','','Lemma suchen'),stats=make('button','','Wortformen');
   lemma.onclick=()=>{$('#q').value='';$('#surface-query').value='';$('#lemma-query').value=w.lemma;performSearch();};
   stats.onclick=()=>displayStats(w.lemma);buttons.append(lemma,stats);await displayStats(w.lemma);
  }pane.append(buttons);
  const entries=$('#lexicon-results');entries.replaceChildren();
  if(w.lexicon_candidate_lemma)entries.append(make('p','field-caption','Lexikontreffer zur möglichen Grundform „'+w.lexicon_candidate_lemma+'“ – nicht für diese Textstelle bestätigt.'));
  if(!w.lexica?.length)entries.append(make('p','placeholder','Kein passendes Lexikon installiert oder kein Wörterbucheintrag gefunden.'));
  else for(const l of w.lexica){
   const card=make('article','lexicon-entry');
   card.append(make('strong','',l.lemma+' · '+l.title),
    make('p','',l.display_gloss||l.gloss||l.definition.slice(0,600)));
   const detail=make('details');detail.append(make('summary','','Originaleintrag'),make('p','',l.definition));
   card.append(detail,make('small','',l.reference+' · '+l.license));entries.append(card);
  }
 }catch(error){toast(error.message,true);}
}
async function displayStats(lemma=''){
 if(!state.active)return;
 const pane=$('#word-stats');
 try{
  const d=await api(url('/api/sources/stats',{module_id:state.active,lemma}));
  pane.replaceChildren(make('p','stats-caption',fmt(d.tokens)+' Wörter · '+fmt(d.annotated)+' annotiert · '+d.basis));
  if(lemma)pane.append(make('h4','','Grundform: '+lemma));
  const max=Math.max(1,...d.forms.map(x=>x.count));
  for(const f of d.forms.slice(0,50)){
   const button=make('button','stat-line'),bar=make('span','stat-track'),fill=make('span','stat-fill');
   fill.style.width=(100*f.count/max)+'%';bar.append(fill);
   button.append(make('span','',f.form),bar,make('strong','',String(f.count)));
   button.onclick=()=>{$('#q').value='';$('#lemma-query').value='';$('#surface-query').value=f.form;performSearch();};
   pane.append(button);
  }
  if(lemma&&d.references.length){
   pane.append(make('h4','','Stellenverteilung'));
   for(const r of d.references.slice(0,30)){
    const b=make('button','ref-stat',r.ref+' · '+fmt(r.count));
    b.onclick=()=>selectPassage(r.ref);pane.append(b);
   }
  }
 }catch(error){pane.replaceChildren(make('p','message error',error.message));}
}
async function performSearch(offset=0){
 const args=Object.fromEntries(new FormData($('#search-form')).entries());
 args.limit='50';args.offset=String(offset);
 if(!args.q&&!args.lemma&&!args.surface&&!args.morph){
  status('search-status','Bitte Suchtext, Lemma, Wortform oder Morphologie eingeben.',true);return;
 }
 try{
  const d=await api(url('/api/sources/search',args));
  state.search={...args,total:d.total,limit:d.limit,offset};
  status('search-status',fmt(d.total)+' Treffer');
  const pane=$('#search-results');pane.replaceChildren();
  for(const item of d.results){
   const b=make('button','result-card');
   b.append(make('strong','',item.title+' · '+item.ref),
    make('span','',item.text.slice(0,230)+(item.text.length>230?' …':'')));
   b.onclick=()=>selectModule(item.module_id,item.ref);pane.append(b);
  }
  if(!d.total)pane.append(make('p','placeholder','Keine Treffer im gewählten Quellenbestand.'));
  $('#search-count').textContent=fmt(offset+d.results.length)+' / '+fmt(d.total);
  $('#search-prev').disabled=offset<=0;$('#search-next').disabled=offset+d.limit>=d.total;
 }catch(error){status('search-status',error.message,true);}
}
async function loadCatalog(){
 const data=await api('/api/sources/catalog'),lang=$('#catalog-language').value,
  category=$('#catalog-category').value,pane=$('#catalog-list');
 pane.replaceChildren();
 const groups=[
  {id:'quellen',name:'01 · Primärquellen',description:'Kirchenväter, antike Philosophie und hebräische Grundquellen'},
  {id:'lexika',name:'02 · Lexika',description:'Historische Wörterbücher mit Herkunfts- und Editionsangaben'},
  {id:'sprachen',name:'03 · Sprachwissenschaftliche Daten',description:'Textproben mit geprüfter Zuordnung importierter Lemmata und Grammatikdaten'},
  {id:'hilfsmittel',name:'04 · Hilfsmittel',description:'Ergänzende Forschungsportale und grammatische Dokumentation'}
 ];
 for(const group of groups){
  if(category&&group.id!==category)continue;
  const filtered=data.filter(x=>x.category===group.id&&(!lang||x.language===lang||x.language==='all'));
  if(!filtered.length)continue;
  const heading=make('div','catalog-group-header');
  heading.append(make('h3','',group.name),make('p','',group.description));pane.append(heading);
  for(const item of filtered){
  const card=make('article','catalog-card'),head=make('div','catalog-heading');
  head.append(make('h3','',item.title),make('span','tag',({la:'Latein',grc:'Altgriechisch',he:'Hebräisch',all:'Allgemein'})[item.language]||item.language));
  const kind=({lexicon:'Wörterbuch',treebank:'Text mit Wortanalysen',
   reference:'Externer Forschungsdienst',text:'Text ohne positionsgenaue Morphologie'})[item.kind]||'Datenmodul';
  card.append(head,make('p','',kind+' · '+(item.edition||'')),
   make('small','','Rechte: '+item.license+' · '+item.provenance));
  if(item.description)card.append(make('p','',item.description));
  const row=make('div','catalog-action');
  if(item.download_size_hint)row.append(make('small','',item.download_size_hint));
  if(item.kind==='reference'){
   const link=make('a','catalog-external','↗ Forschungsangebot öffnen');
   link.href=item.external_url;link.target='_blank';link.rel='noopener noreferrer';
   row.append(link);card.append(row);pane.append(card);continue;
  }
  const button=make('button',item.installed?'':'primary',item.installed?'✓ Installiert':'↓ Installieren');
  button.disabled=item.installed;button.onclick=async()=>{
   button.disabled=true;button.textContent='Installiere …';
   status('catalog-status',item.title+' wird heruntergeladen und geprüft. Bitte warten.');
   try{
    const r=await api('/api/sources/catalog/'+encodeURIComponent(item.id)+'/install',{method:'POST'});
    const amount=fmt(r.sections||r.entries||0);
    let message=item.title+' installiert ('+amount+' Einträge).';
    if(item.kind==='treebank')message+=' '+fmt(r.annotated_sections||0)+' Abschnitte mit Wortanalysen.';
    if(r.annotation_skipped_sections)message+=' '+fmt(r.annotation_skipped_sections)+' Stellen wegen abweichender Tokenisierung ohne Annotation.';
    status('catalog-status',message);
    await loadModules();await loadCatalog();
   }catch(error){status('catalog-status',error.message,true);button.disabled=false;button.textContent='↻ Erneut versuchen';}
  };
  row.append(button);card.append(row);pane.append(card);
  }
 }
}
async function sendForm(id,endpoint,statusId,done){
 const form=document.getElementById(id),button=form.querySelector('button[type="submit"]');
 button.disabled=true;status(statusId,'Datei wird importiert …');
 try{
  const d=await api(endpoint,{method:'POST',body:new FormData(form)});
  status(statusId,'Erfolgreich: '+fmt(d.sections||d.tokens||d.entries||0)+' Einträge.');
  form.reset();await done(d);
 }catch(error){status(statusId,error.message,true);}
 finally{button.disabled=false;}
}
async function installPackage(form){
 const button=form.querySelector('button[type="submit"]');button.disabled=true;
 status('package-install-status','Paket wird geprüft. Texte und Wortdaten werden erst nach erfolgreicher Prüfung gemeinsam installiert.');
 try{
  const result=await api('/api/sources/packages/install',{method:'POST',body:new FormData(form)});
  status('package-install-status',fmt(result.sections)+' Abschnitte, '+fmt(result.annotated_sections)+' vollständig annotierte Abschnitte und '+fmt(result.translations)+' Übersetzungen '+(result.updated?'aktualisiert.':'installiert.'));
  form.reset();await loadModules(result.module_id);await loadCatalog();
 }catch(error){status('package-install-status',error.message,true);}
 finally{button.disabled=false;}
}
document.addEventListener('DOMContentLoaded',async()=>{
 document.addEventListener('scroll',hideTooltip,true);
 document.addEventListener('pointerdown',e=>{if(!e.target.closest('.word-token'))hideTooltip();});
 window.addEventListener('resize',hideTooltip);
 document.addEventListener('keydown',e=>{if(e.key==='Escape')hideTooltip();});
 $('#catalog-open').onclick=()=>{dialog('catalog-dialog');loadCatalog().catch(e=>status('catalog-status',e.message,true));};
 $('#package-install-form').onsubmit=e=>{e.preventDefault();installPackage(e.currentTarget);};
 $('#import-open').onclick=()=>dialog('import-dialog');$('#help-open').onclick=()=>dialog('help-dialog');
 for(const button of document.querySelectorAll('[data-close]'))button.onclick=()=>document.getElementById(button.dataset.close).close();
 $('#catalog-language').onchange=()=>loadCatalog().catch(e=>status('catalog-status',e.message,true));
 $('#catalog-category').onchange=()=>loadCatalog().catch(e=>status('catalog-status',e.message,true));
 $('#module-select').onchange=e=>selectModule(e.target.value).catch(x=>toast(x.message,true));
 $('#ref-select').onchange=e=>selectPassage(e.target.value).catch(x=>toast(x.message,true));
 $('#section-prev').onclick=()=>state.passage?.previous&&selectPassage(state.passage.previous);
 $('#section-next').onclick=()=>state.passage?.next&&selectPassage(state.passage.next);
 $('#search-form').onsubmit=e=>{e.preventDefault();performSearch();};
 $('#search-prev').onclick=()=>performSearch(Math.max(0,state.search.offset-state.search.limit));
 $('#search-next').onclick=()=>performSearch(state.search.offset+state.search.limit);
 $('#source-import-form').onsubmit=e=>{e.preventDefault();sendForm('source-import-form','/api/sources/import',
  'source-import-status',d=>loadModules(d.module_id));};
 $('#annotation-form').onsubmit=e=>{e.preventDefault();sendForm('annotation-form','/api/sources/annotations/import',
  'annotation-status',()=>loadModules(state.active));};
 $('#lexicon-form').onsubmit=e=>{e.preventDefault();sendForm('lexicon-form','/api/lexica/import','lexicon-status',async()=>{});};
 $('#note-save').onclick=async()=>{
  try{await api('/api/sources/note',{method:'PUT',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({module_id:state.active,ref:state.ref,content:$('#note-text').value})});
   status('note-status','Notiz gespeichert.');
  }catch(e){status('note-status',e.message,true);}
 };
 try{const settings=await api('/api/settings');
  document.body.dataset.theme=settings.theme==='light'?'light':'dark';await loadModules();
 }catch(e){toast('Quellenstudium nicht geladen: '+e.message,true);}
});
