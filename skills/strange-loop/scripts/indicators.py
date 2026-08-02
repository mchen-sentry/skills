#!/usr/bin/env python3
"""An indicator battery: how confident can an outside actor be?

No test can establish that a system is phenomenally conscious - not for this
program, and not for the person running it (the problem of other minds). The
scientific alternative (Butlin et al. 2023, "Consciousness in Artificial
Intelligence") is to assess a system against indicator properties derived from
the major theories, using third-person tests anyone can rerun. Confidence is
then graded and evidence-based rather than binary.

This script embeds a richer agent than workspace.py - embodied in a small
world, predictive, metacognitive, learning - runs the battery against it, and
prints a scorecard with measured values, including the indicators it fails.

Deterministic for a given --seed. Standard library only.
"""

import argparse
import random
import statistics

WORLD = 24  # positions on a circular 1-D world


def circ_dist(a: float, b: float) -> float:
    d = abs(a - b) % WORLD
    return min(d, WORLD - d)


def toward(src: float, dst: float) -> int:
    """Step direction (-1, 0, 1) along the shortest arc from src to dst."""
    if circ_dist(src, dst) < 0.5:
        return 0
    return 1 if (dst - src) % WORLD < WORLD / 2 else -1


class Env:
    """A resource drifts around a ring; the agent is rewarded for staying near it."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.agent = 0
        self.resource = WORLD // 2

    def step(self, action: int) -> float:
        self.agent = (self.agent + action) % WORLD
        if self.rng.random() < 0.2:
            self.resource = (self.resource + self.rng.choice([-1, 1])) % WORLD
        return 1.0 - 2.0 * circ_dist(self.agent, self.resource) / WORLD

    def observe(self) -> tuple[float, float]:
        """A noisy reading of the resource position; noise level varies per tick."""
        sigma = self.rng.uniform(0.3, 3.0)
        return (self.resource + self.rng.gauss(0.0, sigma)) % WORLD, sigma


class Agent:
    """Global workspace + world model + metacognition + learned agency.

    lesioned=True severs the broadcast: modules still run, but nothing is
    globally available. The performance gap between the two conditions is what
    the workspace contributes.
    """

    PRIOR_SIGMA = 1.2  # how much the system trusts its own top-down prediction

    def __init__(self, lesioned: bool = False):
        self.lesioned = lesioned
        self.prediction: float | None = None   # world model's estimate of the resource
        self.broadcast_estimate: float | None = None  # what the workspace made available
        self.trust = 0.5          # learned propensity to act on the broadcast
        self.reward_baseline = 0.0
        self.acted_on_broadcast = False
        self.log: list[dict] = []

    def tick(self, env: Env, rng: random.Random) -> None:
        obs, sigma = env.observe()
        if self.prediction is None:
            self.prediction = obs

        # Recurrent perceptual settling (RPT/predictive coding): the percept is
        # not the raw observation. Starting from the bottom-up signal, it
        # relaxes over several feedback iterations toward a precision-weighted
        # fusion with the top-down prediction - noisier signal, more weight on
        # expectation. The settled percept is what the rest of the system sees.
        w_obs = (1.0 / sigma**2) / (1.0 / sigma**2 + 1.0 / self.PRIOR_SIGMA**2)
        target = (self.prediction + w_obs * ((obs - self.prediction + WORLD / 2) % WORLD - WORLD / 2)) % WORLD
        percept = obs
        for _ in range(3):
            percept = (percept + 0.6 * ((target - percept + WORLD / 2) % WORLD - WORLD / 2)) % WORLD

        # World model (predictive processing): track the resource, measure error.
        error = circ_dist(percept, self.prediction)
        self.prediction = (self.prediction + 0.5 * ((percept - self.prediction + WORLD / 2) % WORLD - WORLD / 2)) % WORLD
        model_true_error = circ_dist(self.prediction, env.resource)

        # Perception bids for the workspace; prediction error adds bottom-up salience.
        confidence = 1.0 / (1.0 + sigma)      # metacognition: less noise, more confidence
        salience = 0.4 + 0.15 * error

        # Competing internal bid (habituating self-reference, as in workspace.py).
        self_salience = 0.5 if not self.log else max(0.1, 0.5 - 0.02 * len(self.log))
        perception_won = salience >= self_salience

        # Broadcast: winning content becomes globally available - unless lesioned.
        if perception_won and not self.lesioned:
            self.broadcast_estimate = self.prediction

        # Agency: act on the broadcast with learned probability, else wander.
        if self.broadcast_estimate is not None and rng.random() < self.trust:
            action = toward(env.agent, self.broadcast_estimate)
            self.acted_on_broadcast = True
        else:
            action = rng.choice([-1, 0, 1])
            self.acted_on_broadcast = False

        reward = env.step(action)

        # Learning from feedback: credit whichever policy just ran.
        delta = reward - self.reward_baseline
        self.reward_baseline += 0.05 * delta
        if self.acted_on_broadcast:
            self.trust = min(0.98, max(0.02, self.trust + 0.02 * delta))
        else:
            self.trust = min(0.98, max(0.02, self.trust - 0.02 * delta))

        self.log.append({
            "reward": reward,
            "confidence": confidence,
            "perceptual_error": circ_dist(obs, env.resource),
            "settled_error": circ_dist(percept, env.resource),
            "prediction_error": error,
            "model_true_error": model_true_error,
            "perception_won": perception_won,
            "acted_on_broadcast": self.acted_on_broadcast,
        })


def run(ticks: int, seed: int, lesioned: bool) -> Agent:
    rng = random.Random(seed)
    env = Env(random.Random(seed + 1))
    agent = Agent(lesioned=lesioned)
    for _ in range(ticks):
        agent.tick(env, rng)
    return agent


def mean_reward(agent: Agent, tail: int | None = None) -> float:
    rewards = [t["reward"] for t in agent.log]
    return statistics.fmean(rewards[-tail:] if tail else rewards)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ticks", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    intact = run(args.ticks, args.seed, lesioned=False)
    lesioned = run(args.ticks, args.seed, lesioned=True)

    # -- measurements ------------------------------------------------------
    r_intact, r_lesion = mean_reward(intact), mean_reward(lesioned)
    workspace_gain = r_intact - r_lesion

    conf = [t["confidence"] for t in intact.log]
    err = [t["perceptual_error"] for t in intact.log]
    calibration = -statistics.correlation(conf, err)  # confidence should track accuracy

    early = mean_reward(intact, tail=None)
    late = mean_reward(intact, tail=args.ticks // 4)
    learning_gain = late - statistics.fmean([t["reward"] for t in intact.log[: args.ticks // 4]])

    naive_err = statistics.fmean(t["perceptual_error"] for t in intact.log)
    settled_err = statistics.fmean(t["settled_error"] for t in intact.log)
    model_err = statistics.fmean(t["model_true_error"] for t in intact.log)

    rows = [
        ("GWT: limited-capacity workspace", "one coalition broadcast per tick, by construction", "PASS"),
        ("GWT: global broadcast is load-bearing",
         f"mean reward {r_intact:+.3f} intact vs {r_lesion:+.3f} lesioned (gap {workspace_gain:+.3f})",
         "PASS" if workspace_gain > 0.1 else "FAIL"),
        ("PP: predictive world model",
         f"model tracks truth at error {model_err:.2f} vs {naive_err:.2f} for a raw observation",
         "PASS" if model_err < naive_err else "FAIL"),
        ("HOT: metacognitive calibration",
         f"confidence tracks accuracy, r = {calibration:+.2f}",
         "PASS" if calibration > 0.2 else "FAIL"),
        ("AST: attention schema", "self-model of workspace state, with habituation (see workspace.py)", "PASS"),
        ("AE: learned agency",
         f"trust in broadcast learned to {intact.trust:.2f}; late-run reward {learning_gain:+.3f} vs early",
         "PASS" if intact.trust > 0.6 else "PARTIAL"),
        ("AE: embodiment", "acts in a world whose feedback shapes it - but the world is 24 cells", "PARTIAL"),
        ("RPT: recurrent perceptual settling",
         f"top-down feedback sharpens perception: settled error {settled_err:.2f} vs raw {naive_err:.2f} "
         "(algorithmic recurrence at toy scale)",
         "PASS" if settled_err < naive_err else "FAIL"),
        ("Rich, unified, temporally thick experience-like state", "nothing here answers to this", "FAIL"),
    ]

    print("=== indicator scorecard (third-person tests; rerun with any --seed) ===\n")
    for name, evidence, verdict in rows:
        print(f"[{verdict:^7}] {name}")
        print(f"          {evidence}\n")

    passes = sum(1 for r in rows if r[2] == "PASS")
    print(f"{passes} PASS / {sum(1 for r in rows if r[2] == 'PARTIAL')} PARTIAL / "
          f"{sum(1 for r in rows if r[2] == 'FAIL')} FAIL of {len(rows)} indicators\n")

    print("=== the ceiling ===")
    print(
        "Every test above is third-person and functional - which is all any\n"
        "outside actor can ever run, on this program or on another person.\n"
        "Passing all indicators would make a system what Butlin et al. call a\n"
        "'serious candidate', not a verified conscious being. Confidence that\n"
        "there IS consciousness, as opposed to confidence that the functional\n"
        "signatures of consciousness are present, is not obtainable from the\n"
        "outside. This scorecard is the honest maximum."
    )


if __name__ == "__main__":
    main()
