"""Original active-selection and grouped-bootstrap teaching examples.

Candidate selection never receives actual candidate outcomes. Example metrics
use explicitly synthetic numbers, not measured robot results.
"""
import random
from math import sqrt
from statistics import mean, pvariance


def score(candidate):
    predictions = candidate['predicted_success_by_model']
    return mean(predictions) * pvariance(predictions)


def select(candidates, budget, separation=0.2):
    if budget < 0:
        raise ValueError('Budget must be nonnegative')
    if budget == 0:
        return []
    chosen=[]
    for candidate in sorted(candidates,key=score,reverse=True):
        if all(sqrt(sum((a-b)**2 for a,b in zip(candidate['features'],old['features'])))>=separation for old in chosen):
            chosen.append(candidate)
        if len(chosen)>=budget:break
    return chosen


def quantile(values, p):
    ordered=sorted(values); position=p*(len(ordered)-1)
    i=int(position); alpha=position-i
    return ordered[i]*(1-alpha)+ordered[min(i+1,len(ordered)-1)]*alpha


def paired_layout_bootstrap(layout_means_a, layout_means_b, draws=2000, seed=7):
    """Resample paired layouts, not every correlated frame or episode."""
    keys=sorted(layout_means_a)
    if set(keys)!=set(layout_means_b) or not keys:raise ValueError('Paired layout IDs required')
    differences=[layout_means_a[k]-layout_means_b[k] for k in keys]
    rng=random.Random(seed)
    samples=[mean(rng.choices(differences,k=len(keys))) for _ in range(draws)]
    return mean(differences),(quantile(samples,0.025),quantile(samples,0.975))


def brier(predictions,outcomes):
    if len(predictions)!=len(outcomes) or not predictions:raise ValueError('Paired predictions required')
    return mean((p-y)**2 for p,y in zip(predictions,outcomes))


if __name__ == '__main__':
    candidates=[{'id':'a','features':(0,0),'predicted_success_by_model':[0.9,0.9,0.9]},
                {'id':'b','features':(1,0),'predicted_success_by_model':[0.2,0.95,0.8]},
                {'id':'c','features':(1.05,0),'predicted_success_by_model':[0.1,0.95,0.9]},
                {'id':'d','features':(0,1),'predicted_success_by_model':[0.4,0.8,0.7]}]
    chosen=select(candidates,2)
    assert select(candidates,0)==[]
    assert len(chosen)==2 and len({c['id'] for c in chosen})==2
    assert not any('actual_outcome' in c for c in candidates)
    a={f'layout{i}':x for i,x in enumerate([.7,.8,.6,.9,.5,.8])}
    b={f'layout{i}':x for i,x in enumerate([.6,.6,.6,.7,.4,.7])}
    estimate,interval=paired_layout_bootstrap(a,b)
    print('Selected candidates:',[c['id'] for c in chosen])
    print('SYNTHETIC paired-layout difference:',round(estimate,3),'95% bootstrap interval:',tuple(round(x,3) for x in interval))
    print('Example Brier score:',brier([0.9,0.2],[1,0]))
    print('Teaching checks passed. Ensemble disagreement is not calibrated uncertainty.')
