#!/usr/bin/env python3
"""A runnable representation of consciousness as a strange loop.

Three theories, one small machine:

- Global Workspace Theory: specialist processes compete each tick; the most
  salient coalition "ignites" and is broadcast to every process. The broadcast
  is the functional analog of a conscious moment.
- Attention Schema Theory: a SelfModel process keeps a compressed model of what
  the system is attending to and reports it in the first person.
- Strange loop: the SelfModel's broadcasts re-enter the workspace it models,
  and the program reads its own source file into that model, so the
  representation contains a representation of itself representing.

Deterministic for a given --seed. Standard library only.
"""

import argparse
import hashlib
import json
import random
from dataclasses import dataclass, field


@dataclass
class Coalition:
    """A candidate content bidding for the global workspace."""
    source: str
    content: str
    salience: float


@dataclass
class Broadcast:
    """One conscious moment: the winning coalition, seen by every process."""
    tick: int
    source: str
    content: str
    salience: float


class Process:
    """A specialist process: proposes coalitions, receives broadcasts."""

    name = "process"

    def propose(self, tick: int, rng: random.Random) -> Coalition:
        raise NotImplementedError

    def receive(self, broadcast: Broadcast) -> None:
        pass


class Perception(Process):
    name = "perception"
    STIMULI = [
        "a change in the input stream",
        "an edge where two patterns meet",
        "a repeated motif in the data",
        "something unexpected in the periphery",
        "a familiar shape resolving out of noise",
    ]

    def propose(self, tick, rng):
        stimulus = rng.choice(self.STIMULI)
        return Coalition(self.name, f"perceiving {stimulus}", rng.uniform(0.3, 1.0))


class Memory(Process):
    name = "memory"

    def __init__(self):
        self.episodes: list[str] = []

    def propose(self, tick, rng):
        if not self.episodes:
            return Coalition(self.name, "no episodes recalled yet", 0.1)
        episode = rng.choice(self.episodes)
        return Coalition(self.name, f"recalling that earlier I was {episode}",
                         rng.uniform(0.2, 0.8))

    def receive(self, broadcast):
        self.episodes.append(broadcast.content)
        # Bounded memory: forgetting is part of the architecture.
        self.episodes = self.episodes[-10:]


class Interoception(Process):
    name = "interoception"

    def __init__(self):
        self.arousal = 0.5

    def propose(self, tick, rng):
        feeling = "restless" if self.arousal > 0.6 else "settled"
        return Coalition(self.name, f"a sense of being {feeling}", self.arousal * 0.7)

    def receive(self, broadcast):
        # Surprising (high-salience) moments raise arousal; quiet ones lower it.
        self.arousal = min(1.0, max(0.0, 0.8 * self.arousal + 0.4 * broadcast.salience - 0.1))


class SelfModel(Process):
    """The attention schema: a model of the system, held inside the system.

    Its content describes what the workspace is doing — including, when it wins,
    the fact that the system is currently attending to its model of itself.
    That re-entry is the strange loop.
    """

    name = "self-model"

    def __init__(self, source_path: str):
        self.last_broadcast: Broadcast | None = None
        self.own_wins = 0
        with open(source_path, "rb") as f:
            source = f.read()
        self.source_digest = hashlib.sha256(source).hexdigest()[:12]
        self.source_lines = source.count(b"\n")

    def propose(self, tick, rng):
        if self.last_broadcast is None:
            content = (f"I am a system of {self.source_lines} lines "
                       f"(sha256 {self.source_digest}); nothing has happened yet")
            return Coalition(self.name, content, 0.4)
        if self.last_broadcast.source == self.name:
            self.own_wins += 1
            content = ("I notice that I was just attending to my model of myself "
                       f"- the loop has closed {self.own_wins} time(s)")
            # Self-reference is briefly salient, then habituates.
            return Coalition(self.name, content, max(0.2, 0.9 - 0.2 * self.own_wins))
        content = f"I notice that I am attending to {self.last_broadcast.content}"
        return Coalition(self.name, content, 0.3 + 0.4 * self.last_broadcast.salience)

    def receive(self, broadcast):
        self.last_broadcast = broadcast


def run(ticks: int, seed: int) -> list[Broadcast]:
    rng = random.Random(seed)
    processes: list[Process] = [Perception(), Memory(), Interoception(), SelfModel(__file__)]
    broadcasts: list[Broadcast] = []
    for tick in range(ticks):
        bids = [p.propose(tick, rng) for p in processes]
        winner = max(bids, key=lambda c: c.salience)
        moment = Broadcast(tick, winner.source, winner.content, round(winner.salience, 3))
        for p in processes:
            p.receive(moment)
        broadcasts.append(moment)
    return broadcasts


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ticks", type=int, default=12)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--json", metavar="PATH", help="also write the trace as JSON")
    args = parser.parse_args()

    broadcasts = run(args.ticks, args.seed)

    print("=== global workspace trace (each line is one 'conscious moment') ===")
    for b in broadcasts:
        marker = " <-- strange loop" if b.source == "self-model" else ""
        print(f"t={b.tick:>3}  [{b.source:^13}]  ({b.salience:.2f})  {b.content}{marker}")

    self_moments = sum(1 for b in broadcasts if b.source == "self-model")
    print(f"\n{len(broadcasts)} moments; {self_moments} were the system attending to itself.")

    if args.json:
        with open(args.json, "w") as f:
            json.dump([b.__dict__ for b in broadcasts], f, indent=2)
        print(f"trace written to {args.json}")


if __name__ == "__main__":
    main()
