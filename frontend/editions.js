"use strict";
/* v1.0.5 – no framework, no external CDN, preferences stored in existing settings table. */
(() => {
 const $ = (sel) => document.querySelector(sel);
 const node = (tag, cls, content) => {
   const result = document.createElement(tag);
   if (cls) result.className = cls;
   if (content !== undefined) result.textContent = content;
   return result;
 };
 const isVisible = (id) => {
   const ids = settings.display_module_ids;
   return !Array.isArray(ids) || ids.includes('*') || ids.includes(id);
 };
 const ordered = (list) => {
   const order = Array.isArray(settings.display_module_order) ? settings.display_module_order : [];
   const positions = new Map(order.map((id, i) => [id, i]));
   return [...list].sort((a, b) => {
     const i = positions.get(a.id), j = positions.get(b.id);
     if (i !== undefined && j !== undefined) return i - j;
     if (i !== undefined) return -1;
     if (j !== undefined) return 1;
     return a.title.localeCompare(b.title, 'de');
   });
 };
 const selectable = () => ordered(modules);
 function paintChips() {
   const root = $('#edition-chips');
   if (!root) return;
   root.replaceChildren();
   const shown = selectable().filter(m => isVisible(m.id) && isShown(m.language));
   const total = modules.length;
   $('#edition-count').textContent = `${shown.length} von ${total} sichtbar`;
   if (!modules.length) {
     root.append(node('span', 'hint', 'Noch keine Bibelausgaben installiert.'));
     return;
   }
   if (!shown.length) {
     root.append(node('span', 'hint', 'Keine Ausgabe ausgewählt.'));
   }
   for (const m of shown) {
     const btn = node('button', 'edition-chip', m.title + ' ×');
     btn.type = 'button';
     btn.title = m.title + ' ausblenden';
     btn.setAttribute('aria-label', m.title + ' ausblenden');
     btn.addEventListener('click', () => selectIds(selectable().filter(x => isVisible(x.id) && x.id !== m.id).map(x => x.id)));
     root.append(btn);
   }
   if (shown.length < total) {
     const more = node('button', 'edition-chip edition-add', '+ Weitere Ausgaben');
     more.type = 'button';
     more.addEventListener('click', openChooser);
     root.append(more);
   }
 }
 async function selectIds(ids) {
   const normalized = [...new Set(ids)].filter(id => modules.some(m => m.id === id));
   const langPatch = {};
   for (const id of normalized) {
     const language=modules.find(m=>m.id===id)?.language;
     const flag={'grc':'show_greek','de':'show_german','la':'show_latin'}[language];
     if (flag && settings[flag]===false) langPatch[flag]=true;
   }
   if (Object.keys(langPatch).length) {
     for (const [flag,value] of Object.entries(langPatch)) {
       const tag={'show_greek':'greek','show_german':'german','show_latin':'latin'}[flag];
       $('#show-'+tag).checked=value;
     }
   }
   save({display_module_ids:normalized,...langPatch});
   if (view) render();
   paintChoices();
 }
 function orderList() {
   return selectable().map(m => m.id);
 }
 function move(id, direction) {
   const order = orderList();
   const from = order.indexOf(id), to = from + direction;
   if (from < 0 || to < 0 || to >= order.length) return;
   [order[from], order[to]] = [order[to], order[from]];
   save({display_module_order: order});
   if (view) render();
   paintChoices();
 }
 function paintChoices() {
   const root = $('#edition-choices');
   if (!root) return;
   const query = $('#edition-filter').value.trim().toLocaleLowerCase('de');
   root.replaceChildren();
   for (const m of selectable()) {
     if (query && !`${m.title} ${m.id} ${m.language}`.toLocaleLowerCase('de').includes(query)) continue;
     const row = node('div','edition-choice');
     const label = node('label','edition-choice-label');
     const input = node('input');
     input.type = 'checkbox';
     input.checked = isVisible(m.id);
     input.setAttribute('aria-label', m.title + ' anzeigen');
     input.addEventListener('change', async () => {
       const ids = selectable().filter(x => isVisible(x.id)).map(x => x.id);
       const next = input.checked ? [...ids, m.id] : ids.filter(id => id !== m.id);
       await selectIds(next);
     });
     const labelText = node('span');
     labelText.append(node('strong','',m.title), node('small','',m.id + ' · ' + m.language + ' · ' + m.verse_count + ' Verse'));
     label.append(input,labelText);
     const actions = node('div','edition-order-buttons');
     for (const [text, direction, title] of [['↑',-1,'Nach oben'],['↓',1,'Nach unten']]) {
       const b = node('button','btn',text);b.type='button';b.title=title + ': ' + m.title;
       b.setAttribute('aria-label',title + ': ' + m.title);
       const arr = selectable();const index = arr.findIndex(x => x.id === m.id);
       b.disabled=direction===-1 ? index===0 : index===arr.length-1;
       b.addEventListener('click', () => move(m.id,direction));actions.append(b);
     }
     row.append(label,actions);root.append(row);
   }
   if (!root.children.length) root.append(node('p','hint',modules.length?'Keine Ausgabe entspricht dem Suchbegriff.':'Noch keine Textausgaben installiert.'));
   const shown=selectable().filter(m=>isVisible(m.id)).length;
   $('#edition-dialog-status').textContent = `${shown} von ${modules.length} Ausgaben ausgewählt. Änderungen werden automatisch gespeichert.`;
 }
 function openChooser() {
   paintChoices();
   if (!$('#edition-dialog').open) $('#edition-dialog').showModal();
 }
 function enable(id) {
   if (!modules.some(m => m.id === id)) return;
   if (!isVisible(id)) save({display_module_ids:[...new Set([...selectable().filter(m=>isVisible(m.id)).map(m=>m.id),id])]});
   if (view) render();
   paintChoices();
 }
 function refresh() {paintChips();paintChoices();}
 const sourceArea=$('#bible-catalog-section');
 function openCatalog() {
   if (!$('#module-dialog').open) $('#module-dialog').showModal();
   refreshBibleCatalog();
   sourceArea.scrollIntoView({block:'start'});
 }
 async function refreshBibleCatalog() {
   const root = $('#bible-catalog-list');root.replaceChildren();
   try {
     const data=await api('/api/bible-catalog');
     for (const m of data) {
       const card=node('div','bible-edition-card');
       const text=node('div','bible-edition-info');
       text.append(node('strong','',m.title), node('span','',m.detail));
       text.append(node('small','',m.id+' · '+m.status+' · '+m.license));
       const link=node('a','edition-source-link','Originalquelle ↗');
       link.href=m.source_url;link.target='_blank';link.rel='noopener noreferrer';text.append(link);
       const b=node('button',m.installed?'btn':'btn primary',m.installed?'Installiert':'Installieren');
       b.type='button';b.disabled=m.installed;
       b.addEventListener('click',async () => {
         b.disabled=true;b.textContent='Installation läuft …';
         $('#bible-catalog-status').textContent=`${m.title} wird heruntergeladen und geprüft. Bitte Dialog geöffnet lassen …`;
         try {
           const res=await api('/api/bible-catalog/'+encodeURIComponent(m.id)+'/install',{method:'POST'});
           $('#bible-catalog-status').textContent=`${res.title} installiert (${res.verses.toLocaleString('de')} Verse). Die Ausgabe kann jetzt in der Textansicht ausgewählt werden.`;
           await refreshModules();enable(res.module_id);await go(view.book,view.chapter,activeVerse);
           await refreshBibleCatalog();
         } catch(err) {
           $('#bible-catalog-status').textContent='Installation fehlgeschlagen: '+err.message;
           b.disabled=false;b.textContent='Erneut versuchen';
         }
       });
       card.append(text,b);root.append(card);
     }
   }catch(err){root.append(node('p','hint','Bibelausgaben-Katalog nicht verfügbar: '+err.message));}
 }
 $('#bible-catalog-btn').addEventListener('click',openCatalog);
 $('#choose-editions').addEventListener('click',openChooser);
 $('#edition-dialog-close').addEventListener('click',()=>$('#edition-dialog').close());
 $('#edition-done').addEventListener('click',()=>$('#edition-dialog').close());
 $('#edition-install').addEventListener('click',()=>{$('#edition-dialog').close();openCatalog()});
 $('#edition-filter').addEventListener('input',paintChoices);
 $('#edition-all').addEventListener('click',()=>selectIds(modules.map(m=>m.id)));
 $('#edition-none').addEventListener('click',()=>selectIds([]));
 $('#edition-german').addEventListener('click',()=>selectIds(modules.filter(m=>m.language==='de').map(m=>m.id)));
 $('#edition-original').addEventListener('click',()=>selectIds(modules.filter(m=>['grc','he'].includes(m.language)).map(m=>m.id)));
 $('#module-btn').addEventListener('click',refreshBibleCatalog);
 $('#add-module-left').addEventListener('click',refreshBibleCatalog);
 window.amicusEditions = {isVisible,ordered,refresh,enable,openChooser,openCatalog};
})();
