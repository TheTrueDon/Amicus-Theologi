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
let allSourcesRunning=false;
async function finishWelcome(){
  try{await get('/api/settings',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({welcome_completed:true})})}catch{}
  if(welcome.open)welcome.close();
}
function showBackup(){if(welcome.open)welcome.close();if(!backup.open)backup.showModal();}
$('#data-center-btn').addEventListener('click',showBackup);
$('#settings-open-backup').addEventListener('click',()=>{$('#settings-dialog').close();showBackup()});
$('#backup-close').addEventListener('click',()=>backup.close());
function setAllSourcesRunning(value){
  allSourcesRunning=value;
  $('#welcome-install-all').disabled=value;
  $('#welcome-close').disabled=value;
  $('#welcome-done').disabled=value;
  for(const id of ['welcome-demo','welcome-modules','welcome-joh','welcome-backup'])$('#'+id).disabled=value;
  $('#install-all-spinner').hidden=!value;
}
function paintAllSourcesProgress(data){
  const panel=$('#install-all-progress');panel.hidden=false;
  const total=Number(data.total)||0,done=Number(data.completed)||0;
  $('#install-all-bar').value=Number(data.progress)||0;
  $('#install-all-count').textContent=total
    ?`${done.toLocaleString('de-DE')} von ${total.toLocaleString('de-DE')} Quellen · ${Number(data.progress)||0} %`
    :'Keine neuen Quellen erforderlich';
  $('#install-all-phase').textContent=data.current_title
    ?`${data.phase} ${data.current_title}`:data.phase;
  const errors=$('#install-all-errors');errors.replaceChildren();
  for(const item of data.errors||[]){
    const line=document.createElement('li');line.textContent=`${item.title}: ${item.message}`;errors.append(line);
  }
  $('#install-all-summary').textContent=data.done
    ?`Neu installiert: ${Number(data.installed||0).toLocaleString('de-DE')} · Bereits vorhanden: ${Number(data.skipped||0).toLocaleString('de-DE')} · Fehler: ${(data.errors||[]).length.toLocaleString('de-DE')} · Externe Verweise: ${(data.external_titles||[]).join(', ')||'keine'}.`
    :`Bereits vorhanden: ${Number(data.skipped||0).toLocaleString('de-DE')} · Einzelne große Quellen können länger laden; der aktuelle Titel bleibt hier sichtbar.`;
}
async function installAllSources(){
  const button=$('#welcome-install-all');setAllSourcesRunning(true);
  $('#install-all-progress').hidden=false;$('#install-all-errors').replaceChildren();
  $('#install-all-count').textContent='Installationsauftrag wird vorbereitet …';
  $('#install-all-phase').textContent='Kataloge und mitgelieferte Pakete werden geprüft.';
  $('#install-all-summary').textContent='Bereits installierte Quellen werden übersprungen.';
  try{
    const started=await get('/api/initial-install/start',{method:'POST'}),jobId=started.id;
    let result=started;
    while(!result.done){
      paintAllSourcesProgress(result);
      await new Promise(resolve=>setTimeout(resolve,900));
      result=await get('/api/initial-install/'+encodeURIComponent(jobId));
    }
    paintAllSourcesProgress(result);setAllSourcesRunning(false);
    if(result.errors?.length){button.disabled=false;button.textContent='Fehlerhafte Quellen erneut versuchen';}
    else{button.disabled=true;button.textContent='Alle verfügbaren Quellen sind installiert';}
    try{await window.amicusReloadAfterDemo()}catch{}
  }catch(error){
    $('#install-all-phase').textContent='Installation konnte nicht gestartet oder abgefragt werden: '+error.message;
    setAllSourcesRunning(false);button.disabled=false;button.textContent='Erneut versuchen';
  }
}
$('#welcome-install-all').addEventListener('click',installAllSources);
$('#welcome-close').addEventListener('click',()=>{if(!allSourcesRunning)finishWelcome()});
$('#welcome-done').addEventListener('click',()=>{if(!allSourcesRunning)finishWelcome()});
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
