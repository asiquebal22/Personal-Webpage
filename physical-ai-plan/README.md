# Fieldwork / Physical AI

A detailed three-month study, coding, research and interview preparation website.
Outreach begins in **week 7, after six full weeks**. The core schedule contains
12 weeks × 42 hours = 504 hours, plus a calendar buffer.

Open `index.html` directly or serve this directory:

```bash
python3 -m http.server 8787
```

The website has no runtime dependencies or external tracking. All learning pages
are generated as actual HTML pages; links are relative so the site works inside
a GitHub Pages repository subdirectory. Checkboxes, notes and the chosen start
date are stored only in the current browser. Export/import transfers that state;
it is not synchronized to GitHub or another device.

## Contents

- Weekly roadmap and 12 individual weekly pages with daily actions and gates.
- Nine theory modules with derivations, implementation connections and mastery checks.
- Twelve implementation labs with verification criteria and five runnable teaching scripts.
- Detailed research task, architecture, learning loop, baselines, splits, budgets and metrics.
- A foundational-paper curriculum with twelve core deep reads, scheduled surveys,
  primary paper links, study prompts and a reference shelf.
- A model landscape covering Cosmos/Cosmos Policy, OpenVLA/OFT, openpi, DreamZero,
  V-JEPA, DINO-WM and the historical model-based RL and robot-policy lineages.
- Two bounded foundation-model practice blocks inside the existing research budget.
- Closest-project reading notes with model classifications and evidence boundaries.
- Interview questions, coding exercises and career preparation beginning privately.
- A resource library linking primary documentation and author repositories.

The site is a proposed plan, not evidence of completed experiments. The teaching
scripts and synthetic examples are labeled accordingly. A paper submission and
strong novelty claim depend on actual results and a fresh literature comparison.

Reading time is included in each week's theory allocation. The two model-practice
blocks use 12 existing research hours across Weeks 5–7 (4/6/2 hours), replacing
optional exploration. They do not expand the 504-hour core schedule. Checkpoint
inference and fine-tuning depend on compatible data and compute; the site separates
an audit, a run and a validated closed-loop result.

## Edit and regenerate

`content/` contains the original curriculum and protocol as Python data.
`build.py` generates HTML, `plan.json` and `assets/search-index.js` using only the
Python standard library. Run with Python 3.12+ in the supplied workspace:

```bash
python3 build.py
```

`assets/style.css` and `assets/app.js` implement responsive navigation, search,
progress export/import, notes, rescheduling and print support.

Source review and initial program date: **October 14, 2026**. The start date can
be changed in the overview; the outreach boundary remains relative to week 7.

## Hosting

The generated folder can be committed under `physical-ai-plan/` in a static
website repository without replacing its home page. If GitHub Pages serves the
repository root, the plan is available at its `/physical-ai-plan/` path.

Do not commit private interview notes, credentials, raw robot data, checkpoints
or generated browser profiles. Browser progress exports are personal backups.
