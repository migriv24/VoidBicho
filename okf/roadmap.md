---
type: Roadmap
title: Roadmap
description: The rungs, ordered so each pays for itself alone. Everything here is planned; nothing is built, and Void Palabra is being built first.
tags: [status:planned, audience:dev, confidence:tentative, roadmap]
timestamp: 2026-07-27T00:00:00Z
---

**Nothing in Void Bicho is built, and it is not next.** By the author's ruling
(2026-07-27), **Void Palabra is developed first**. This bundle exists now so the
[boundary](/design/boundaries.md) is settled before either side grows a shape the
other cannot use — which is cheap today and expensive later.

The ordering rule, inherited from Palabra:

> **Every rung must earn its keep with one model on one device.**
>
> If a step is only valuable once a mesh exists, or once Palabra exists, it is
> scheduled too early. Bicho must be worth having alone or it is not worth having.

---

# Not blocked on anything

Worth stating, because Palabra opens with three Core blockers and Bicho has none.
Bicho needs **no change to Void Core**: the effect seam exists, `effect <op>` routes
arbitrary host operations, `tag_match` is exposed over the FFI, and a `model` glyph is
registrable today. Everything below could start the moment attention is available.

The one soft dependency is on **Palabra's block store**
([runtime](/concepts/runtime.md)) — and it is soft by design: absent one, Bicho falls
back to hashed files on disk.

---

# Phase 0 — the model catalogue

**The cheapest genuinely useful thing, and it involves no inference at all.**

1. The `model` glyph and the `models` mantle
   ([model](/concepts/model.md)).
2. Facet and tag conventions — the axes that make `find "vision AND local"` work.
3. `describe()` over a catalogue: what this device *could* run, and what it *can*
   right now.

**Pays for itself with zero models loaded:** it is the answer to "what have I got,
and where did it come from," which is currently a folder of files with confusing
names. It is also pure data modelling, so it de-risks everything after it by settling
the vocabulary first — the same argument Palabra's Rung 0 makes.

---

# Phase 1 — one invocation, honestly

1. The [invocation](/concepts/invocation.md) request/response shape, **including
   refusal** ([budget](/concepts/budget.md)) from the start rather than bolted on.
2. One local backend behind it. *Revised 2026-10-10:* the first two are **ONNX Runtime**
   (a small perception model, MobileSAM, on CPU; [perception](/concepts/perception.md)) and
   **Needle's C++ engine** (tool routing, structured extraction, embeddings; [Needle](/design/needle.md)),
   because those are what Void Squid will actually call first and both run on this laptop's
   CPU. llama.cpp / GGUF follows for a general language model.
3. The provenance stamp.
4. Cost measurement — actual, and separately, estimate.

**Testable with one model and no network.** This is where the design is validated: if
`model`, `params`, `cost`, `stopped` and `deterministic` can all be filled in
honestly for a real backend, the contract is real. If a field cannot be defended, it
should not be in the response type.

---

# Phase 2 — residency

1. Load, unload, keep-warm.
2. Sessions as a **droppable** optimization ([runtime](/concepts/runtime.md)).
3. Eviction — **gated on [open questions](/design/open-questions.md) §3**, which asks
   whether Bicho may have a policy at all.

**Pays for itself immediately:** the difference between a 4-second and a 40-second
first token.

---

# Phase 3 — the other two backends

1. **Remote** (an OpenAI-shaped HTTP surface). Brings real `spend`, so
   [open questions](/design/open-questions.md) §4 must be answered first.
2. **Peer** — reaching a model on another device. **This is the rung where Palabra
   becomes useful**, via the capability declaration, and it is deliberately last
   because everything before it works with no mesh at all.

---

# Phase 4 — pipelines

[Pipeline](/concepts/pipeline.md), starting with retrieval
(`embed → search → assemble → generate`). Furthest out and most speculative. The
`assemble` stage is where Palabra's *prompt-is-a-scry* becomes literal, so this rung
is genuinely better if Palabra exists — the only one that is.

---

# Explicitly out of scope

- **Training and fine-tuning.** Bicho loads an adapter; it does not make one.
- **Agent frameworks** — planners, tool loops, memory managers. Core already rules
  that memory is a rune and tools are app-defined.
- **Scheduling and prioritization.** Latin-OS's ([boundaries](/design/boundaries.md) §4.1).
- **Writing inference kernels.** If this is ever on the table, the railguard failed.

---

# Research to do before Phase 1

1. **Re-verify [prior art](/references/prior-art.md)** — it was written from existing
   knowledge and not freshly fetched. Do this before depending on any detail in it.
2. **Check what llama.cpp will actually promise about determinism** — decides whether
   [open questions](/design/open-questions.md) §5 has a good answer or an honest
   `false` forever.
3. **Read Ollama's residency policy**, which is the closest working answer to Phase 2
   and probably worth copying rather than deriving.
4. **Confirm `effect` is enough** ([open questions](/design/open-questions.md) §2) —
   if it is, Bicho ships with no command surface of its own, which would be a
   genuinely good outcome and is worth trying to falsify early.
