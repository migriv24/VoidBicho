---
type: Concept
title: Runtime
description: The backend seam — local weights, a model on another peer, and a paid API reached under one vocabulary. Where the weights live, and what "loaded" means.
tags: [status:planned, audience:dev, audience:library, confidence:tentative]
timestamp: 2026-07-27T00:00:00Z
---

A **runtime** is the thing that turns a [model](/concepts/model.md) rune into
something that can answer. It owns three jobs and no others:

1. **Acquisition** — getting the weights onto this device, verified.
2. **Residency** — loading, unloading, and knowing what is currently in memory.
3. **Execution** — one [invocation](/concepts/invocation.md), with a bound.

# Three backends, one vocabulary

The trap is to build for local weights and bolt on the rest. The three cases must be
peers from the start, because an application should be able to move between them by
editing tags — that is the payoff of a model being a rune.

| backend | weights live | cost is | fails by |
|---|---|---|---|
| **local** | on this device | electricity, RAM, time | OOM, missing file, no accelerator |
| **peer** | on another device in the mesh | someone else's electricity, plus latency | peer absent, capability withdrawn |
| **remote** | someone else's datacentre | **money**, per token | rate limit, quota, network, provider outage |

The failure columns are why `describe()` matters more here than anywhere else in
Void Core: *"no accelerator"*, *"peer asleep"* and *"out of credit"* are genuinely
different, and collapsing them into `error` is the silent-wrong-answer failure in a
new costume.

**The `peer` backend is where Palabra shows up and stops.** Bicho does not implement
peer-to-peer anything: it asks whoever is holding the connection *"who can run
`kind: llm, ctx≥8192`?"*, and in a deployment with Palabra present that question is
answered by a capability declaration
(`VoidPalabra:/concepts/peer-and-tier.md`). With no Palabra present, the same
backend can be pointed at a hostname by hand. Neither library imports the other —
see [boundaries](/design/boundaries.md) §3.

# Where the weights live — do not build a second blob store

Model weights are large, immutable, content-addressable, heavily deduplicated
between variants (same base, different adapter), and painful to re-download. That is
**exactly** the object `VoidPalabra:/concepts/persistence.md` is building
content-addressed block storage with prolly trees for, for unrelated reasons.

**Ruling at founding:** Bicho defines *what it needs from* a blob store — content
addressing, verification on read, dedup, resumable fetch, a pinning/eviction hint —
and **does not implement one**. Where no store is provided it falls back to files on
disk with a hash check, which is the honest 80% and roughly what every model loader
already does.

This is a *shape* agreement, not a dependency: Bicho names an interface, Palabra
happens to satisfy it, and a caller with neither still works.

# What "loaded" means, and why it is not versioned

A loaded model is **residency**, and residency is the one genuinely stateful thing in
Bicho:

- it consumes a resource that is not divisible (VRAM),
- loading is slow and unloading is fast,
- the useful policy is `keep-warm` with an eviction rule,
- and a KV cache is a **session**: a bounded, resumable, discardable thing attached
  to a conversation, not to a model.

None of this is versioned, synced, or historical. It is closer to Void Core's
`placement` — real state that is deliberately carved out of the undoable slice
because it is a view/runtime concern, not content. Palabra's compute page flags the
same question for agent working state, and the answer is likely the same.

**Explicitly not decided:** the eviction policy, and whether Bicho gets to have one
at all. An eviction policy is a scheduling decision with a different name, which is
uncomfortably close to [boundaries](/design/boundaries.md) §4.1 — see
[open questions](/design/open-questions.md) §3.

# What to borrow rather than write

Nearly all of this exists. See [prior art](/references/prior-art.md). The short
version: **llama.cpp / GGUF** for local, **ONNX Runtime** for the small non-LLM
bichos, an OpenAI-shaped HTTP surface for remote. Bicho's contribution is the
vocabulary above them, not a third inference engine — and if it ever starts writing
kernels, [boundaries](/design/boundaries.md)'s railguard has been crossed.

# Status

`planned`. Nothing built, and this page is `confidence:tentative` — the three-backend
split is confident, the residency model is a sketch.
