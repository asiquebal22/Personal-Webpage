"""One priority vocabulary for papers, coding, research and completion tracking."""

from literature import CANON

PRIORITIES = ("Critical", "If time permits", "Optional")
PRIORITY_RANK = {label: i for i, label in enumerate(PRIORITIES)}
PRIORITY_CLASS = {"Critical": "critical", "If time permits": "time", "Optional": "optional"}
PRIORITY_HELP = {
 "Critical": "Protect this work first: interview foundations, the core adaptation experiment and a trustworthy artifact. Complete the stated depth; survey does not mean full reproduction.",
 "If time permits": "Do after the critical work for that week is on track. Use the existing timebox; replace lower-value review rather than extending the week.",
 "Optional": "An extension or specialist direction. It is not required to finish the three-month program and does not hold up release.",
}

_CRITICAL_SURVEYS = {"dagger", "attention", "ddpm", "flow", "lora", "rt2", "oxe", "oft", "dinowm-paper", "cosmos3", "dreamzero-paper", "wmpo", "wovr", "gae", "mopo", "deep-ensembles", "bald", "plan2explore", "hil-serl", "action-following"}
_CORE = {p[0] for p in CANON if p[5] == "Core"}
_REFERENCE = {p[0] for p in CANON if p[5] == "Reference"}
PAPER_ALIASES = {"dinowm": "dinowm-paper", "dreamer": "dreamerv3"}
_CRITICAL_RELATED = {"daydreamer", "fosp", "rise", "reoi", "fail2progress", "evo-wam", "achieve-imagined"}

def paper_key(key):
    return PAPER_ALIASES.get(key, key)

def paper_priority(key):
    key = paper_key(key)
    if key in _CORE | _CRITICAL_SURVEYS | _CRITICAL_RELATED:
        return "Critical"
    if key in {"wam-survey", "murphy", "lehmann", "flow-grpo", "dsrl"}:
        return "If time permits"
    if key in _REFERENCE | {"cbwm", "namo", "nie"}:
        return "Optional"
    return "If time permits"

def lab_priority(key):
    return "If time permits" if key == "diffusion" else "Critical"

# The paper's significance, reading depth and full-system implementation cost
# are separate. These overrides label individual implementation steps.
LAB_STEP_PRIORITY = {
 ("diffusion", 0): "If time permits", ("diffusion", 1): "If time permits", ("diffusion", 2): "If time permits", ("diffusion", 3): "Critical",
 ("dynamics", 3): "If time permits",
 ("ppo", 3): "If time permits",
}

PRACTICE_STEP_PRIORITY = {
 "vla-practice": ["Critical", "Critical", "If time permits", "If time permits", "Critical"],
 "cosmos-practice": ["Critical", "If time permits", "If time permits", "If time permits", "Critical"],
}

QUESTIONS = [
 ("RQ1", "Measure the imagination–execution gap", "Do predicted gains survive execution after a new obstruction? Use paired starts and actual outcomes; a large gap is a possible finding, not a required result.", "Critical"),
 ("RQ2", "Establish the value of adaptation", "Do persistent policy updates add anything beyond frozen behavior and compute-matched planning with the same learned model?", "Critical"),
 ("RQ3", "Spend real trials well", "At a fixed correction budget, does active selection beat uniform random trials? A policy-rollout refresh baseline is the next comparison if time permits.", "Critical"),
 ("RQ4", "Test transfer and retention", "Do corrections help on untouched obstruction layouts, and does the nominal task still work after adaptation?", "Critical"),
]

# section id, title, (stable checkbox id, action, priority)
PROJECT_CHECKLIST = [
 ("questions", "01 · Questions and claims", [
  ("claim-scope", "Write the four questions, the observation/model setting and one falsifiable primary claim.", "Critical"),
  ("claim-overlap", "Compare the closest methods in a novelty matrix; do not equate an unsuccessful search with an open problem.", "Critical"),
  ("claim-shared", "Test shared versus separate policy/simulator weights as a mechanism study after the main comparison.", "Optional"),
 ]),
 ("study", "02 · Study and prior work", [
  ("study-foundations", "Complete the assigned critical foundational papers and explain their objectives without notes.", "Critical"),
  ("study-reliability", "Compare RISE/WMPO, WoVR, Achieve What You Imagined and EVO-WAM with the planned update/verification loop.", "Critical"),
  ("study-guards", "Deep-read RAW-Dream and HaWMPO to select one compatible reliability-control ablation.", "If time permits"),
  ("study-generative", "Inspect FPO, Flow-GRPO or DSRL when implementing a generative-policy extension; do not implement all three.", "Optional"),
 ]),
 ("setup", "03 · Setup and protocol", [
  ("setup-task", "Freeze one clear-access→grasp/place task, a legal obstruction family, success rubric and reset procedure.", "Critical"),
  ("setup-interface", "Record and replay timestamped observations, executed actions, units, frames, contacts and outcome labels.", "Critical"),
  ("setup-compute", "Profile the reported 2 × A6000 setup and available cluster allocation; pin a model route from measured memory and rollout throughput.", "Critical"),
  ("setup-extra-sensors", "Add wrist-camera or force/torque features when available and when they resolve a measured failure.", "If time permits"),
  ("setup-task-two", "Add a second contact-rich task, such as insertion, after the primary result is stable.", "Optional"),
 ]),
 ("data", "04 · Data and real-trial budget", [
  ("data-splits", "Separate training, development/acquisition, held-out layouts and nominal retention before final evaluation.", "Critical"),
  ("data-pairs", "Save a matched imagined rollout for each evaluation/correction trial where the model supports that comparison; retain failures and aborted attempts.", "Critical"),
  ("data-budget", "Use nested correction budgets and log all training, correction, evaluation, reset and operator costs separately.", "Critical"),
  ("data-format", "Export a redistributable paired subset in LeRobot format with a dataset card and precise provenance.", "If time permits"),
  ("data-expansion", "Expand toward the attachment’s two-task, ~1,950-episode study only after measured operator/compute capacity supports it.", "Optional"),
 ]),
 ("models", "05 · Models and learning loop", [
  ("model-base", "Run the nominal policy and action-conditioned predictor; check contact/blocker persistence and multi-step error.", "Critical"),
  ("model-reward", "Validate the success/progress readout against actual outcomes before optimizing against it.", "Critical"),
  ("model-adapt", "Run short imagined rollouts, a real policy-parameter update, execution and retention checks end to end.", "Critical"),
  ("model-correct", "Rank legal candidate trials before their outcomes are known, collect the selected transitions, correct the predictor and repeat adaptation.", "Critical"),
  ("model-audit", "Audit Cosmos/Cosmos Policy/DreamZero and one OpenVLA/OFT or openpi interface; document exactly what was inspected or run.", "Critical"),
  ("model-foundation", "Port the full adaptation experiment to a compatible foundation model if the measured route fits the budget. This is required before making a foundation-model-specific result claim.", "If time permits"),
  ("model-all-guards", "Reproduce all three hallucination-control families and a shared-weights mechanism study.", "Optional"),
 ]),
 ("experiments", "06 · Experiments, one question per figure", [
  ("experiment-pilot", "E0: execute a full pilot round and diagnose model, search, controller and policy-update failures, whether or not an optimism gap appears.", "Critical"),
  ("experiment-gap", "E1 / RQ1: plot predicted versus executed success over adaptation rounds and inspect paired contact failures.", "Critical"),
  ("experiment-planning", "E2 / RQ2: compare frozen policy, same-model MPC and imagination-only adaptation under reported compute/time budgets.", "Critical"),
  ("experiment-active", "E3 / RQ3: compare active and random real correction at matched nested budgets, with layout-level intervals.", "Critical"),
  ("experiment-transfer", "E4 / RQ4: evaluate untouched obstruction layouts and nominal-task retention.", "Critical"),
  ("experiment-guard", "E5: compare one faithfully specified reliability-control variant at a matched data/compute budget; label simplified variants clearly.", "If time permits"),
  ("experiment-refresh", "Add policy-rollout refresh as a third correction-data baseline from the same initial data and total real-trial allowance.", "If time permits"),
  ("experiment-shifts", "Test moved/slippery objects, action offsets and additional embodiments as separate harder splits.", "Optional"),
 ]),
 ("gates", "07 · Gates and schedule", [
  ("gate-two", "Week 2: reset→act→record→replay works and one nominal/blocked execution is interpretable.", "Critical"),
  ("gate-four", "Week 4: action-sensitive prediction and a same-model planner run; diagnose inadequate predictions before synthetic optimization.", "Critical"),
  ("gate-six", "Week 6: the adaptation/correction pilot runs and the confirmatory protocol is frozen. Select the claim from evidence.", "Critical"),
  ("gate-eight", "Week 8: the matched comparison and preliminary budget curve are reproducible.", "Critical"),
  ("gate-eleven", "Week 11: the clean reproduction, cost ledger, figures and limitations support the intended release.", "Critical"),
 ]),
 ("release", "08 · Release and industry transition", [
  ("release-recipe", "Release a reproducible recipe, configurations, evaluated provenance and an evidence-backed technical report.", "Critical"),
  ("release-demo", "Create the paired imagination/execution demo, failure gallery and 10-minute project presentation.", "Critical"),
  ("release-outreach", "Prepare privately during Weeks 1–6; begin outreach and applications only in Week 7.", "Critical"),
  ("release-preprint", "Prepare a submission/preprint after results, authorship, permissions and current venue dates justify it.", "If time permits"),
  ("release-assets", "Release large checkpoints and a full paired dataset when licensing, storage and documentation are ready.", "Optional"),
 ]),
]
