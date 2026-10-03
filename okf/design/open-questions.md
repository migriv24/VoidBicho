---
type: Design
title: Open questions
description: What is genuinely undecided in Void Bicho, what blocks what, and who owns each answer. Decisions already made live in the concept pages, not here.
tags: [status:planned, audience:dev, confidence:tentative]
timestamp: 2026-07-27T00:00:00Z
---

Only genuinely open items belong here. Settled decisions (a model is a rune; refusal
is a value; Bicho does not schedule; neither sibling imports the other) are recorded
in the concept pages and in [boundaries](/design/boundaries.md).

Ordered by **what blocks what**, not by interest.

---

# 1. Naming — the vocabulary (author's call)

Concept names are descriptive placeholders, following Void Palabra's precedent. The
project name itself suggests the flavored set, and *bicho* is doing real work
already: a model is a **bicho** you keep and feed. Candidates, none adopted:

| concept | descriptive (current) | possible |
|---|---|---|
| a model | model | *bicho* |
| a loaded instance | residency | *nido* (nest) |
| one call | invocation | — |
| a multi-stage graph | pipeline | — |

**Blocks nothing technically; blocks the verb surface.** Cheap now, expensive once
applications depend on it.

---

# 2. Does Bicho need dispatcher verbs, or is `effect` enough? **(blocks the surface)**

Core's generic `effect <op> [args…]` verb already routes arbitrary host operations
through the effect seam and returns the result as `data`. So `effect infer "…"` works
**today**, with no change to Core and no new verb.

The question is whether that is sufficient or merely possible:

- **If `effect` is enough** — Bicho ships as a host-side library plus an effect
  handler, and adds nothing to any command surface. Cheapest, and it keeps Bicho out
  of Core entirely.
- **If verbs are needed** — agents must be able to *discover* models, not just call
  them, and `find "vision AND local"` over a `models` mantle is already the discovery
  path ([model](/concepts/model.md)). That argues **no new verbs are needed for
  discovery either**, which is a surprisingly strong result if it holds.

**Leaning: `effect` is enough**, which would make Bicho the first Void library that
needs no vocabulary of its own. Worth trying to falsify before assuming.

---

# 3. May Bicho have an eviction policy at all? **(the railguard's edge case)**

VRAM is finite and indivisible, so *something* must decide what to unload. But an
eviction policy is a resource-allocation decision, which is
[boundaries](/design/boundaries.md) §4.1's forbidden territory wearing a different
hat.

The distinction that probably saves it: **eviction is local and reactive** (this
device, right now, out of memory), while **scheduling is global and predictive**
(who runs next, across devices). Local reactive policy looks acceptable; a policy
that *anticipates* demand does not.

Not decided. It is the sharpest test of whether the railguard is well-drawn, and it
should be settled before [runtime](/concepts/runtime.md) is built rather than
discovered during.

---

# 4. What is the honest unit of `spend`?

Money is straightforward for remote backends and meaningless for local ones — but
local is not free, it is *prepaid* (hardware) plus electricity plus opportunity cost
plus, on a phone, battery the user will notice.

If `spend` is money-only, then local models appear free and applications will make
bad choices. If it is a synthetic unit, it is comparing things that are not
comparable and will be quietly wrong.

Directions, none verified: separate incomparable dimensions and refuse to sum them;
a caller-supplied exchange rate; report all dimensions and let the caller collapse
them. **Blocks** [budget](/concepts/budget.md)'s enforcement shape.

---

# 5. Determinism — how hard should Bicho try?

[Invocation](/concepts/invocation.md) requires `deterministic` to be a **defensible
claim**, not a hope. But defending it is real work: fixed seed, greedy decode,
deterministic kernels, pinned backend version, identical quantization — and some
backends cannot promise it at any price.

Open: whether Bicho offers a `--deterministic` mode that *fails* rather than
silently degrading, and how much of the stack it must pin to be entitled to say
`true`. This matters more than it looks, because it is the difference between
Palabra's reproducible-agent-run property being real or decorative.

---

# 6. Where does a model's *evaluation* live?

*"Is this bicho any good at this task"* is a real question with a real answer shape
(a benchmark is a mantle of cases; a score is a rune). It is also unbounded scope and
adjacent to training, which [boundaries](/design/boundaries.md) §6 excludes.

Not answered. Recorded because the pull toward it will be strong the moment two
models are installed.

---

# 7. What Bicho does *not* answer yet

- **Training and fine-tuning.** Out of scope at founding. Core's
  `VoidCore:/design/needle-finetune.md` is the one live track and it is Core's.
- **Tool-calling loops and agent planning.** Not Bicho's
  ([boundaries](/design/boundaries.md) §6); the app builds those from ~40 tools over
  dispatcher verbs, per `VoidCore:/design/agent-tools-memory.md`.
- **Multi-tenancy.** Two applications on one device sharing one loaded model is
  obviously desirable and obviously a scheduling problem. Deferred with §3.
- **Whether Needle ships with Bicho or with Core.** Needle is Core's design; if it
  becomes the default rune-sized agent, the packaging question is real and unowned.
