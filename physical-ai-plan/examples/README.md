# Teaching examples

These are original, miniature exercises for the learning program. They do not
constitute a completed robot-learning implementation or experimental results.
No script commands hardware or uses a learned foundation-model checkpoint.

Run from the `physical-ai-plan` directory:

```bash
python3 examples/bellman_grid.py
python3 examples/kinematics.py
python3 examples/cem_planner.py
python3 examples/metrics_and_selection.py
```

These four scripts use only the Python standard library (Python 3.9+). The PPO
update additionally requires PyTorch in your learning environment:

```bash
python3 examples/ppo_update.py
```

| Example | What is implemented | Boundary |
| --- | --- | --- |
| Bellman grid | Value iteration and a wall intervention | Known tabular transitions, not neural imagination |
| Kinematics | Planar FK, Jacobian and damped IK | Not a hardware controller or full SE(3) library |
| PPO update | GAE with terminal/truncation handling and one update | Not a complete PPO trainer |
| CEM planner | Bounded trajectory search around a rectangle | Analytic teaching dynamics, not learned world-model planning |
| Metrics/selection | Outcome-blind candidate selection and layout bootstrap | Synthetic example numbers; uncertainty is not calibrated |

Each script includes targeted teaching checks. The larger labs on the website
specify what remains to implement, reproduce, evaluate and document.
