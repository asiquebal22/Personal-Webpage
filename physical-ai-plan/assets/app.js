(() => {
  'use strict';
  const KEY = 'physical-ai-fieldwork-v1';
  let state;
  try { state = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch { state = {}; }
  if (!state || typeof state !== 'object' || Array.isArray(state)) state = {};
  state.checks = state.checks && typeof state.checks === 'object' ? state.checks : {};
  state.notes = state.notes && typeof state.notes === 'object' ? state.notes : {};
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { toast('Browser storage is unavailable. Export your progress before leaving.'); } };
  function toast(message) {
    document.querySelector('.toast')?.remove();
    const el = document.createElement('div'); el.className = 'toast'; el.setAttribute('role', 'status'); el.textContent = message; document.body.append(el);
    setTimeout(() => el.remove(), 4500);
  }
  const allIDs = window.PLAN_CHECKS || [];
  const priorities = window.PLAN_PRIORITIES || {};
  const criticalIDs = allIDs.filter(id => !priorities[id] || priorities[id] === 'Critical');
  function paintProgress() {
    const count = allIDs.filter(id => state.checks[id] === true).length;
    const criticalCount = criticalIDs.filter(id => state.checks[id] === true).length;
    document.querySelectorAll('[data-progress-text]').forEach(el => el.textContent = `${criticalCount} / ${criticalIDs.length}`);
    document.querySelectorAll('[data-progress-fill]').forEach(el => { el.style.width = `${criticalIDs.length ? criticalCount / criticalIDs.length * 100 : 0}%`; });
    document.querySelectorAll('[data-all-progress-text]').forEach(el => el.textContent = `All tracked items: ${count} / ${allIDs.length}`);
    document.querySelectorAll('[data-check]').forEach(input => {
      input.checked = state.checks[input.dataset.check] === true;
      input.closest('label')?.classList.toggle('checked', input.checked);
    });
    document.querySelectorAll('[data-week-progress]').forEach(el => {
      const row=el.closest('.week-row');
      const ids=[...new Set([...row.querySelectorAll('[data-check]')].map(x=>x.dataset.check))].filter(id=>priorities[id]==='Critical');
      el.textContent=`Critical: ${ids.filter(id=>state.checks[id]===true).length} / ${ids.length}`;
    });
  }
  document.querySelectorAll('[data-check]').forEach(input => input.addEventListener('change', () => {
    state.checks[input.dataset.check] = input.checked; save(); paintProgress();
  }));
  document.querySelectorAll('[data-note]').forEach(input => {
    input.value = typeof state.notes[input.dataset.note] === 'string' ? state.notes[input.dataset.note] : '';
    input.addEventListener('input', () => { state.notes[input.dataset.note] = input.value; save(); });
  });
  function validDate(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const d = new Date(value + 'T12:00:00Z');
    return !Number.isNaN(d.getTime()) && d.toISOString().slice(0,10) === value;
  }
  function dateAt(offset) {
    const date = new Date((validDate(state.start) ? state.start : '2026-10-14') + 'T12:00:00Z');
    date.setUTCDate(date.getUTCDate() + offset); return date;
  }
  function formatDate(date, year = false) {
    return new Intl.DateTimeFormat('en-US', { month:'short', day:'numeric', ...(year ? {year:'numeric'} : {}), timeZone:'UTC' }).format(date);
  }
  function paintDates() {
    document.querySelectorAll('[data-week-date]').forEach(el => {
      const n = Number(el.dataset.weekDate); el.textContent = `${formatDate(dateAt((n - 1) * 7))} – ${formatDate(dateAt((n - 1) * 7 + 6), n === 12)}`;
    });
    document.querySelectorAll('[data-outreach-date]').forEach(el => el.textContent = formatDate(dateAt(42), true));
    document.querySelectorAll('[data-plan-range]').forEach(el => el.textContent = `${formatDate(dateAt(0), true)} – ${formatDate(dateAt(83), true)}`);
    document.querySelectorAll('[data-buffer-range]').forEach(el => el.textContent = `${formatDate(dateAt(84))} – ${formatDate(dateAt(91), true)}`);
    const today = new Date();
    const parts = new Intl.DateTimeFormat('en-US',{timeZone:'America/Phoenix',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(today);
    const get = type => parts.find(p => p.type === type).value;
    const day = new Date(`${get('year')}-${get('month')}-${get('day')}T12:00:00Z`);
    const week = Math.max(1, Math.min(12, Math.floor((day - dateAt(0)) / 604800000) + 1));
    document.querySelectorAll('[data-current-week-link]').forEach(el => { el.href = `week-${String(week).padStart(2,'0')}.html`; el.textContent = `Open week ${week} →`; });
  }
  const startInput = document.querySelector('#planStart');
  if (startInput) {
    startInput.value = validDate(state.start) ? state.start : '2026-10-14';
    startInput.addEventListener('change', () => { if (validDate(startInput.value)) {state.start=startInput.value;save();paintDates();toast('Dates updated. Outreach remains in week 7.');} });
  }
  document.querySelectorAll('[data-export]').forEach(button => button.addEventListener('click', () => {
    const data = JSON.stringify({ schema:1, exported:new Date().toISOString(), ...state }, null, 2);
    const url = URL.createObjectURL(new Blob([data], {type:'application/json'}));
    const a = document.createElement('a'); a.href=url; a.download='physical-ai-progress.json'; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  }));
  document.querySelectorAll('[data-import]').forEach(button => button.addEventListener('click', () => document.querySelector('#importFile').click()));
  document.querySelector('#importFile')?.addEventListener('change', async event => {
    const file=event.target.files[0]; if(!file)return;
    try {
      if(file.size>2000000)throw new Error('File too large');
      const data=JSON.parse(await file.text());
      if(data.schema!==1 || !data.checks || typeof data.checks!=='object' || Array.isArray(data.checks))throw new Error('Invalid export');
      state.checks=Object.fromEntries(allIDs.map(id=>[id,data.checks[id]===true]));
      if(validDate(data.start))state.start=data.start;
      state.notes=data.notes && typeof data.notes==='object' && !Array.isArray(data.notes) ? Object.fromEntries(Object.entries(data.notes).filter(([key,value])=>typeof value==='string' && value.length<100000)) : {};
      save();paintProgress();paintDates();
      document.querySelectorAll('[data-note]').forEach(el=>el.value=state.notes[el.dataset.note]||'');
      if(startInput)startInput.value=state.start||'2026-10-14';
      toast('Progress imported.');
    } catch { toast('That file is not a valid progress export.'); }
    event.target.value='';
  });
  document.querySelector('.mobile-menu')?.addEventListener('click', event => {
    const open=document.querySelector('.sidebar').classList.toggle('open'); event.currentTarget.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('click', event => {
    if(window.innerWidth<=800 && !event.target.closest('.sidebar,.mobile-menu')) {document.querySelector('.sidebar')?.classList.remove('open');document.querySelector('.mobile-menu')?.setAttribute('aria-expanded','false');}
  });
  document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll('[data-filter]').forEach(el=>{const selected=el===button;el.classList.toggle('active',selected);el.setAttribute('aria-pressed',String(selected));});
    document.querySelectorAll('[data-category]').forEach(el=>el.classList.toggle('hidden',button.dataset.filter!=='All'&&el.dataset.category!==button.dataset.filter));
  }));
  function revealLinkedPaper() {
    let id;
    try { id=decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
    const paper=document.getElementById(id);
    if(!paper || paper.tagName!=='DETAILS') return;
    if(paper.classList.contains('hidden') || paper.closest('[data-category]')?.classList.contains('hidden')) {
      document.querySelectorAll('[data-category]').forEach(el=>el.classList.remove('hidden'));
      document.querySelectorAll('[data-filter]').forEach(el=>{const selected=el.dataset.filter==='All';el.classList.toggle('active',selected);el.setAttribute('aria-pressed',String(selected));});
    }
    paper.open=true;
    paper.scrollIntoView({block:'start'});
  }
  window.addEventListener('hashchange',revealLinkedPaper);
  revealLinkedPaper();
  const dialog=document.querySelector('#searchDialog'), query=document.querySelector('#searchQuery'), results=document.querySelector('#searchResults');
  function renderSearch() {
    const terms=query.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const matches=(window.PLAN_SEARCH||[]).filter(x=>terms.every(t=>(x.title+' '+x.text+' '+x.kind).toLowerCase().includes(t))).slice(0,18);
    results.replaceChildren();
    if(!matches.length){const p=document.createElement('p');p.className='search-empty';p.textContent='No matches. Try PPO, obstruction, world model or evaluation.';results.append(p);return;}
    matches.forEach(item=>{const a=document.createElement('a');a.href=item.href;a.className='search-result';a.addEventListener('click',()=>dialog.close());const k=document.createElement('span');k.textContent=item.kind;const t=document.createElement('strong');t.textContent=item.title;const p=document.createElement('p');p.textContent=item.text.slice(0,165);a.append(k,t,p);results.append(a);});
  }
  function openSearch(){dialog.showModal();renderSearch();query.focus();}
  document.querySelectorAll('[data-search]').forEach(el=>el.addEventListener('click',openSearch));
  document.querySelector('[data-close-search]')?.addEventListener('click',()=>dialog.close());
  query?.addEventListener('input',renderSearch);
  dialog?.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  document.addEventListener('keydown',event=>{if((event.metaKey||event.ctrlKey)&&event.key==='k'){event.preventDefault();openSearch();}});
  document.querySelectorAll('[data-print]').forEach(el=>el.addEventListener('click',()=>window.print()));
  let priorOpen=[];
  window.addEventListener('beforeprint',()=>{priorOpen=[...document.querySelectorAll('details')].map(x=>[x,x.open]);priorOpen.forEach(([x])=>x.open=true);});
  window.addEventListener('afterprint',()=>priorOpen.forEach(([x,open])=>x.open=open));
  paintProgress();paintDates();
})();
