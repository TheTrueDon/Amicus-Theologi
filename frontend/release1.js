/* Amicus Theologi 1.0 – onboarding, complete local backup, diagnostics, safe restore */
(()=>{
'use strict';
const $=q=>document.querySelector(q);
const get=async(url,options)=>{
  const response=await fetch(url,options);
  if(!response.ok){let body={};try{body=await response.json()}catch{}
    throw new Error(body.detail||`HTTP ${response.status}`)}
  return response.json();
};
const welcome=$('#welcome-dialog');
const backup=$('#backup-dialog');
const status=$('#backup-restore-status');
async function finishWelcome(){
  try{await get('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({welcome_completed:true})})}catch{}
  if(welcome.open)welcome.close();
}
function showBackup(){if(welcome.open)welcome.close();if(!backup.open)backup.showModal();}
$('#data-center-btn').addEventListener('click',showBackup);
$('#settings-open-backup').addEventListener('click',()=>{$('#settings-dialog').close();showBackup()});
$('#backup-close').addEventListener('click',()=>backup.close());
$('#welcome-close').addEventListener('click',finishWelcome);
$('#welcome-done').addEventListener('click',finishWelcome);
$('#welcome-demo').addEventListener('click',async()=>{
  const btn=$('#welcome-demo');btn.disabled=true;btn.textContent='Installiere Mini-Beispiele …';
  try{const res=await get('/api/demo/install',{method:'POST'});
    await finishWelcome();
    await window.amicusReloadAfterDemo();
    alert('Mini-Beispiele bereit. Öffne Johannes 1,1 oder Genesis 1,1 und klicke auf ein Wort. Die Daten dienen nur der Erprobung.');
  }catch(e){alert('Die Mini-Beispiele konnten nicht installiert werden: '+e.message)}
  finally{btn.disabled=false;btn.textContent='Mini-Beispiele installieren'}
});
$('#welcome-modules').addEventListener('click',async()=>{await finishWelcome();$('#module-btn').click()});
$('#welcome-joh').addEventListener('click',async()=>{await finishWelcome();document.querySelector('#reference').value='Joh 1,1';document.querySelector('#navigate').click()});
$('#welcome-backup').addEventListener('click',async()=>{await finishWelcome();showBackup()});
$('#diagnostics-btn').addEventListener('click',async()=>{
  const root=$('#diagnostics-results');root.replaceChildren();root.textContent='Datenbank wird überprüft …';
  try{
    const d=await get('/api/diagnostics');root.replaceChildren();
    const top=document.createElement('p');top.textContent=(d.database_ok?'✓ Datenbankprüfung bestanden.':'⚠ Datenbankprüfung fehlgeschlagen. ')+` ${d.database_message}`;
    top.style.fontWeight='bold';root.append(top);
    const grid=document.createElement('div');grid.className='diagnostic-counts';
    const labels={bibeltexte:'Textausgaben',verse:'Bibelverse',annotierte_woerter:'Wortannotationen',lexika:'Lexika',lexikoneintraege:'Lexikoneinträge',projekte:'Studienprojekte',notizen:'Notizen',markierungen:'Markierungen',textvarianten:'Textkritische Lesarten'};
    for(const [key,label] of Object.entries(labels)){
      const cell=document.createElement('div');cell.className='diagnostic-count';
      const big=document.createElement('strong');big.textContent=Number(d.counts[key]).toLocaleString('de-DE');
      const small=document.createElement('small');small.textContent=label;cell.append(big,small);grid.append(cell);
    }root.append(grid);
    const extra=document.createElement('p');extra.className='hint';extra.textContent=`Speicherort: ${d.storage} · Datenbankgröße: ${d.data_size_mb} MB`;root.append(extra);
    if(!d.counts.bibeltexte){const hint=document.createElement('p');hint.className='hint';hint.textContent='Noch keine Bibeltexte installiert. Öffne den Modulkatalog oder verwende die Mini-Beispiele für einen Test.';root.append(hint)}
    for(const m of d.modules){const line=document.createElement('p');line.className='hint';line.textContent=`${m.title}: Wortdaten in ${m.annotated_verses.toLocaleString('de-DE')} von ${m.verse_count.toLocaleString('de-DE')} Versen (${m.annotation_coverage_percent.toLocaleString('de-DE')} %), ${m.annotated_words.toLocaleString('de-DE')} annotierte Wörter · ${m.provenance}`;root.append(line)}
    if(d.modules.some(m=>m.annotated_words)){const note=document.createElement('p');note.className='hint';note.textContent=d.coverage_note;root.append(note)}
  }catch(err){root.textContent='Prüfung fehlgeschlagen: '+err.message}
});
$('#backup-restore-form').addEventListener('submit',async ev=>{
  ev.preventDefault();const file=$('#backup-restore-file').files[0];if(!file)return;
  if(!confirm('Die ausgewählte Sicherung wird nach einem Neustart ALLE derzeit gespeicherten Inhalte ersetzen. Fortfahren?'))return;
  if(prompt('Zum Vorbereiten bitte WIEDERHERSTELLEN eingeben:')!=='WIEDERHERSTELLEN')return;
  const btn=$('#backup-restore-button');btn.disabled=true;status.textContent='Sicherung wird überprüft. Die aktuellen Daten werden noch nicht verändert …';
  try{
    const form=new FormData();form.set('file',file);
    const result=await get('/api/backup/restore',{method:'POST',body:form});
    status.textContent='✓ '+result.message;
    status.style.fontWeight='bold';$('#backup-restore-cancel').hidden=false;
    alert('Sicherung erfolgreich geprüft und vorgemerkt. Bitte Amicus Theologi jetzt vollständig BEENDEN (Terminal/Programm schließen) und anschließend NEU STARTEN. Bis dahin sind Datenänderungen gesperrt.');
  }catch(err){status.textContent='Wiederherstellung nicht vorbereitet: '+err.message;btn.disabled=false}
});
$('#backup-restore-cancel').addEventListener('click',async()=>{
  if(!confirm('Die vorgemerkte Wiederherstellung verwerfen? Die aktuellen Daten bleiben dadurch erhalten.'))return;
  try{const res=await get('/api/backup/restore/cancel',{method:'POST'});
    status.textContent='✓ '+res.message;$('#backup-restore-cancel').hidden=true;
    $('#backup-restore-button').disabled=false;
  }catch(err){status.textContent='Abbrechen fehlgeschlagen: '+err.message}
});
// Settings live in the SQLite DB and persist across the random local port on each start.
window.addEventListener('load',async()=>{
  try{
    const res=await get('/api/settings');
    if(!res.welcome_completed && !welcome.open)welcome.showModal();
    const diag=await get('/api/diagnostics');
    if(diag.pending_restore){$('#backup-restore-cancel').hidden=false;status.textContent='Eine geprüfte Wiederherstellung wartet auf den nächsten Neustart. Bitte Programm vollständig beenden und neu starten.';showBackup();}
  }catch{}
});
})();
