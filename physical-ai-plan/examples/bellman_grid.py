"""Teaching example: a new wall invalidates a policy. No neural world model.

Run with Python 3.9+. The revised policy is computed by value iteration, not RL.
"""
from math import inf

WIDTH, HEIGHT = 7, 5
START, GOAL = (0, 2), (6, 2)
ACTIONS = ((1, 0), (0, -1), (0, 1), (-1, 0))
GAMMA = 0.97


def transition(state, action, walls):
    if state == GOAL:
        return GOAL, 0.0
    x, y = state[0] + action[0], state[1] + action[1]
    target = (x, y)
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or target in walls:
        target = state
    return target, (1.0 if target == GOAL else -0.01)


def solve(walls, tolerance=1e-10):
    states = [(x, y) for x in range(WIDTH) for y in range(HEIGHT) if (x, y) not in walls]
    values = {s: 0.0 for s in states}
    residual = inf
    for _ in range(5000):
        updated = {}
        for s in states:
            if s == GOAL:
                updated[s] = 0.0
                continue
            scores = [r + GAMMA * values[next_s] for next_s, r in (transition(s, a, walls) for a in ACTIONS)]
            updated[s] = max(scores)
        residual = max(abs(updated[s] - values[s]) for s in states)
        values = updated
        if residual < tolerance:
            break
    policy = {}
    for s in states:
        policy[s] = max(ACTIONS, key=lambda a: transition(s, a, walls)[1] + GAMMA * values[transition(s, a, walls)[0]])
    return values, policy, residual


def execute(policy, walls, limit=30):
    path = [START]
    for _ in range(limit):
        if path[-1] == GOAL:
            break
        path.append(transition(path[-1], policy[path[-1]], walls)[0])
    return path


def diagram(path, walls):
    for y in range(HEIGHT):
        print(' '.join('S' if (x,y)==START else 'G' if (x,y)==GOAL else '#' if (x,y) in walls else '·' if (x,y) in path else '_' for x in range(WIDTH)))


if __name__ == '__main__':
    walls = {(3, 1), (3, 2), (3, 3)}
    _, old_policy, old_residual = solve(set())
    original = execute(old_policy, set())
    blocked = execute(old_policy, walls)
    values, new_policy, residual = solve(walls)
    recovered = execute(new_policy, walls)
    assert original[-1] == GOAL and blocked[-1] != GOAL
    assert recovered[-1] == GOAL and len(recovered) > len(original)
    assert values[GOAL] == 0 and residual < 1e-8
    for name, path, scene in [('Original', original, set()), ('Frozen policy after blockage', blocked, walls), ('Replanned', recovered, walls)]:
        print(f'\n{name}: {len(path)-1} steps; reached goal = {path[-1] == GOAL}')
        diagram(path, scene)
    print(f'\nBellman residual: {residual:.3g}. All teaching checks passed.')
