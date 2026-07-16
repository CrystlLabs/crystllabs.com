---
title: I Picked My Tour de France Fantasy Team With a Real Quantum Computer. It Told Me Not to Buy Pogačar.
date: 2026-07-16
summary: I optimized my Tour de France fantasy roster with real IBM quantum hardware: gate-based QAOA, not a hybrid solver. A provably lossless 172-to-45 rider reduction, an exact classical ILP baseline, and four real QPU jobs later, the optimal team benches Pogačar, and a trained 21-qubit circuit found that exact optimum twice through the noise.
tags: Quantum Computing, QAOA, Optimization
---
My Velogames league has one rule: no AI for picks. Fair enough. So I didn't use AI. I used a quantum computer.

Not a hybrid cloud service that quietly does most of the work classically. Gate-based QAOA on IBM's actual hardware, the kind with a Hamiltonian you build yourself and a job queue you wait in.

## The problem

Velogames TdF is a knapsack problem wearing a cycling jersey:

- Pick 9 riders from the pool (172 this year)
- Stay under 100 credits
- Class quotas: 2 All-Rounders, 2 Climbers, 1 Sprinter, 3 Unclassed, 1 Wildcard (any class)
- Maximize projected points

Riders are binary, in or out, and 172-choose-9 is over 10^15 combinations. Classic combinatorial optimization, exactly the shape of problem QAOA is built to attack.

## Formulating it as a QUBO

Quantum hardware doesn't take "pick 9 riders under budget" as input. It takes a QUBO: Quadratic Unconstrained Binary Optimization. Each rider is a binary variable, and every constraint becomes a penalty term:

```
H = -Σ pointsᵢ·xᵢ
    + λ_count (Σxᵢ - 9)²
    + λ_budget max(0, Σcostᵢxᵢ - 100)²
    + λ_class (per-class quota miscounts)²
```

Tuning the λ weights is a real part of the work. Too low and the solver ignores the budget; too high and it stops caring about points and hands you any feasible squad. I set them so that any single violation costs more than the best rider in the race is worth (λ_count 3000, λ_budget 60).

## The projections

The quantum computer doesn't know who's good, and it doesn't know Velogames' scoring rules either. Both get fed in explicitly. The scoring tables (stage results top 20, daily GC, KOM and points classifications, intermediate sprints, summit bonuses, breakaway points, teammate assists, end-of-tour bonuses) are fact, pulled from the official rules. Everything on top is a model, and a model can be wrong. Worth keeping those two separate.

The model: last three seasons of results per rider, 2026 form, course fit (mountain stages, time-trial kilometers, sprint finishes) mapped against each rider's role, breakaway habits, and a team-assist component, because Velogames pays teammates when a leader scores (riding for UAE is worth about 204 assist points; Lidl-Trek 154; Visma 108).

Top of the board: Pogačar 2565, Vingegaard 1891, Evenepoel 1406, Ayuso 1182. Remember those, because the punchline is coming.

## Making it fit

IBM's free-tier machines are 156 qubits, and every rider is a qubit. 172 riders do not fit.

The plan was heuristic: prune "dominated" riders until the problem fits. What I actually found is better, a pruning rule that is provably lossless. Within each (class, cost) group, at most quota+1 riders can ever appear in a legal team (the quota plus the one wildcard slot), and if two riders have the same class and the same cost you always prefer the higher projection. Keep only the top quota+1 per group and you have thrown away nothing, exactly.

- 172 riders → 45 riders. Plus 4 wildcard slack bits and 5 budget slack bits: 54 qubits total.
- Control check passed: the exact ILP on the pruned pool reproduces the full-pool optimum of 8014.0 to the decimal. Zero loss.

Half the work in "quantum computing" is deleting variables until the problem fits on the quantum computer. The other half is proving the deleting didn't change the problem.

## The classical answer, and the Pogačar problem

Before any qubits: greedy gets 6846 points for 86 credits. The exact ILP (PuLP, about 1 second on my laptop) gets 8014 for a full 100.

And the optimal team does not contain Pogačar. The highest-projected rider in the race, the guy winning everything, is not worth 34 credits, because those credits buy Vingegaard (24) plus most of Evenepoel (16), and the rest of the budget assembles a Lidl-Trek assist stack around Ayuso, Pedersen, and Skjelmose. Value per credit beats star power. My model says so, anyway.

The optimal nine:

| Rider | Team | Class | Cost |
|---|---|---|---|
| Jonas Vingegaard | Team Visma \| Lease a Bike | All-Rounder | 24 |
| Remco Evenepoel | Red Bull - BORA - hansgrohe | All-Rounder | 16 |
| Juan Ayuso | Lidl - Trek | Climber | 12 |
| Lenny Martinez | Bahrain - Victorious | Climber | 10 |
| Mads Pedersen | Lidl - Trek | Sprinter | 10 |
| Mattias Skjelmose | Lidl - Trek | Wildcard (All-Rounder) | 10 |
| Thomas Pidcock | Pinarello-Q36.5 Pro Cycling Team | Unclassed | 10 |
| Edoardo Affini | Team Visma \| Lease a Bike | Unclassed | 4 |
| Sean Quinn | EF Education - EasyPost | Unclassed | 4 |

Total: 100/100 credits, 9/9 slots, quotas satisfied exactly. Projected 8014 points, provably optimal under my projections. No Pogačar.

## QAOA in one paragraph

QAOA is a circuit that alternates two kinds of layers, p times over: a "cost" layer that phases each measurement outcome by its energy under my QUBO (nudging the state toward low-energy, high-scoring teams), and a "mixer" layer that shuffles amplitude between outcomes so it can move. Each layer has an angle, a classical optimizer tunes the angles, and at the end you measure a few thousand times and hope the good bitstrings come out more often than chance. It is a heuristic. It carries no optimality certificate. It is, in the strict sense my league banned, still not AI.

The catch: the angles need training, and training means simulating the circuit, which you cannot do at 54 qubits. That circularity is the actual story of this experiment.

## Running it on real hardware

The free tier (IBM Open Plan, 10 QPU minutes a month) currently offers three 156-qubit Heron machines: ibm_fez, ibm_kingston, ibm_marrakesh. qiskit 2.5.0, qiskit-ibm-runtime 0.48.0.

Now the horror-story number. My QUBO is about 90% dense, because the team-size and budget constraints couple every rider to every other rider, and dense problems route badly on heavy-hex chips. The p=2 circuit for ibm_kingston transpiled to total depth 4282 and two-qubit depth 1517 in the dry run, and the production job came out even worse: 5608 and 2022. That is far beyond what survives coherence. Honest pre-registration, written down before the QPU job: I expect the raw 54-qubit hardware output to be indistinguishable from noise.

So the experiment is two-tier:

- **Tier A, the honest full-scale attempt.** All 54 qubits, training-free "linear ramp" angles (a discretized annealing schedule), post-select the shots that decode to legal teams, and grade against a null hypothesis: density-matched random guessing, each rider bit on with probability 9/45. The random control over 8192 shots: 1.83% of samples feasible, best feasible team 6461 points, 19.4% below optimum. If the hardware can't beat that, the hardware ran a very expensive random number generator.
- **Tier B, where QAOA gets a fair fight.** A 12-rider mini-instance (the ILP-optimal nine plus three decoys), 21 qubits, small enough to brute-force and to actually train the angles on a simulator, then run the trained circuit on hardware.

One war story from the training: Qiskit's generic statevector estimator was unusably slow (it exponentiates a sparse matrix per objective evaluation), so I wrote a custom exact simulator. The cost Hamiltonian is diagonal, so the cost layer is just a precomputed phase vector and the mixer is axis-wise RX. Milliseconds per evaluation, training (p=2, COBYLA, 5 restarts) done in seconds. On the noiseless simulator the trained circuit gets 7.67% of shots feasible and lands on the exact optimum state in 0.134% of shots, 5.6× more often than chance. That's the ceiling. Then the queue: each hardware job waited about 12.5 minutes to run for a handful of seconds.

## Results

Four jobs in the end: each circuit ran on ibm_kingston, and duplicates ran on ibm_fez after a five-and-a-half-hour queue, which amounts to a free cross-chip replication. Grand total: 17 seconds of QPU out of my 10 free monthly minutes.

| Approach | Best (model pts) | Budget | Feasible samples | Gap vs ILP | Solve time |
|---|---|---|---|---|---|
| Greedy | 6846 | 86 | — | 14.6% | <1 s |
| ILP (PuLP, exact) | 8014 | 100 | — | 0 | ~1 s |
| Random control (density-matched, 54q) | 6461 | 100 | 1.83% | 19.4% | <1 min |
| QAOA trained, simulator (21q mini) | 8014 | 100 | 7.67% | 0, exact optimum | seconds |
| QAOA trained, ibm_kingston (21q mini) | **8014** | 100 | 1.15% | 0, exact optimum | 3 s QPU + 12.5 min queue |
| QAOA trained, ibm_fez (21q, same params) | 7615 | 96 | 0.93% | 5.0% | 3 s QPU + 5.4 h queue |
| QAOA linear ramp, ibm_kingston (54q) | 3899 | 76 | 0.024% | 51.4% | 6 s QPU + 12.5 min queue |
| QAOA linear ramp, ibm_fez (54q) | none | — | 0% (0/8192) | — | 5 s QPU + 5.4 h queue |

Tier B first, because it's the good news. The trained 21-qubit circuit, at transpiled two-qubit depth 346, ran on real hardware and its best feasible sample was the exact optimum team: Vingegaard, Evenepoel, Skjelmose, Ayuso, Martinez, Pedersen, Pidcock, Quinn, Affini, all 8014 points of it. Noise did real damage. Feasibility collapsed from 7.67% to 1.15%, which is statistically the same as random guessing (1.33% on this instance). But the exact optimum state showed up 2 times in 4096 shots, 2.0× the random expectation. Read that carefully: most of the trained advantage died in the noise, and a faint, real preference for the right answer survived it. A quantum computer found my optimal fantasy team. Twice. Out of four thousand and ninety-six attempts.

This is what that circuit actually looks like after transpilation, the 21-qubit trained circuit as routed for ibm_fez (job d9bqia66hjac73fg2ptg):

![Transpiled 21-qubit QAOA circuit for ibm_fez, job d9bqia66hjac73fg2ptg](quantum-tour-de-france-fantasy-circuit.png)

*The opening bars, anyway. The full diagram is 95,000 pixels wide.*

Tier A is the pre-registered bad news, delivered on schedule. At two-qubit depth 2022, the 54-qubit machine is fully decohered: 2 feasible teams in 8192 shots (0.024%), best one worth 3899 points, a 51% gap, spending only 76 of 100 credits. It lost to the random control on every number. One nerdy nuance worth keeping: against a *strictly uniform* null (where hitting exactly 9-of-45 rider bits has probability around 0.0025%), the hardware's 0.024% is actually about 10× above chance, so a ghost of the mixer's density bias may survive. But density-matched random is the fair comparison, and against it the QPU is an expensive random number generator with a queue. Choose your null hypothesis honestly; it decides your conclusion.

Then the replication, which is where NISQ gets philosophical. Same circuits, same trained parameters, second chip. On the 21-qubit instance, ibm_fez (two-qubit depth 360, nearly identical to kingston's 346) did *not* find the optimum. Best sample 7615, one rider swap off (a Kanter wildcard configuration instead of Skjelmose), 0.93% feasible. So the exact-optimum hit is a kingston result, not a reproducible law of nature: at this depth, which chip you land on is a real experimental variable. And the 54-qubit run delivers the punchline in reverse. Fez actually routed the circuit *shallower* (two-qubit depth 1373 vs kingston's 2022) and got zero feasible teams in 8192 shots. A shallower circuit, on a different chip, did strictly worse. Once you're past the coherence cliff, feasibility isn't a function of circuit quality anymore. It's weather.

## The honest part

The ILP solved the exact problem in about 1 second on a laptop, provably optimally. The full-scale quantum run cost 12.5 minutes of queue and 6 seconds of QPU to produce a squad 51% below optimum at a 0.024% feasibility rate. Classical wins, decisively, and the physical reason is depth: gate-model NISQ pays for every constraint in circuit depth and noise, and my 90%-dense constraint structure alone transpiled to two-qubit depth 2022. The one quantum result worth keeping is the small one: at 21 qubits, where the circuit is shallow enough to partly survive, the trained QAOA really did surface the true optimum through the noise.

Also honest: nothing here needed a quantum computer, and four jobs is not statistics. The 2.0× optimum-state signal is literally 2 counts, and the ibm_fez replica didn't reproduce the exact-optimum hit. Kingston's result might be signal; it might be a lucky Wednesday. The full accounting: 4 hardware jobs, 2 backends, 17 seconds of quantum compute, and the longest queue was 5.4 hours for 3 seconds of it.

One documented wart: the budget slack bits cover 0–62 credits of headroom in steps of 2, so teams costing under 38 credits get mis-penalized by the QUBO. Doesn't matter near the optimum (which spends all 100), but it's the kind of encoding fine print a managed hybrid solver would have handled silently, and doing it by hand is how you find out it exists.

Why do it anyway: the assist-scoring rules make rider correlations genuinely quadratic, and that's the regime QUBO-native methods are built for. One budget constraint over 172 riders will never trouble an ILP, but a season-long version of this problem, every rider in every race with team-assist and breakaway correlations across thousands of rider-race pairs, is dense-quadratic at a scale where exact solvers start paying for every cross term and a sampler that natively speaks QUBO stops looking silly. Not this year's hardware. But the formulation is already the right one.

## The point

The exact optimum team, the one a real quantum computer found twice in 4096 shots through a wall of noise, does not include the best cyclist on Earth. The quantum computer and my laptop agree on the same uncomfortable conclusion: don't buy Pogačar.

Three weeks in France now get to grade that answer.
