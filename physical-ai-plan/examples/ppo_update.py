"""One educational PyTorch PPO update, including terminal/truncation-aware GAE.

Requires torch. This is an update exercise, not a complete PPO trainer.
"""
import torch
from torch import nn
from torch.distributions import Categorical


def gae(rewards, values, terminated, truncated, gamma=0.99, lam=0.95):
    """One contiguous sequence; values has T+1 entries.

    At truncations values[t+1] must be the final observation's value, not a
    vectorized environment's auto-reset observation. Bootstrap is permitted,
    but the advantage recurrence must not leak into the next episode.
    """
    advantages = torch.zeros_like(rewards)
    carry = torch.zeros((), dtype=rewards.dtype, device=rewards.device)
    for t in reversed(range(len(rewards))):
        bootstrap = (~terminated[t]).to(rewards.dtype)
        continuing = (~(terminated[t] | truncated[t])).to(rewards.dtype)
        delta = rewards[t] + gamma*bootstrap*values[t+1] - values[t]
        carry = delta + gamma*lam*continuing*carry
        advantages[t] = carry
    return advantages.detach(), (advantages + values[:-1]).detach()


def ppo_loss(model, obs, actions, old_logp, advantages, returns, clip=0.2):
    output = model(obs)
    dist = Categorical(logits=output[:, :2])
    values = output[:, 2]
    logp = dist.log_prob(actions)
    ratio = (logp-old_logp.detach()).exp()
    advantages = advantages.detach()
    policy = -torch.minimum(ratio*advantages, ratio.clamp(1-clip,1+clip)*advantages).mean()
    value = 0.5*(values-returns.detach()).square().mean()
    entropy = dist.entropy().mean()
    approximate_kl = ((ratio-1)-(logp-old_logp.detach())).mean().detach()
    return policy + 0.5*value - 0.01*entropy, {'policy':policy.detach(), 'value':value.detach(), 'kl':approximate_kl}


if __name__ == '__main__':
    torch.manual_seed(7)
    rewards = torch.tensor([1.0, 2.0])
    values = torch.tensor([0.5, 0.5, 4.0])
    terminal = torch.tensor([False, True])
    truncation = torch.tensor([False, False])
    a, _ = gae(rewards, values, terminal, truncation, gamma=1.0, lam=1.0)
    assert torch.allclose(a, torch.tensor([2.5, 1.5]))
    b, _ = gae(torch.tensor([2.0]), torch.tensor([0.5, 4.0]), torch.tensor([False]), torch.tensor([True]), gamma=1.0)
    assert torch.allclose(b, torch.tensor([5.5]))
    model = nn.Sequential(nn.Linear(4,32),nn.Tanh(),nn.Linear(32,3))
    obs = torch.randn(16,4)
    with torch.no_grad():
        old_dist = Categorical(logits=model(obs)[:,:2])
        actions = old_dist.sample(); old_logp = old_dist.log_prob(actions)
    advantages, returns = torch.randn(16), torch.randn(16)
    loss, metrics = ppo_loss(model,obs,actions,old_logp,advantages,returns)
    optimizer = torch.optim.Adam(model.parameters(),lr=3e-4)
    optimizer.zero_grad(); loss.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    optimizer.step()
    print('One PPO update:', {key:float(value) for key,value in metrics.items()})
    print('Terminal, truncation and finite-gradient teaching checks passed.')
