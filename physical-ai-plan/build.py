#!/usr/bin/env python3
"""Build the dependency-free static learning site. Run: python3 build.py."""
from pathlib import Path
from html import escape
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content"))
from foundations import MODULES, RESOURCES
from labs import LABS
from weeks import WEEKS
from research import PROJECT_SECTIONS, PAPERS
from interviews import QUESTIONS, CAREER_PHASES, CODING_PRACTICE
from literature import CANON, CORE_AUTHORS, READING_SCHEDULE, MODEL_FAMILIES, PRACTICE
from priorities import (PRIORITIES, PRIORITY_RANK, PRIORITY_CLASS, PRIORITY_HELP,
                        paper_key, paper_priority, lab_priority, LAB_STEP_PRIORITY,
                        PRACTICE_STEP_PRIORITY, PROJECT_CHECKLIST, QUESTIONS as RESEARCH_QUESTIONS)

E = lambda x: escape(str(x), quote=True)
NAV = [("index.html","Home","00"),("roadmap.html","Weekly checklist","01"),("theory.html","Theory & foundations","02"),("implementation.html","Implementation labs","03"),("project-checklist.html","Research checklist","04"),("research.html","Protocol","04"),("reading.html","Reading room","05"),("interviews.html","Interview preparation","06"),("resources.html","Resource library","07")]
PAPER_KEYS = list(dict.fromkeys(paper_key(p[0]) for p in CANON + PAPERS))
CHECK_META = {}
for w in WEEKS:
    for i in range(len(w['outputs'])): CHECK_META[f'week-{w["n"]}-output-{i}'] = 'Critical'
    for i in range(len(w['days'])): CHECK_META[f'week-{w["n"]}-day-{i}'] = 'Critical'
for m in MODULES: CHECK_META['module-'+m['id']] = 'Critical'
for l in LABS:
    CHECK_META['lab-'+l['id']] = lab_priority(l['id'])
    for i in range(len(l['steps'])): CHECK_META[f'lab-{l["id"]}-step-{i}'] = LAB_STEP_PRIORITY.get((l['id'],i),lab_priority(l['id']))
for i in range(6): CHECK_META[f'release-{i}'] = 'Critical'
for key in PAPER_KEYS: CHECK_META['paper-'+key] = paper_priority(key)
for p in PRACTICE:
    CHECK_META[p['id']] = 'Critical'
    for i,priority in enumerate(PRACTICE_STEP_PRIORITY[p['id']]): CHECK_META[f'{p["id"]}-step-{i}'] = priority
for _,_,items in PROJECT_CHECKLIST:
    for key,_,priority in items: CHECK_META['project-'+key] = priority
CHECKS = list(CHECK_META)
SEARCH = []
LAB_BY_ID = {x["id"]: x for x in LABS}

def ul(items): return '<ul>'+''.join(f'<li>{E(x)}</li>' for x in items)+'</ul>'
def ol(items): return '<ol>'+''.join(f'<li>{E(x)}</li>' for x in items)+'</ol>'
def refs(keys):
    return '<div class="resource-links">'+''.join(f'<a class="resource-link" href="{E(RESOURCES[k][1])}" target="_blank" rel="noopener">{E(RESOURCES[k][0])}</a>' for k in keys)+'</div>'
def paper_links(keys):
    canon_keys = {p[0] for p in CANON}
    return '<ul class="paper-assignments">'+''.join(f'<li>{check("paper-"+paper_key(k),RESOURCES[k][0])}<a href="{("reading-foundations.html#paper-"+E(k)) if k in canon_keys else E(RESOURCES[k][1])}">Reading brief / paper ↗</a></li>' for k in sorted(keys,key=lambda k:PRIORITY_RANK[paper_priority(k)]))+'</ul>'
def badge(priority): return f'<span class="priority priority-{PRIORITY_CLASS[priority]}">{E(priority)}</span>'
def priority_legend(): return '<div class="priority-guide">'+''.join(f'<p>{badge(p)} {E(PRIORITY_HELP[p])}</p>' for p in PRIORITIES)+'</div>'
def priority_filters(): return '<div class="filter-row" aria-label="Filter by priority">'+''.join(f'<button class="filter{(" active" if p=="All" else "")}" data-filter="{p}" aria-pressed="{str(p=="All").lower()}">{p}</button>' for p in ('All',)+PRIORITIES)+'</div>'
def check(id, text):
    priority=CHECK_META[id]
    return f'<label class="check"><input type="checkbox" data-check="{E(id)}"><span>{E(text)} {badge(priority)}</span></label>'
def tinycheck(id): return f'<label class="tiny-check"><input type="checkbox" data-check="{E(id)}">Completed</label>'
def heading(kicker,title,description): return f'<div class="page-heading"><div class="eyebrow">{E(kicker)}</div><h1>{E(title)}</h1><p class="lead">{E(description)}</p></div>'
def section(id,title,body): return f'<section id="{E(id)}"><h2>{E(title)}</h2>{body}</section>'
def toc(items): return '<aside class="toc" aria-label="On this page"><h3>On this page</h3>'+''.join(f'<a href="#{E(id)}">{E(title)}</a>' for id,title in items)+'</aside>'
def article(sections): return '<div class="article-layout"><article class="article">'+''.join(section(*s) for s in sections)+'</article>'+toc([(s[0],s[1]) for s in sections])+'</div>'
def hours(w):
    labels=['Theory','Coding labs','Research','Interview / career']
    bar='<div class="hours-bar" aria-hidden="true">'+''.join(f'<span style="width:{h/42*100:.3f}%"></span>' for h in w['hours'])+'</div>'
    legend='<div class="hours-legend">'+''.join(f'<span><b>{h} h</b> {label}</span>' for h,label in zip(w['hours'],labels))+'</div>'
    return bar+legend
def weekcard(w):
    n=w['n']
    readings=READING_SCHEDULE[n]
    papers=paper_links(readings['deep']+readings['survey']) if w['papers'] else '<p>No new assigned paper. Use targeted review.</p>'
    coding=''.join(check('lab-'+key,LAB_BY_ID[key]['title'])+f'<a class="small" href="lab-{LAB_BY_ID[key]["number"]}.html">Instructions →</a>' for key in w['labs']) or '<p>Apply the existing implementation to the research experiment.</p>'
    outputs=''.join(check(f'week-{n}-output-{i}',t) for i,t in enumerate(w['outputs']))
    return f'<article class="week-row" data-category="{E(w["phase"])}"><div class="week-index"><strong>Week {n:02}</strong><span class="week-date" data-week-date="{n}"></span><span class="tag">{E(w["phase"])}</span><span class="small" data-week-progress="{n}"></span></div><div><h2><a href="week-{n:02}.html">{E(w["title"])}</a></h2><p>{E(w["aim"])}</p>{hours(w)}<div class="week-work"><section><h3>Read</h3>{papers}</section><section><h3>Implement</h3>{coding}</section></div><h3>Produce</h3>{outputs}<p><a href="week-{n:02}.html">Daily checklist and decision gate →</a></p></div></article>'
def write(name,title,body,active,kind="Guide",description=""):
    navigation=''
    for file,label,number in NAV:
        aria=' aria-current="page"' if file==active else ''
        selected=' active' if file==active else ''
        navigation+=f'<a class="nav-link{selected}" href="{file}"{aria}>{label}</a>'
    text=re.sub('<[^>]+>',' ',body);text=re.sub(r'\s+',' ',text).strip()
    SEARCH.append(dict(title=title,kind=kind,href=name,text=description or text[:450]))
    critical_total=sum(p=='Critical' for p in CHECK_META.values())
    doc=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{E(description or 'Physical AI study and research checklist.')}"/><title>{E(title)} · Physical AI study plan</title><link rel="stylesheet" href="assets/style.css"><script src="assets/search-index.js" defer></script><script src="assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="header-row"><a class="site-title" href="index.html">Physical AI · Study &amp; research</a><div class="header-controls"><button class="small-btn" data-search>Search</button><button class="small-btn" data-export>Export progress</button><button class="small-btn" data-import>Import</button><button class="small-btn" data-print>Print</button></div></div><div class="program-progress"><span>Critical items: <strong data-progress-text>0 / {critical_total}</strong></span><div class="progress-track"><div class="progress-fill" data-progress-fill></div></div><span class="muted" data-all-progress-text>All tracked items: 0 / {len(CHECKS)}</span></div><p class="small muted">Checkboxes and notes are saved in this browser. Export to back up or move devices.</p></header>
<nav class="site-nav" aria-label="Main navigation">{navigation}</nav><main id="main" class="content">{body}<footer class="footer">Physical AI study plan · Source review: October 14, 2026 · <a href="README.md">About this plan</a></footer></main>
<dialog id="searchDialog" aria-label="Search the program"><div class="search-head"><input id="searchQuery" type="search" aria-label="Search topics, labs and weeks" placeholder="Search a paper, concept or task"><button data-close-search>Close</button></div><div class="search-results" id="searchResults"></div></dialog><input type="file" id="importFile" accept="application/json" hidden></body></html>'''
    (ROOT/name).write_text(doc,encoding='utf-8')

def build_overview():
    body=heading('Plan home','Physical AI study and research plan','Twelve weeks of foundations, implementation, research and interview preparation. Use the checkboxes to track completed work; follow the priority labels when time is tight.')
    body+='<p><strong>Schedule:</strong> <span data-plan-range></span> · Up to 42 core hours/week.<br><strong>Outreach:</strong> starts in Week 7, <span data-outreach-date></span>.</p>'
    body+='<section><h2>Week 1 deliverables</h2>'+''.join(check(f'week-1-output-{i}',t) for i,t in enumerate(WEEKS[0]['outputs']))+'<p><a href="week-01.html">Open the daily checklist →</a></p></section>'
    body+=priority_legend()
    body+='<p><a class="button secondary" href="roadmap.html" data-current-week-link>Open the current week →</a> <a class="button secondary" href="project-checklist.html">Research checklist →</a></p>'
    body+='<section><h2>Use the plan</h2><ol><li>Open your week and complete its critical work first.</li><li>Use the paper and coding checklists; a survey-level reading can still be critical.</li><li>Take on time-permitting work only after the critical work is on track. Optional extensions do not block completion.</li><li>Record evidence: an explanation, a runnable implementation, an evaluated result or a diagnosed failure.</li></ol></section>'
    body+='<section><h2>Plan contents</h2><div class="table-wrap"><table><thead><tr><th>Section</th><th>What to work through</th></tr></thead><tbody>'
    contents=[('roadmap.html','Weekly schedule','Daily actions, deliverables, reading and decision gates.'),('reading-foundations.html','Papers and priorities','Foundational papers, modern model families and reliability methods; each with a checkbox.'),('theory.html','Theory','Derivations, interview questions and mastery checks.'),('implementation.html','Coding','Twelve labs with step checkboxes and five supplied teaching scripts.'),('model-landscape.html','World models and VLAs','Cosmos, OpenVLA/OFT, openpi, DreamZero and model-interface practice.'),('project-checklist.html','Research checklist','Questions → study → setup → data → models → experiments → gates → release.'),('research.html','Research protocol','Assumptions, learning loop, baselines, splits, budgets and metrics.'),('reading.html','Closest related work','Evidence boundaries and the novelty comparison.'),('interviews.html','Interview preparation','Technical questions, coding practice and outreach from Week 7.')]
    body+=''.join(f'<tr><td><a href="{file}">{label}</a></td><td>{desc}</td></tr>' for file,label,desc in contents)+'</tbody></table></div></section>'
    body+='<section><h2>Research question</h2><p>When an unseen obstruction defeats a robot policy, can imagined policy updates improve executed recovery, and can a small, actively selected budget of real trials correct the model more effectively than random trials?</p><p>Start with one task and a feasible action-conditioned model. Compare policy adaptation with replanning; select claims from measured outcomes.</p></section>'
    body+='<section><h2>Set your start date</h2><div class="settings-row"><label for="planStart">Program start</label><input type="date" id="planStart" value="2026-10-14"></div><p class="small muted">Six seven-hour work sessions are the weekly capacity. Reading and model practice fit inside it; optional work replaces other review. A seventh day is flexible. Calendar buffer: <span data-buffer-range></span>.</p></section>'
    write('index.html','Physical AI study and research plan',body,'index.html','Overview','A practical checklist with critical, time-permitting and optional study, coding and research. Outreach begins in week 7.')

def build_roadmap():
    body=heading('01 / Weekly schedule','Weekly study and implementation checklist','Read → implement → produce. Complete critical items first. The 42-hour allocation is a capacity limit, including selected time-permitting work.')
    body+='<div class="callout"><strong>Your outreach boundary:</strong> private preparation during weeks 1–6. Researcher conversations, applications and follow-ups begin in week 7: <strong data-outreach-date></strong>.</div>'
    body+='<p><a href="project-checklist.html">Research checklist</a> · <a href="reading-foundations.html#catalog">All papers by priority</a></p>'+priority_legend()
    body+='<div class="filter-row" aria-label="Filter weeks">'+''.join(f'<button class="filter{(" active" if t=="All" else "")}" data-filter="{t}" aria-pressed="{str(t=="All").lower()}">{t}</button>' for t in ['All','Foundations','Method','Evidence','Release'])+'</div><div class="week-list">'+''.join(weekcard(w) for w in WEEKS)+'</div>'
    body+='<div class="section-head"><h2>The complete time ledger</h2></div><div class="table-wrap"><table><thead><tr><th>Week</th><th>Theory</th><th>Labs</th><th>Research</th><th>Interview / career</th><th>Total</th></tr></thead><tbody>'+''.join(f'<tr><td><a href="week-{w["n"]:02}.html">{w["n"]:02}</a></td>'+''.join(f'<td>{h} h</td>' for h in w['hours'])+'<td>42 h</td></tr>' for w in WEEKS)+'</tbody></table></div>'
    body+='<p class="muted small">Scope and timeboxes are adjustable at development gates. Reallocate hours when you already demonstrate mastery; use optional labs as replacements, not additional mandatory work.</p>'
    write('roadmap.html','Weekly roadmap',body,'roadmap.html')
    for w in WEEKS:
        n=w['n']; body=f'<div class="breadcrumb"><a href="roadmap.html">Weekly roadmap</a> / Week {n:02}</div>'+heading(f'Week {n:02} / {w["phase"]}',w['title'],w['aim'])
        body+=f'<div class="card"><div class="card-top"><span data-week-date="{n}" class="week-date"></span><span class="tag">42 core hours</span></div>{hours(w)}</div>'
        secs=[]
        daily='<p>Day 1 starts on your selected program date; the labels are work sessions, not fixed weekdays. Divide each session using the week’s hour ledger.</p>'
        daily+=''.join(f'<div class="day"><div class="day-index">DAY {i+1:02}</div><div>{check(f"week-{n}-day-{i}",title)}<p>{E(desc)}</p></div></div>' for i,(title,desc) in enumerate(w['days']))
        daily+='<div class="day"><div class="day-index">DAY 07</div><div><h3>Recover or absorb overflow</h3><p>Keep this day flexible. Optional reading or a delayed run can fit here; do not assume another full mandatory workday.</p></div></div>'
        secs.append(('daily','The daily plan',daily))
        study='<h3>Theory modules</h3><div class="resource-links">'+''.join(f'<a class="resource-link" href="theory-{E(m)}.html">{E(next(x["title"] for x in MODULES if x["id"]==m))}</a>' for m in w['modules'])+'</div>'
        if w['labs']: study+='<h3>Implementation assignments</h3>'+ul_links([(f'lab-{LAB_BY_ID[l]["number"]}.html',f'Lab {LAB_BY_ID[l]["number"]}: {LAB_BY_ID[l]["title"]}') for l in w['labs']])
        study+='<p>Use the paper checkboxes in the next section. A time-permitting assignment may be skipped while completing the critical work.</p>'
        study+='<p><a href="reading.html#reading-method">Use the paper-reading template</a>: extract setting, model, update, actual experiment, limitations and a reproducible question.</p>'
        secs.append(('assignments','Study and implementation',study))
        reading=READING_SCHEDULE[n]
        reading_body=f'<p><strong>Up to {reading["hours"]:g} h inside this week’s theory allocation.</strong> A deep pass is about two hours; a survey is 20–30 minutes. Priority and depth are separate. Critical surveys need a mechanism/limitation note; time-permitting items can be skipped.</p>'
        reading_body+='<h3>Deep reading</h3>'+(paper_links(reading['deep']) if reading['deep'] else '<p>No new mandatory deep reading. Use the time for synthesis, retrieval or a specific evidence gap.</p>')
        reading_body+='<h3>Survey for context</h3>'+(paper_links(reading['survey']) if reading['survey'] else '<p>No new survey assignment.</p>')
        reading_body+=f'<div class="callout green"><strong>Produce:</strong> {E(reading["artifact"])}</div><p><a href="reading-foundations.html#sequence">See the complete reading progression →</a> · <a href="model-landscape.html#practice">Foundation-model practice →</a></p>'
        secs.append(('literature','The literature, in order',reading_body))
        secs.append(('deliverables','The deliverables',''.join(check(f'week-{n}-output-{i}',t) for i,t in enumerate(w['outputs']))))
        secs.append(('decision','Decision gate',f'<div class="callout">{E(w["gate"])}</div><h3>Explain this without notes</h3><p>{E(w["explain"])}</p><p class="small muted">Record a short answer, identify where your reasoning is vague, and revisit only those gaps.</p>'))
        secs.append(('notes','Private review notes',f'<label class="small muted" for="weekNotes">What worked, what failed, and what changes next week?</label><textarea id="weekNotes" class="notes" data-note="week-{n}" placeholder="Record evidence, questions and next actions. Saved only in this browser."></textarea>'))
        body+=article(secs)
        body+='<div class="week-nav">'+(f'<a class="button secondary" href="week-{n-1:02}.html">← Week {n-1}</a>' if n>1 else '<a class="button secondary" href="index.html">← Overview</a>')+(f'<a class="button" href="week-{n+1:02}.html">Week {n+1} →</a>' if n<12 else '<a class="button" href="research.html#release">Release checklist →</a>')+'</div>'
        write(f'week-{n:02}.html',f'Week {n:02}: {w["title"]}',body,'roadmap.html','Week',w['aim']+' '+w['explain'])

def ul_links(items): return '<ul>'+''.join(f'<li><a href="{E(href)}">{E(label)}</a></li>' for href,label in items)+'</ul>'

def build_theory():
    body=heading('02 / Theory & foundations','Theory and foundations','Build on existing modeling and research strengths. Focus new study on robotics, RL, control, learned dynamics and rigorous experiments.')
    body+='<div class="callout green"><strong>Study the lineage, not only the latest release.</strong> Use the <a href="reading-foundations.html">foundational-paper curriculum</a> with these modules, then compare <a href="model-landscape.html">current world models and robot policies</a>. These readings are assigned within each week’s theory hours.</div>'
    body+='<section id="self-assessment" class="card"><div class="card-label">Before you start / 90 minutes</div><h2>A practical self-assessment</h2><p>Score each area 0–3: <strong>0</strong> unfamiliar; <strong>1</strong> can recognize; <strong>2</strong> can explain/derive; <strong>3</strong> can implement/debug and discuss limitations. Start with the lowest-scoring core areas. Skip a module only after demonstrating its gate.</p>'+ul(['Derive a Bellman target and policy gradient, including a baseline.','Trace a PPO/SAC update with tensor dimensions and correct terminal masks.','Compose a camera-to-base transform and explain a robot action interface.','Compare BC, diffusion/flow policies, VLAs and action-conditioned world models.','Explain model-based planning versus persistent policy adaptation.','Design an evaluation with held-out layouts, a fair baseline and honest cost accounting.'])+'<label class="small muted" for="assessmentNotes">Your starting point</label><textarea class="notes" id="assessmentNotes" data-note="assessment" placeholder="Scores, strengths you can skip through, and priority gaps."></textarea></section>'
    body+='<div class="section-head"><h2>The core knowledge map</h2></div><div class="grid-3">'
    for i,m in enumerate(MODULES):
        body+=f'<div class="card"><div class="card-top"><span class="card-number">{i+1:02}</span><span class="tag">Weeks {E(m["weeks"])}</span></div><h3><a href="theory-{m["id"]}.html">{E(m["title"])}</a></h3><p>{E(m["question"])}</p><div class="card-footer"><span>{E(m["hours"])} h · {E(m["level"])}</span><a href="theory-{m["id"]}.html">Study →</a></div></div>'
    body+='</div><div class="callout green"><strong>Depth rule:</strong> each module ends in a derivation, an implementation or inspection, an explanation and a concrete mastery check. The goal is transfer into your experiment and your interview answers.</div>'
    write('theory.html','Theory and foundations',body,'theory.html')
    for m in MODULES:
        lab=LAB_BY_ID[m['lab']]
        body='<div class="breadcrumb"><a href="theory.html">Theory & foundations</a> / '+E(m['title'])+'</div>'+heading('Core knowledge / Weeks '+m['weeks'],m['title'],m['question'])
        body+=f'<div class="tags">{badge("Critical")}<span class="tag">{E(m["hours"])} study hours</span><a class="tag" href="lab-{lab["number"]}.html">Connected lab {lab["number"]} →</a></div>'
        secs=[('concepts','What to understand',ul(m['topics'])),('derive','What to derive or explain',ol(m['derive'])),('implement','Connect it to code',f'<p>{E(m["implement"])}</p><a class="button secondary" href="lab-{lab["number"]}.html">Open the implementation brief →</a><p><a href="model-landscape.html#practice">Cosmos and VLA implementation practice →</a></p>'),('resources','Primary resources',refs(m['resources'])+'<p class="small muted"><a href="reading-foundations.html">Read these in the scheduled order.</a> Use author documentation and repositories. Record the exact revision for any code you run. Runtime compatibility must be checked in your environment.</p>'),('interview','Interview retrieval practice',ul(m['interview'])),('gate','Mastery check',f'<div class="callout">{E(m["gate"])}</div>'+check('module-'+m['id'],'I can demonstrate this mastery check without following a tutorial.'))]
        body+=article(secs)
        write(f'theory-{m["id"]}.html',m['title'],body,'theory.html','Theory',m['question']+' '+' '.join(m['topics']))

def build_labs():
    body=heading('03 / Implementation labs','Implementation checklist','Twelve bounded assignments. Implement the essential mechanics yourself; reproduce and modify larger systems instead of rebuilding every framework.')
    body+='<section class="card"><div class="card-label">Pretrained-model practice / Weeks 5–7</div><h2>Work with a VLA and a world foundation model.</h2><p>The compact coding labs are complemented by two bounded practice blocks: OpenVLA/OFT or openpi inference and adaptation, plus a Cosmos/world-action-model capability audit. These draw from the existing research hours.</p><a href="model-landscape.html#practice">Open the hands-on briefs →</a></section>'
    body+='<div class="callout"><strong>Spinning Up belongs here.</strong> Use it for conceptual explanations and update equations. Treat its original code as a reference with older dependencies. Use an isolated environment and current documented examples from CleanRL, Gymnasium or Stable-Baselines3 for runnable baselines.</div><p class="small muted">Lab estimates fit inside the weekly ledger. Research-integrated labs use the research allocation as well as coding time; they are not extra hours added on top of the schedule.</p>'
    body+='<div class="grid-3">'
    for l in LABS:
        body+=f'<div class="card"><div class="card-top"><span class="card-number">LAB {l["number"]}</span>{badge(lab_priority(l["id"]))}<span class="tag">{l["hours"]} h</span></div><h3><a href="lab-{l["number"]}.html">{E(l["title"])}</a></h3><p>{E(l["brief"])}</p>{check("lab-"+l["id"],"Artifact implemented and verified")}<div class="card-footer"><span>Week {E(l["week"])} · {E(l["mode"])}</span><a href="lab-{l["number"]}.html">Instructions →</a></div></div>'
    body+='</div><div class="section-head"><h2>What is included now?</h2></div><div class="card"><p>The website ships with five original, runnable teaching examples: a Bellman gridworld, kinematics checks, a PPO update, a CEM planner, and evaluation/acquisition utilities. The larger assignments are detailed implementation briefs; they are not presented as finished robot-research code.</p><a href="examples/README.md">Open the starter-code guide →</a></div>'
    write('implementation.html','Implementation labs',body,'implementation.html')
    for l in LABS:
        body='<div class="breadcrumb"><a href="implementation.html">Implementation labs</a> / Lab '+l['number']+'</div>'+heading('Lab '+l['number']+' / Week '+l['week'],l['title'],l['brief'])
        body+=f'<div class="tags">{badge(lab_priority(l["id"]))}<span class="tag">{l["hours"]} focused hours</span><span class="tag">{E(l["mode"])}</span><a class="tag" href="theory-{l["module"]}.html">Theory companion →</a></div>'
        if l['file']: body+=f'<a class="code-link" href="examples/{l["file"]}" download><span>↓ Starter: {E(l["file"])}</span><span>Python</span></a>'
        starter=(f'<pre><code>python3 examples/{E(l["file"])}</code></pre><p>The example prints its own teaching checks. Read <a href="examples/README.md">dependencies and limitations</a> first. A passing teaching example is not a completed research experiment.</p>' if l['file'] else '<p>This lab is an implementation brief, not a claim that the complete system is supplied. Create the smallest reproducible version in your experiment repository, using the linked source as a reference.</p>')
        steps=''.join(check(f'lab-{l["id"]}-step-{i}',step) for i,step in enumerate(l['steps']))
        secs=[('build','Implementation checklist',steps),('check','How to verify it',ul(l['checks'])),('deliver','What to produce',f'<div class="callout green">{E(l["output"])}</div>'),('starter','Start here',starter+refs(l['resources'])),('scope','Optional depth',badge('Optional')+f'<p>{E(l["stretch"])}</p><p>Stop optional work when the timebox is exhausted. Complete critical steps and document what was skipped.</p>'+check('lab-'+l['id'],'I have a runnable artifact and can explain its verification and limitations.'))]
        body+=article(secs)
        write(f'lab-{l["number"]}.html',f'Lab {l["number"]}: {l["title"]}',body,'implementation.html','Lab',l['brief']+' '+' '.join(l['steps']))

def build_research():
    body=heading('04 / Research project','Research protocol','A proposed study of imagined policy adaptation, real-world verification and active correction. One task first; claims follow evidence.')
    body+='<div class="tags"><span class="tag">Proposed protocol</span><span class="tag">One arm · one core task</span><span class="tag">Learned predictive model</span><span class="tag orange">No results implied</span></div>'
    body+='<p><a class="button secondary" href="project-checklist.html">Open the research checklist and priorities →</a></p>'
    sections=list(PROJECT_SECTIONS)
    release_items=['Core code/configurations run from a clean setup.','Data/split manifests and paired imagined/executed examples are documented.','Metrics, uncertainty, costs and failed trials are reported.','A two-minute demo and technical presentation match real checkpoints.','The report states assumptions, related-work overlap and limitations.','Authorship, licenses and release permissions are resolved.']
    sections[-1]=(sections[-1][0],sections[-1][1],sections[-1][2]+''.join(check(f'release-{i}',t) for i,t in enumerate(release_items)))
    body+=article(sections)
    write('research.html','Research project and experiment protocol',body,'research.html','Research','Detailed experiment design: task, architecture, imagined policy updates, active physical verification, baselines, budgets, data splits, metrics and decision gates.')

def build_reading():
    body=heading('05 / Reading room','Related work and reading notes','The curriculum connects seminal algorithms, modern model families and the closest obstruction/adaptation research. Reading depth is bounded by the existing time budget.')
    body+='<div class="grid-2"><section class="card"><div class="card-label">Start here</div><h2>The foundational literature</h2><p>Dyna, World Models, PPO/SAC, PETS, PlaNet, Dreamer and MBPO; then robot-policy and foundation-model lineages. Twelve core deep reads, followed by selected surveys and a reference shelf.</p><a class="button secondary" href="reading-foundations.html">Papers, priorities & weekly order →</a></section><section class="card"><div class="card-label">From papers to systems</div><h2>The model landscape</h2><p>Compare latent dynamics, visual predictors, VLAs and world-action models. Include Cosmos, OpenVLA/OFT, openpi, DreamZero and V-JEPA; run selected interfaces.</p><a class="button secondary" href="model-landscape.html">Model map & hands-on work →</a></section></div>'
    body+='<section id="reading-method" class="card"><div class="card-label">Two-hour deep pass / 20–30 minute survey</div><h2>The six-question paper note</h2>'+ol(['Setting: what is known, what changes, and what data/interaction are allowed?','Model: what is learned, predicted or supplied by a simulator?','Update: which parameters change, and is adaptation at training time or deployment?','Evidence: which exact experiment demonstrates the behavior? Locate the figure, section and hardware/simulation distinction.','Comparison: which baseline, budget, split and sample count support the claim?','Transfer: what can we reproduce or reuse, and what limitation matters for our project?'])+'<p>Follow the assigned weekly reading schedule. The related-work shelf below is a source library, not an additional mandatory reading list. A difficult paper may take longer: replace a survey or optional review rather than expanding the week. By Weeks 9–12, prioritize synthesis and evidence.</p></section>'
    body+='<div class="section-head"><h2>The closest project literature</h2></div><div class="grid-2">'
    for key,when,kind,question,limit in sorted(PAPERS,key=lambda p:PRIORITY_RANK[paper_priority(p[0])]):
        title,url=RESOURCES[key]
        body+=f'<div class="card"><div class="card-top"><span class="tag">{E(when)}</span>{badge(paper_priority(key))}</div><div class="card-label">{E(kind)}</div><h3><a href="{E(url)}" target="_blank" rel="noopener">{E(title)}</a></h3>{check("paper-"+paper_key(key),"Source note complete")}<p><strong>Read to answer:</strong> {E(question)}</p><p><strong>Evidence boundary:</strong> {E(limit)}</p></div>'
    body+='</div><section id="novelty" class="card" style="margin-top:24px"><h2>Keep a living novelty matrix</h2><p>For each close paper, track learned model type, policy-update timing, obstruction novelty, model correction, real-trial selection, real-data budget, planning baseline and hardware evidence. The absence of a feature in an abstract does not establish novelty. Recheck the literature in Weeks 6 and 9 and before submission.</p><p>Promising comparison: event-triggered policy adaptation with actively selected physical correction. This remains a research hypothesis until the closest methods and their appendices have been checked.</p></section>'
    write('reading.html','Reading room and related-work boundaries',body,'reading.html','Reading','Paper-reading questions, evidence boundaries, world-model classifications and a novelty matrix for obstruction-triggered adaptation.')

def build_interviews():
    body=heading('06 / Interview preparation','Interview preparation','Prepare from day one; begin outreach only after six full weeks. Combine fundamentals, coding, research judgment and evidence from your own implementation.')
    body+='<div class="callout"><strong>Outreach starts in Week 7:</strong> <span data-outreach-date></span>. Weeks 1–6 are private study, coding, project work and rehearsal. This website does not send messages or create scheduled outreach.</div>'
    body+='<section id="career"><h2>The career preparation sequence</h2><div class="grid-2">'+''.join(f'<div class="card"><div class="card-label">{E(period)}</div><h3>{E(title)}</h3><p>{E(desc)}</p></div>' for period,title,desc in CAREER_PHASES)+'</div></section>'
    body+='<section id="coding" style="margin-top:36px"><h2>Coding practice that supports the role</h2>'+''.join(f'<details><summary>{E(title)}</summary><div class="answer">{E(desc)}</div></details>' for title,desc in CODING_PRACTICE)+'</section>'
    body+=f'<section id="questions" style="margin-top:36px"><h2>{len(QUESTIONS)} questions to answer with evidence</h2><p class="muted">Answer aloud before expanding the rubric. Use equations, dimensions, one concrete example and one limitation.</p><div class="filter-row">'+''.join(f'<button class="filter{(" active" if t=="All" else "")}" data-filter="{t}" aria-pressed="{str(t=="All").lower()}">{t}</button>' for t in ['All','RL','Robotics','Policies','World models','Research','Systems','Career'])+'</div>'
    body+=''.join(f'<details data-category="{E(category)}"><summary><span class="card-number">{i+1:02} / {E(category)}</span><br>{E(question)}</summary><div class="answer"><strong>A strong answer should cover:</strong> {E(answer)}</div></details>' for i,(category,question,answer) in enumerate(QUESTIONS))+'</section>'
    body+='<section id="narrative" class="card" style="margin-top:30px"><h2>Your project, at three depths</h2>'+ul(['2 minutes: physical problem, why a learned model helps, your method, one measured result and one limitation.','10 minutes: setting, strongest related work, architecture, baseline fairness, main figures and failure analysis.','30 minutes: equations, tensor/data flow, implementation decisions, ablations, statistical uncertainty, costs and next research steps.'])+'<p>Prepare three prior-research stories as well: a technical contribution, a difficult failure/debugging episode, and leadership/collaboration. Connect existing expertise to the new robot-learning evidence without implying that three months covers every robotics specialty.</p></section>'
    write('interviews.html','Interview and career preparation',body,'interviews.html','Interview',f'{len(QUESTIONS)} interview questions including model lineages, Cosmos, OpenVLA, coding practice and an outreach schedule beginning in week 7.')

def build_resources():
    body=heading('07 / Resource library','Resources and repositories','Read the theory references deeply and pin the code you actually run. Repository availability is not a guarantee of checkpoint, GPU or robot-interface compatibility.')
    body+='<div class="callout green"><a href="reading-foundations.html">The foundational papers and reading order →</a><br><a href="model-landscape.html">Current model families and required practice →</a></div>'
    groups=[('Explain and derive',['spinning','pg','sac','sutton','murphy','lehmann','modern','underactuated']),('Run baseline algorithms',['cleanrl','sb3','gym','mujoco']),('Collect data and learn policies',['lerobot','minari','robomimic','diffusion','openvla','openvla-oft','openpi']),('Learn and plan with world models',['dreamer','dinowm','tdmpc','vjepa2','cosmos','cosmos-policy-code','cosmos-cookbook','dreamzero']),('Read the closest research',['daydreamer','fosp','rise','wmpo','wovr','raw-dream','hawmpo','achieve-imagined','reoi','fail2progress','resync','evo-wam','replan']),('Generative-policy RL extensions · choose one if needed',['wmpo-code','fpo-code','flow-grpo-code','dsrl-code'])]
    for title,keys in groups:
        body+=f'<section style="margin-bottom:30px"><h2>{E(title)}</h2><div class="grid-2">'+''.join(f'<div class="card"><h3><a href="{E(RESOURCES[k][1])}" target="_blank" rel="noopener">{E(RESOURCES[k][0])} ↗</a></h3><p class="mono" style="overflow-wrap:anywhere">{E(RESOURCES[k][1])}</p></div>' for k in keys)+'</div></section>'
    body+='<section class="card"><h2>Environment and provenance rules</h2>'+ol(['Keep the learning sandbox and research training environments separate. Do not force older Spinning Up dependencies into the main robot stack.','Use repository setup instructions for your platform. Pin the working commit and resolved dependencies after the first successful run.','Use local CPU/MPS for small exercises; measure GPU requirements before selecting a large predictor or policy.','Keep raw robot logs and large checkpoints out of the website repository. Publish only the approved artifact and documented samples.','Record code revision, seed, config, split manifest, model/data source and actual device in every run.'])+'<p>Resource review date: October 14, 2026. The curriculum contains original assignments; source links support further study and implementation. Paper claims and compatibility should be rechecked before reproductions or publication.</p></section>'
    write('resources.html','Resource library and implementation references',body,'resources.html')

def build_project_checklist():
    body=heading('Research working checklist','Obstruction-triggered policy adaptation','Questions → prior work → setup → data → models → experiments → gates → release. Tick completed work; use the protocol page for the detailed experimental assumptions.')
    body+='<p><a href="research.html">Detailed protocol</a> · <a href="roadmap.html">Weekly study checklist</a> · <a href="reading-foundations.html#catalog">Paper checklist</a></p>'+priority_legend()
    body+='<nav class="toc" aria-label="Checklist sections">'+''.join(f'<a href="#{sid}">{E(title.split(" · ",1)[-1])}</a>' for sid,title,_ in PROJECT_CHECKLIST)+'</nav>'+priority_filters()
    for sid,title,items in PROJECT_CHECKLIST:
        body+=f'<section id="{sid}"><h2>{E(title)}</h2>'
        if sid=='questions':
            body+='<div class="table-wrap"><table><thead><tr><th>Question</th><th>What to establish</th></tr></thead><tbody>'+''.join(f'<tr><td>{E(key)} · {E(q)}</td><td>{E(desc)}</td></tr>' for key,q,desc,_ in RESEARCH_QUESTIONS)+'</tbody></table></div>'
        if sid=='study':
            body+='<p>Start with the <a href="reading-foundations.html">prioritized paper list</a>. Add the attachment’s reliability papers and active-learning foundations at the assigned depth. Read mechanisms and evidence before adopting an algorithm.</p>'
        if sid=='setup':
            body+='<p><strong>Primary setup:</strong> one arm, one obstruction-induced strategy-change task, logged execution and independent outcome checks. Two tasks and shared policy/simulator weights are extensions after the pilot.</p>'
        if sid=='data':
            body+='<p><strong>Initial hardware envelope:</strong> 320–430 episodes, including development, correction, evaluation and retention. The simulation plan begins with 1,080 headline evaluations across methods, seeds and layouts. These are provisional allocations; measure reset time and data needs before collection. <a href="research.html#budgets">Full budget and accounting →</a></p>'
        if sid=='models':
            body+='<p>Critical training includes the nominal policy, learned dynamics and actual imagined policy updates. Foundation-model interface knowledge is critical; a full Cosmos/DreamZero or generative-policy training experiment is conditional on compatibility and time.</p>'
        if sid=='experiments':
            body+='<p>One main figure per question. Report negative results and raw denominators. A desired optimism gap or success increase is a hypothesis, not a condition for accepting an experiment.</p>'
        if sid=='gates':
            body+='<p>Use week-relative gates rather than the attachment’s older calendar dates. Dates follow the start date in the plan home. Protect writing/figure-review time inside the research allocation from Week 4.</p>'
        if sid=='release':
            body+='<p>Outreach begins in Week 7: <strong data-outreach-date></strong>. The technical report and reproducible artifact are the planned deliverables; submission depends on evidence and readiness.</p>'
        for key,text,priority in sorted(items,key=lambda x:PRIORITY_RANK[x[2]]):
            body+=f'<div data-category="{E(priority)}">{check("project-"+key,text)}</div>'
        body+='</section>'
    write('project-checklist.html','Research checklist and priorities',body,'project-checklist.html','Checklist','Prioritized research actions with checkboxes: questions, prior work, setup, data, models, experiments, gates and release.')

def build_literature():
    body='<div class="breadcrumb"><a href="reading.html">Reading room</a> / Papers and priorities</div>'+heading('Study checklist','Papers, reading order and priorities','Check a paper after producing a note at its assigned depth. Work through critical items first; time-permitting and optional readings are not extra obligations.')
    body+=priority_legend()
    body+='<p><strong>Priority and depth are different:</strong> a critical survey requires understanding the mechanism and limitation; a deep read also requires the objective, method and evidence. It does not require reproducing the full system.</p>'
    body+='<section id="progression"><h2>Three connected lines of development</h2><div class="grid-3"><div class="card"><div class="card-label">Models and decisions</div><h3>Dyna → World Models → PETS / PlaNet → Dreamer / MBPO</h3><p>Learn dynamics, then distinguish planning through them from learning a policy with them. Continue to DreamerV3, TD-MPC2, DINO-WM and V-JEPA 2-AC.</p></div><div class="card"><div class="card-label">Robot policies and data</div><h3>DAgger → ACT / Diffusion Policy → RT-1 / RT-2 → generalist VLAs</h3><p>Study distribution shift, multimodal actions, scaling robot data and VLM transfer. Compare Open X-Embodiment, Octo, OpenVLA/OFT and π₀.</p></div><div class="card"><div class="card-label">Foundation world and action models</div><h3>Transformers / generative models → Cosmos → Cosmos Policy / DreamZero</h3><p>Connect representation and generation to actual robot actions. Study the current Cosmos 3 architecture and checkpoint interfaces.</p></div></div><p class="small muted">These are conceptual learning paths, not claims that each paper directly descends from its neighbor or that one family supersedes another.</p></section>'
    body+='<section id="sequence"><h2>Weekly reading checklist</h2><p>A deep pass is about two hours; a survey is 20–30 minutes. Reading time is inside the weekly theory allocation. The time below is a ceiling including selected time-permitting items; critical work comes first.</p><div class="table-wrap"><table><thead><tr><th>Week / up to</th><th>Deep reading</th><th>Survey / context</th></tr></thead><tbody>'
    for n,r in READING_SCHEDULE.items():
        deep=paper_links(r['deep']) if r['deep'] else 'No new mandatory paper; synthesize or resolve an evidence gap.'
        survey=paper_links(r['survey']) if r['survey'] else 'Use the reference shelf only as needed.'
        body+=f'<tr><td><a href="week-{n:02}.html#literature">Week {n}</a><br>{r["hours"]:g} h</td><td>{deep}</td><td>{survey}</td></tr>'
    body+='</tbody></table></div><p><strong>Weeks 1–6:</strong> twelve foundational/core papers. <strong>Weeks 7–8:</strong> four close project papers. <strong>Weeks 9–12:</strong> retrieval, novelty checks, writing and targeted review. Paper reading is one component of theory time; derivations and exercises use the remainder.</p></section>'
    body+='<section id="catalog"><h2>All papers, in priority order</h2><p>The same paper checkbox is synchronized across the weekly schedule, this list and related-work pages.</p>'+priority_filters()
    deep_keys={k for r in READING_SCHEDULE.values() for k in r['deep']}
    for key,title,year,url,family,depth,mechanism,connection in sorted(CANON,key=lambda p:PRIORITY_RANK[paper_priority(p[0])]):
        author_line = f'<p class="small muted">{E(CORE_AUTHORS[key])}</p>' if key in CORE_AUTHORS else ''
        depth='Deep read' if key in deep_keys else ('Reference' if depth=='Reference' else 'Survey')
        body+=f'<div class="paper-entry" data-category="{E(paper_priority(key))}">{check("paper-"+key,title)}<p class="paper-meta">{E(depth)} · {E(family)} · {E(year)} · <a href="{E(url)}" target="_blank" rel="noopener">Primary paper ↗</a></p><details id="paper-{E(key)}"><summary>Mechanism and implementation connection</summary><div class="answer">{author_line}<p><strong>Mechanism:</strong> {E(mechanism)}</p><p><strong>Do:</strong> {E(connection)}</p></div></details></div>'
        SEARCH.append(dict(title=title,kind='Paper',href='reading-foundations.html#paper-'+key,text=f'{paper_priority(key)} / {depth} / {family} / {year}. {mechanism} {connection}'))
    body+='</section><section class="card" style="margin-top:28px"><h2>What counts as understanding a paper?</h2>'+ol(['Draw the observations, actions, model, actor and learning signals, marking what is learned versus supplied.','Write the main objective and explain each term, including where gradients stop.','Locate one result that supports the central claim and one limitation relevant to your robot.','Connect the paper to a working exercise or a precise implementation inspection.','Explain what changed relative to its predecessor and what your project still needs to demonstrate.'])+'<p>This page provides study prompts and verified primary links. It does not claim that every paper has been reproduced or that abstracts establish detailed experimental validity. Use the <a href="reading.html#reading-method">six-question note</a> for full-paper reading.</p></section>'
    write('reading-foundations.html','Foundational papers and weekly reading order',body,'reading.html','Foundations','Dyna, World Models, PPO, SAC, PETS, PlaNet, Dreamer, MBPO, Diffusion Policy, OpenVLA, pi0, Cosmos Policy, foundational transformers and modern world-model lineages.')

    body='<div class="breadcrumb"><a href="reading.html">Reading room</a> / Model landscape</div>'+heading('Model study and implementation','World models and VLA practice','Understand the major families. Complete the critical interface audits; run selected inference/adaptation exercises when time and compatible hardware permit.')
    body+='<div class="callout"><strong>Two obligations:</strong> understand the model families for industry discussions; produce a small, measured implementation artifact for selected systems. Full pretraining or full benchmark reproduction is not required for every model.</div>'
    body+='<section id="families"><h2>A map of models, predictions and decisions</h2><div class="table-wrap"><table><thead><tr><th>Family / examples</th><th>What it predicts or does</th><th>Your required depth</th></tr></thead><tbody>'
    for family,examples,prediction,depth,keys in MODEL_FAMILIES:
        body+=f'<tr><td><strong>{E(family)}</strong><p>{E(examples)}</p></td><td>{E(prediction)}</td><td>{E(depth)}{paper_links(keys)}</td></tr>'
    body+='</tbody></table></div></section>'
    body+='<section id="cosmos"><h2>Cosmos belongs in the core knowledge map</h2><p>Study the original platform paper for context, then the <a href="https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf">Cosmos 3 report</a> and <a href="https://github.com/NVIDIA/Cosmos">current repository</a>. NVIDIA’s current documentation distinguishes reasoning and generation interfaces and includes action-related capabilities. Do not treat a generic video demo as the complete robotics interface.</p><p><a href="https://research.nvidia.com/labs/cosmos-lab/cosmos-policy/">Cosmos Policy</a> is a required deep read: it connects video pretraining to robot actions, future-state prediction and values. Compare direct execution with planning, then ask separately how you would fine-tune a policy on imagined experience and verify its gains physically.</p><p>For the legacy Predict / Transfer / Reason families, understand prediction versus spatially controlled generation versus reasoning. Newer Cosmos 3 capabilities make a blanket claim that “Cosmos cannot accept actions” incorrect; checkpoint-specific interfaces and embodiment support decide what can actually be used.</p></section>'
    body+='<section id="vlas"><h2>OpenVLA is required, alongside its predecessors and alternatives</h2><p>Read <a href="https://arxiv.org/abs/2406.09246">OpenVLA</a> after RT-1, RT-2 and Open X-Embodiment. Trace the original tokenized action decoder and normalization; then compare <a href="https://openvla-oft.github.io/">OpenVLA-OFT</a> and its continuous chunked-action recipe with <a href="https://arxiv.org/abs/2410.24164">π₀’s flow-based action generation</a>. Survey ACT, Octo, π₀.₅ and GR00T to understand alternative architecture/data choices.</p><p>A VLA is a policy family; a world model supplies predictions of how actions change the environment. A system can contain both. Joint action/video prediction in Cosmos Policy or DreamZero should be examined explicitly rather than inferred from the word “foundation.”</p></section>'
    body+='<section id="practice"><h2>Two bounded hands-on blocks</h2><p>Reserve 12 hours from the existing research allocation: four hours in Week 5, six in Week 6 and two in Week 7. They replace model-interface exploration and optional model upgrades; they do not add hours or delay the core loop. The VLA block uses six hours across Weeks 5–6; the world-model block uses six across Weeks 6–7. If blocked, stop at the documented audit and preserve the compact experiment.</p>'
    for p in PRACTICE:
        steps=''.join(check(f'{p["id"]}-step-{i}',step) for i,step in enumerate(p['steps']))
        body+=f'<section id="{E(p["id"])}" class="card" style="margin-top:20px"><div class="card-label">{E(p["when"])} / {E(p["hours"])}</div><h3>{E(p["title"])}</h3>{steps}<div class="callout green"><strong>Deliver:</strong> {E(p["deliver"])}</div>{check(p["id"],"Critical interface audit documented")}{refs(p["resources"])}</section>'
    body+='</section><section id="choice"><h2>Make a model decision you can defend</h2>'+ol(['Write the exact observation/action contract and compatible embodiment, not only the model name.','Separate source inspection, inference run, fine-tuning smoke test and actual closed-loop evaluation in your report.','Profile memory, rollout throughput and end-to-end latency before promising online imagination at foundation-model scale.','Require action-sensitive predictions at contact and a valid reward/readout before synthetic policy optimization.','Keep the compact core when it answers the research question. Add a foundation-model experiment before making a foundation-model-specific publication claim.'])+'<p class="small muted">Current-source review: October 14, 2026. Model versions and hardware requirements can change; use the linked current repositories and record the exact revision you run.</p></section>'
    write('model-landscape.html','World models, VLAs and foundation-model practice',body,'reading.html','Models','Cosmos 3, Cosmos Policy, OpenVLA, OpenVLA-OFT, openpi pi0, DreamZero, V-JEPA 2, DINO-WM, Dreamer and two bounded implementation blocks.')

if __name__ == '__main__':
    assert len({x for x in CHECKS}) == len(CHECKS)
    assert all(sum(w['hours']) == 42 and len(w['days']) == 6 for w in WEEKS)
    build_overview();build_roadmap();build_theory();build_labs();build_research();build_reading();build_interviews();build_resources();build_literature();build_project_checklist()
    (ROOT/'assets/search-index.js').write_text('window.PLAN_CHECKS='+json.dumps(CHECKS)+';\nwindow.PLAN_PRIORITIES='+json.dumps(CHECK_META)+';\nwindow.PLAN_SEARCH='+json.dumps(SEARCH,ensure_ascii=False)+';\n',encoding='utf-8')
    (ROOT/'plan.json').write_text(json.dumps(dict(start='2026-10-14',weeks=WEEKS,modules=MODULES,labs=LABS,resources=RESOURCES,canon=CANON,reading_schedule=READING_SCHEDULE,model_practice=PRACTICE,priorities=CHECK_META,project_checklist=PROJECT_CHECKLIST,outreach_week=7,weekly_hours=42),ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built {len(list(ROOT.glob("*.html")))} pages, {len(CHECKS)} progress checks, {sum(sum(w["hours"]) for w in WEEKS)} core hours.')
