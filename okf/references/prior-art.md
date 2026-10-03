---
type: Reference
title: Prior art
description: What already exists to borrow, what each one settles, and the small part that is genuinely Bicho's. Surveyed at founding from existing knowledge, not freshly verified.
tags: [status:planned, audience:dev, confidence:tentative, reference]
timestamp: 2026-07-27T00:00:00Z
---

**Verification status.** Surveyed 2026-07-27 from existing knowledge, **not freshly
fetched** — unlike `VoidPalabra:/references/academic-foundations.md`, which was. Treat
version numbers and current-state claims as needing a check before anything is built
on them. The *shapes* below are stable enough to reason with; the details are not.

**The honest position:** almost none of Bicho is novel. Inference engines, model
registries, routers and prompt frameworks all exist and are mature. Bicho's
contribution is a **vocabulary** that makes them addressable from Void Core's data
model — and if that vocabulary ever requires writing an inference kernel,
[boundaries](/design/boundaries.md) has been crossed.

---

# Local inference: llama.cpp / GGUF, ONNX Runtime

**llama.cpp** and the **GGUF** format are the de-facto substrate for running language
models on ordinary hardware: quantization from ~2 to 8 bits, CPU and GPU, a stable
single-file weight format, and bindings in every language.

**ONNX Runtime** is the right answer for the small non-LLM bichos —
[model](/concepts/model.md)'s `embed`, `classify`, `asr` kinds — where a whole LLM
stack is absurd overhead.

**Settles:** local execution entirely. Bicho writes **no** inference code.
**Leaves open:** nothing about *selection*, *budgets* or *provenance*, which is
exactly the gap Bicho fills.

---

# Model management: Ollama, LM Studio, HuggingFace Hub

**Ollama** is the closest thing to a working answer for the acquisition/residency
half of [runtime](/concepts/runtime.md): pull by name, keep-warm, unload on idle, a
local HTTP surface. **HuggingFace Hub** is where weights actually come from, with
content-addressed blobs and resumable fetch already solved.

**Settles:** the shape of acquisition and residency, and the fact that keep-warm +
idle-unload is the policy people actually want.
**Leaves open:** their model identity is a **string** (`llama3:8b`), and their
metadata is a flat file. That is precisely what [model](/concepts/model.md) replaces
with a rune — and the difference is not cosmetic: a string cannot be tagged,
queried, versioned, attributed, or synced, and a rune can be, using machinery that
already exists.

---

# Routing and gateways: LiteLLM, OpenRouter

Unify many providers behind one API, with fallback chains, cost tracking, and
per-key budgets. **The closest existing thing to Bicho's whole remit**, and worth
studying closely.

**Settles:** that cost tracking and budget enforcement at the call site is
practical, and that one vocabulary over many backends works.
**Leaves open:** these are **routers with opinions** — they substitute models to save
money, which [boundaries](/design/boundaries.md) §6 explicitly refuses. Take the cost
accounting; leave the automatic substitution. The disagreement is Core's honesty
principle: a silently cheaper model is a silent wrong answer.

---

# Prompt and pipeline frameworks: LangChain, DSPy, Haystack

**DSPy** is the interesting one — it treats a pipeline as a **program to be
optimized** rather than a string to be tuned, which is a genuinely better framing than
most of the field.

**Settles:** that multi-stage composition is a real need and that a declarative
graph beats imperative glue.
**Leaves open:** all of them invent their own graph representation. **Void Core
already has one** — a mantle with `layout.edges` — so [pipeline](/concepts/pipeline.md)
should borrow the *idea* and none of the *machinery*. This is the single place where
Bicho's Void Core inheritance is a real advantage over the field rather than a
constraint.

---

# The world-model side: DINO, JEPA

Assessed at length in `VoidPalabra:/design/world-models.md`, which rejected three
proposed uses and identified four narrow ones. For Bicho the conclusion is
deliberately boring: **a world model is a [model](/concepts/model.md) with
`kind: "world"`** — a rune, a runtime, a budget, a stamp.

**Settles:** nothing about Bicho's design; it was already general enough.
**Leaves open:** whether `world` models need an [invocation](/concepts/invocation.md)
shape different from token-in/token-out. They predict *embeddings*, so probably the
`embed` shape, but this has not been checked.

---

# What is genuinely Bicho's

Stated plainly so it is not mistaken for more than it is:

1. **A model as a rune, selected by tag query.** Everyone else uses a string. This is
   the one real idea, and it is only available because Core's tag grammar exists.
2. **Refusal as a value, with an estimate attached** — rather than an exception or a
   silent downgrade ([budget](/concepts/budget.md)).
3. **The provenance stamp meeting Palabra's addressable prompt.** Jointly, a
   reproducible agent run: exact input state recoverable by hash, exact model and
   parameters recorded beside it. Neither library can do this alone, and the seam
   between them costs neither a dependency.

(3) is the only one that is genuinely unbuilt anywhere, and it is unbuilt because it
requires a version-control system with content-addressed cuts sitting next to a model
runner — which is a combination nobody has had a reason to build.
