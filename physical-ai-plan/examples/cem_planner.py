"""Pure-Python CEM trajectory search with an analytic point transition.

Teaching example only: no learned dynamics, no robot benchmark, no policy update.
Replace rollout_cost's transition with your learned model in Lab 09.
"""
import random
from math import sqrt

START, GOAL = (-1.0, 0.0), (1.0, 0.0)
HORIZON, BOUND = 20, 0.15


def rollout_cost(actions):
    x, y = START
    cost = 0.0
    for dx, dy in actions:
        next_x, next_y = x+dx, y+dy
        # Short substeps expose contact along a segment, not just at endpoints.
        collision = any(-0.18<=x+(next_x-x)*t/8<=0.18 and -0.38<=y+(next_y-y)*t/8<=0.38 for t in range(1,9))
        if collision:
            cost += 80
        else:
            x, y = next_x, next_y
        cost += 0.04*((x-GOAL[0])**2+(y-GOAL[1])**2) + 0.05*(dx*dx+dy*dy)
    return cost+20*((x-GOAL[0])**2+(y-GOAL[1])**2), (x,y)


def cem(seed=7, samples=384, rounds=10, elite_count=32):
    rng = random.Random(seed)
    mean = [[0.1,0.0] for _ in range(HORIZON)]
    std = [[0.14,0.14] for _ in range(HORIZON)]
    best = None
    for _ in range(rounds):
        candidates=[]
        for _ in range(samples):
            actions=[tuple(max(-BOUND,min(BOUND,rng.gauss(mean[t][d],std[t][d]))) for d in range(2)) for t in range(HORIZON)]
            score, end=rollout_cost(actions)
            candidates.append((score,actions,end))
        candidates.sort(key=lambda x:x[0]); elites=candidates[:elite_count]
        if best is None or elites[0][0]<best[0]:best=elites[0]
        for t in range(HORIZON):
            for d in range(2):
                avg=sum(c[1][t][d] for c in elites)/elite_count
                variance=sum((c[1][t][d]-avg)**2 for c in elites)/elite_count
                mean[t][d]=avg;std[t][d]=max(0.012,sqrt(variance))
    return best


if __name__ == '__main__':
    direct, _ = rollout_cost([(0.1,0.0)]*HORIZON)
    score, actions, end = cem()
    assert score<direct and all(abs(x)<=BOUND for action in actions for x in action)
    print('Straight-path cost:',round(direct,3))
    print('CEM cost:',round(score,3),'final position:',tuple(round(x,3) for x in end))
    print('Final distance:',round(sqrt((end[0]-GOAL[0])**2+(end[1]-GOAL[1])**2),3))
    print('Teaching checks passed. This is trajectory optimization, not policy fine-tuning.')
