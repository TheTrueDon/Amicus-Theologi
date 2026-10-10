/* Offline-only client-side full-text index for the Amicus Theologi manual.
   No external service, cookies, analytics, or network requests. */
(()=>{
  'use strict';
  const input=document.getElementById('manual-search');
  const results=document.getElementById('search-results');
  const clear=document.getElementById('clear-search');
  const chapters=[...document.querySelectorAll('.help-chapter')];
  const links=[...document.querySelectorAll('.contents a')];
  const normalize=text=>(text||'').toLocaleLowerCase('de-DE').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const textIndex=chapters.map(node=>({
    id:node.id,
    title:node.querySelector('h1,h2')?.textContent.trim()||node.id,
    text:node.textContent.replace(/\s+/g,' ').trim(),
    keywords:node.getAttribute('data-keywords')||''
  }));
  const sortResults=query=>{
    const terms=normalize(query).split(/\s+/).filter(Boolean);
    if(!terms.length)return [];
    return textIndex.map(item=>{
      const title=normalize(item.title),body=normalize(item.text),tags=normalize(item.keywords);
      if(!terms.every(term=>title.includes(term)||body.includes(term)||tags.includes(term)))return null;
      let score=0;
      for(const term of terms)score+=(title.includes(term)?30:0)+(tags.includes(term)?15:0)+(body.includes(term)?1:0);
      const first=body.indexOf(terms[0]);
      const start=Math.max(0,first-68),end=Math.min(item.text.length,first+120);
      // normalized positions can differ for accents, but snippets are purely informative
      return {...item,score,snippet:(start?'…':'')+item.text.slice(start,end)+(end<item.text.length?'…':'')};
    }).filter(Boolean).sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title,'de'));
  };
  function render(){
    const q=input.value.trim();clear.hidden=!q;results.replaceChildren();
    if(!q)return;
    const matched=sortResults(q),top=matched.slice(0,14);
    const count=document.createElement('p');count.className='search-summary';count.textContent=matched.length===1?'1 Kapitel gefunden':`${matched.length} Kapitel gefunden`;results.append(count);
    if(!matched.length){const p=document.createElement('p');p.className='search-empty';p.textContent='Nichts gefunden. Versuche z. B. „Lemma“, „Aorist“ oder „Sicherung“.';results.append(p);return}
    for(const item of top){const a=document.createElement('a');a.className='hit-row';a.href='#'+item.id;
      const head=document.createElement('strong');head.textContent=item.title;
      const snippet=document.createElement('span');snippet.textContent=item.snippet;
      a.append(head,snippet);a.addEventListener('click',()=>{input.blur();document.getElementById(item.id)?.scrollIntoView()});results.append(a)}
  }
  input.addEventListener('input',render);
  clear.addEventListener('click',()=>{input.value='';render();input.focus()});
  document.addEventListener('keydown',e=>{
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){
      e.preventDefault();input.focus();input.select();return
    }
    if(e.key==='Escape'&&document.activeElement===input){input.value='';render();input.blur()}
  });
  document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
    const value=button.dataset.copy;const old=button.textContent;
    try{
      if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(value);
      else{const area=document.createElement('textarea');area.value=value;area.style.position='fixed';area.style.left='-10000px';document.body.append(area);area.select();if(!document.execCommand('copy'))throw new Error('Clipboard unavailable');area.remove()}
      button.textContent='Kopiert ✓';
    }catch{button.textContent='Bitte Text markieren'}
    setTimeout(()=>button.textContent=old,1800);
  }));
  document.getElementById('print').addEventListener('click',()=>window.print());
  const theme=document.getElementById('theme');
  try{document.documentElement.dataset.theme=localStorage.getItem('amicus_help_theme')||'light'}catch{}
  theme.addEventListener('click',()=>{
    const mode=document.documentElement.dataset.theme==='dark'?'light':'dark';
    document.documentElement.dataset.theme=mode;
    try{localStorage.setItem('amicus_help_theme',mode)}catch{}
  });
  function markActive(){const hash=location.hash||'#start';for(const a of links)a.classList.toggle('active',a.getAttribute('href')===hash)}
  window.addEventListener('hashchange',markActive);markActive();
  if(new URLSearchParams(location.search).has('q')){input.value=new URLSearchParams(location.search).get('q').slice(0,120);render()}
})();
