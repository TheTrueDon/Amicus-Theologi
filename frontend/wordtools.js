/* Amicus Theologi – safe lexicon display, word previews and lemma concordance.
   All external lexical material is treated as UNTRUSTED content. */
(()=>{
'use strict';
const q=x=>document.querySelector(x);
const elt=(tag,cls,value)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(value!==undefined)node.textContent=String(value);return node};
const FORBIDDEN=new Set(['script','style','iframe','object','embed','svg','math','template','form','input','button','audio','video']);
const ALLOWED=new Map([['strong','strong'],['b','strong'],['em','em'],['i','em'],['u','u'],['sup','sup'],['sub','sub'],['small','small'],['code','code'],['ul','ul'],['ol','ol'],['li','li'],['br','br'],['p','p'],['div','div'],['blockquote','blockquote']]);
const STRUCTURAL=new Set(['div','p','ul','ol','li','blockquote']);

// Never use HTML injection for untrusted lexicon content. Parse in an inert
// document and COPY ONLY ALLOWED ELEMENTS with textContent (no attributes).
// Small token parser: avoids inserting arbitrary HTML, attributes, remote images
// or executable tags into a live or inert DOM.
const ENTITY_MAP={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '};
function decodeEntities(text){
 return text.replace(/&(#(?:x[0-9a-f]+|[0-9]+)|amp|lt|gt|quot|apos|nbsp);/gi,(whole,entity)=>{
  if(entity[0]!=='#')return ENTITY_MAP[entity.toLowerCase()]||whole;
  const hex=entity[1].toLowerCase()==='x';const code=Number.parseInt(entity.slice(hex?2:1),hex?16:10);
  return Number.isInteger(code)&&code>0&&code<=0x10ffff&&!(code>=0xd800&&code<=0xdfff)?String.fromCodePoint(code):whole;
 });
}
function appendLexicalTokens(text,root){
 const stack=[{tag:'root',node:root}];
 let skip=null,skipDepth=0;
 for(const token of String(text).match(/<[^>]{1,600}>|[^<]+|</g)||[]){
  const match=/^<\s*(\/)?\s*([a-z][a-z0-9-]*)\b[^>]*>$/i.exec(token);
  if(!match){if(!skip)stack[stack.length-1].node.append(document.createTextNode(decodeEntities(token)));continue}
  const closing=!!match[1],tag=match[2].toLowerCase();
  if(skip){
   if(tag===skip){if(closing){if(--skipDepth===0)skip=null}else skipDepth++}
   continue;
  }
  if(FORBIDDEN.has(tag)){
   if(!closing&&!/\/\s*>$/.test(token)){skip=tag;skipDepth=1}
   continue;
  }
  if(closing){
   for(let i=stack.length-1;i>0;i--){if(stack[i].tag===tag){stack.splice(i);break}}
   continue;
  }
  if(tag==='br'){stack[stack.length-1].node.append(document.createElement('br'));continue}
  const mapped=ALLOWED.get(tag);
  if(mapped){
   const parent=stack[stack.length-1].node;
   const element=document.createElement(mapped);parent.append(element);
   if(!/\/\s*>$/.test(token))stack.push({tag,node:element});
  }else if(tag==='a'){
   const element=document.createElement('span');element.className='lex-ref';stack[stack.length-1].node.append(element);
   stack.push({tag,node:element});
  }else{
   // Unknown markup is omitted, but its textual content remains visible.
  }
 }
}
function renderLexicalText(raw){
 const root=elt('div','lexical-richtext');
 const chunks=String(raw||'').split(/\s+·\s+/u);
 for(const rawChunk of chunks){
   // STEPBible imports may combine multiple source columns with " · ".
   const part=elt('div','lexical-section');
   appendLexicalTokens(rawChunk,part);
   if(part.textContent.trim())root.append(part);
 }
 if(!root.textContent.trim())root.append(elt('span','hint','Keine lesbare Beschreibung vorhanden.'));
 return root;
}
const tooltip=q('#word-tooltip');
const previewCache=new Map();
let timer=null,activeButton=null,requestSequence=0;
function placeTooltip(btn){
 if(!tooltip||tooltip.hidden||!btn?.isConnected)return;
 const rect=btn.getBoundingClientRect();
 const box=tooltip.getBoundingClientRect();
 const margin=10;
 let x=rect.left+(rect.width/2)-(box.width/2);
 x=Math.max(margin,Math.min(x,innerWidth-box.width-margin));
 let y=rect.bottom+10;
 if(y+box.height>innerHeight-margin)y=Math.max(margin,rect.top-box.height-10);
 tooltip.style.left=Math.round(x)+'px';tooltip.style.top=Math.round(y)+'px';
}
function hideTooltip(){
 clearTimeout(timer);++requestSequence;activeButton=null;
 if(tooltip){tooltip.hidden=true;tooltip.replaceChildren()}
}
function field(label,value,cls){const p=elt('div','word-preview-field');p.append(elt('span','word-preview-label',label),elt('span',cls||'',value));return p}
function drawPreview(btn,data){
 tooltip.replaceChildren();
 tooltip.append(elt('div','word-preview-title',data.surface||''));
 tooltip.append(field('Grundform',data.display_lemma|| (data.lemma_available===false?'Nicht im installierten Lexikon verfügbar':data.lemma||'–'),'word-preview-red'));
 tooltip.append(field('Bedeutung',data.gloss||'Keine verlässliche Übersetzung im installierten Lexikon')); 
 if(data.gloss_source)tooltip.append(elt('div','word-preview-source',data.gloss_source));
 if(data.grammar?.recognized&&data.grammar.features?.length){
   const parts=data.grammar.features.filter(x=>x.name!=='Wortart').map(x=>x.value);
   const pos=data.grammar.features.find(x=>x.name==='Wortart')?.value||'';
   tooltip.append(field('Grammatik',pos));
   if(parts.length)tooltip.append(elt('div','word-preview-red word-preview-grammar',parts.join(' · ')));
 }else{
   tooltip.append(field('Grammatik',data.morph||'Keine Analyse','word-preview-red'));
   if(data.morph)tooltip.append(elt('div','word-preview-source','Originalcode – nicht sicher entschlüsselt'));
 }
 placeTooltip(btn);
}
function showPreview(btn,word,mod){
 clearTimeout(timer);
 activeButton=btn;
 const sequence=++requestSequence;
 timer=setTimeout(async()=>{
  if(activeButton!==btn||!btn.isConnected)return;
  tooltip.hidden=false;
  tooltip.replaceChildren(elt('div','word-preview-title',word.surface),elt('div','word-preview-source','Lade Grundform, Bedeutung und Grammatik …')); 
  placeTooltip(btn);
  const key=[mod.id,word.book||'',word.chapter||'',word.verse,word.position].join('|');
  let data=previewCache.get(key);
  if(!data){
   try{
    const params=new URLSearchParams({module_id:mod.id,book:word.book||'',chapter:word.chapter||1,verse:word.verse,position:word.position});
    const response=await fetch('/api/morphology/preview?'+params);
    if(!response.ok)throw Error('HTTP '+response.status);
    data=await response.json();
    if(previewCache.size>400)previewCache.clear();
    previewCache.set(key,data);
   }catch{
    data={surface:word.surface,lemma:word.lemma,display_lemma:mod.language==='he'?'':word.lemma,lemma_available:mod.language!=='he',gloss:'Momentan nicht verfügbar',morph:word.morph||'',grammar:{recognized:false}};
   }
  }
  if(activeButton!==btn||sequence!==requestSequence||!btn.isConnected)return;
  drawPreview(btn,data);
 },110);
}
function enableHover(btn,word,mod){
 const complete={...word,book:word.book||q('#book-choice')?.value,chapter:word.chapter||Number(q('#chapter-choice')?.value||1)};
 btn.setAttribute('aria-label',`${word.surface}, Grundform ${word.lemma}. Klicken für Wortanalyse.`);
 btn.addEventListener('pointerenter',()=>showPreview(btn,complete,mod));
 btn.addEventListener('pointermove',()=>{if(activeButton===btn)placeTooltip(btn)});
 btn.addEventListener('pointerleave',hideTooltip);
 btn.addEventListener('focus',()=>showPreview(btn,complete,mod));
 btn.addEventListener('blur',hideTooltip);
}
const dialog=q('#lemma-dialog'),results=q('#lemma-dialog-results'),status=q('#lemma-dialog-status');
const prev=q('#lemma-dialog-prev'),next=q('#lemma-dialog-next');
const sortSelect=q('#lemma-dialog-sort'),directionBtn=q('#lemma-dialog-direction');
let concordanceRequest=0,concordanceState=null;
function closeConcordance(){concordanceRequest++;if(dialog.open)dialog.close()}
async function loadConcordance(offset){
 if(!concordanceState)return;
 const seq=++concordanceRequest;
 const {word,mod,sortBy,direction}=concordanceState;
 status.textContent='Vorkommen werden geladen …';
 results.replaceChildren();prev.disabled=next.disabled=true;
 try{
  const params=new URLSearchParams({module_id:mod.id,lemma:word.lemma,limit:50,offset:String(offset),sort_by:sortBy,direction});
  const response=await fetch('/api/morphology/lemma?'+params);
  let data=await response.json();
  if(!response.ok)throw Error(data.detail||'Suchabfrage fehlgeschlagen');
  if(seq!==concordanceRequest||!dialog.open)return;
  concordanceState.offset=offset;
  status.textContent=`${data.total.toLocaleString('de-DE')} Vorkommen im annotierten Bestand „${mod.title}“`;
  if(!data.total){results.append(elt('p','hint','Keine Treffer. Prüfe, ob die Wortannotationen installiert sind.'))}
  for(const hit of data.results){
    const b=elt('button','lemma-result');b.type='button';
    b.append(elt('strong','',`${hit.book} ${hit.chapter},${hit.verse}`));
    b.append(elt('span','lemma-result-form',hit.surface));
    b.append(elt('span','lemma-result-context',hit.text));
    b.addEventListener('click',async()=>{
      closeConcordance();
      await concordanceState.navigate(hit);
    });
    results.append(b);
  }
  prev.disabled=offset<=0;
  next.disabled=offset+data.results.length>=data.total;
  q('#lemma-dialog-page').textContent=data.total?`${offset+1}–${offset+data.results.length} von ${data.total}`:'Keine Treffer';
 }catch(e){
  if(seq===concordanceRequest){status.textContent='Fehler bei der Lemma-Suche: '+e.message;results.append(elt('p','hint','Die Suche konnte nicht ausgeführt werden.'))}
 }
}
function openConcordance(word,mod,navigate){
 hideTooltip();
 concordanceState={word,mod,navigate,offset:0,sortBy:'reference',direction:'asc'};
 sortSelect.value='reference';directionBtn.textContent='↑ Aufsteigend';
 q('#lemma-dialog-title').textContent='Lemma-Konkordanz · '+word.lemma;
 dialog.showModal();
 loadConcordance(0);
}
sortSelect.addEventListener('change',()=>{
 if(!concordanceState)return;
 concordanceState.sortBy=sortSelect.value;
 loadConcordance(0);
});
directionBtn.addEventListener('click',()=>{
 if(!concordanceState)return;
 concordanceState.direction=concordanceState.direction==='asc'?'desc':'asc';
 directionBtn.textContent=concordanceState.direction==='asc'?'↑ Aufsteigend':'↓ Absteigend';
 loadConcordance(0);
});
q('#lemma-dialog-close').addEventListener('click',closeConcordance);
dialog.addEventListener('close',()=>{++concordanceRequest});
prev.addEventListener('click',()=>loadConcordance(Math.max(0,concordanceState.offset-50)));
next.addEventListener('click',()=>loadConcordance(concordanceState.offset+50));

const formsDialog=q('#forms-dialog'),formsList=q('#forms-dialog-results');
let formsState=null,formsRequest=0;
function closeForms(){formsRequest++;if(formsDialog.open)formsDialog.close()}
async function loadForms(offset=0){
 if(!formsState)return;
 const seq=++formsRequest;const {word,mod}=formsState;
 const status=q('#forms-dialog-status');formsList.replaceChildren();status.textContent='Wortformen werden aus den importierten Annotationen gezählt …';
 q('#forms-dialog-prev').disabled=true;q('#forms-dialog-next').disabled=true;
 try{
  const params=new URLSearchParams({module_id:mod.id,lemma:word.lemma,limit:'50',offset:String(offset)});
  const response=await fetch('/api/morphology/forms?'+params);
  if(!response.ok){let body={};try{body=await response.json()}catch{}throw new Error(body.detail||`HTTP ${response.status}`)}
  const data=await response.json();
  if(seq!==formsRequest||!formsDialog.open)return;
  formsState.offset=offset;formsState.totalForms=data.total_forms;
  status.textContent=`${data.total_forms.toLocaleString('de-DE')} belegte Wortformen · ${data.total_occurrences.toLocaleString('de-DE')} Vorkommen in ${mod.title}`;
  if(!data.forms.length)formsList.append(elt('p','hint','Für dieses Lemma liegen in diesem Modul keine annotierten Vorkommen vor.'));
  for(const form of data.forms){
   const card=elt('article','morph-form-card');
   const top=elt('div','morph-form-top');
   const search=elt('button','morph-form-search',form.surface);search.type='button';search.title='Nach dieser exakten Wortform suchen';
   search.addEventListener('click',async()=>{const runSearch=formsState.search;closeForms();await runSearch(form.surface,'')});
   top.append(search,elt('strong','morph-form-count',`${form.occurrences.toLocaleString('de-DE')}×`));card.append(top);
   for(const analysis of form.analyses||[]){
    const grammar=analysis.grammar?.recognized?(analysis.grammar.features||[]).map(x=>`${x.name}: ${x.value}`).join(' · '):analysis.morph;
    card.append(elt('p','morph-form-grammar',`${grammar||'Keine grammatische Analyse in der Quelle angegeben.'} · ${analysis.occurrences.toLocaleString('de-DE')}×`));
    if(analysis.grammar?.recognized&&analysis.morph)card.append(elt('p','morph-form-code','Originalcode: '+analysis.morph));
   }
   if(form.books?.length){
    const detail=elt('details','morph-form-books');detail.append(elt('summary','',`Vorkommen in ${form.books.length} Büchern`));
    const list=elt('ul','');
    for(const entry of form.books){
     const row=elt('li',''),bookSearch=elt('button','morph-book-search',`${entry.book}: ${entry.occurrences.toLocaleString('de-DE')}`);
     bookSearch.type='button';bookSearch.title=`Diese Wortform in ${entry.book} suchen`;
     bookSearch.addEventListener('click',async()=>{const runSearch=formsState.search;closeForms();await runSearch(form.surface,entry.book)});
     row.append(bookSearch);list.append(row);
    }
    detail.append(list);card.append(detail);
   }
   formsList.append(card);
  }
  q('#forms-dialog-page').textContent=data.total_forms?`${offset+1}–${Math.min(offset+data.forms.length,data.total_forms)} von ${data.total_forms}`:'';
  q('#forms-dialog-prev').disabled=offset===0;q('#forms-dialog-next').disabled=offset+data.forms.length>=data.total_forms;
 }catch(e){if(seq===formsRequest){status.textContent='Die Wortformen konnten nicht geladen werden: '+e.message;formsList.append(elt('p','hint','Prüfe, ob das ausgewählte Modul Wortannotationen enthält.'))}}
}
function openForms(word,mod,search){
 formsState={word,mod,search,offset:0,totalForms:0};
 q('#forms-dialog-title').textContent='Wortformen · '+word.lemma;
 q('#forms-dialog-page').textContent='';
 formsDialog.showModal();loadForms(0);
}
q('#forms-dialog-close').addEventListener('click',closeForms);
formsDialog.addEventListener('close',()=>{formsRequest++;formsState=null});
q('#forms-dialog-prev').addEventListener('click',()=>loadForms(Math.max(0,formsState.offset-50)));
q('#forms-dialog-next').addEventListener('click',()=>loadForms(formsState.offset+50));
window.addEventListener('scroll',()=>{if(activeButton)placeTooltip(activeButton)},true);
window.amicusWordTools={renderLexicalText,enableHover,hideTooltip,openConcordance,openForms};
})();
