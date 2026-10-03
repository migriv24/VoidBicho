---
type: Design
title: Boundaries — what Bicho owns and what it refuses
description: The division of labour across Core, Palabra, Bicho and Latin-OS; why neither sibling library imports the other; and the two data shapes they agree on. The page to read before designing anything here.
tags: [status:planned, audience:dev, confidence:asserted, foundation]
timestamp: 2026-07-27T00:00:00Z
---

# Boundaries

> Void Core has a railguard (*"are we making the core compute the application's
> results?"*). Void Palabra has one (*"are we assuming an order we do not actually
> know?"*). This is Bicho's:
>
> **Are we deciding something a caller should have decided?**
>
> Bicho holds models, runs them, and reports what it cost. The moment it starts
> deciding *whether* something should run, *which* agent gets priority, or *what*
> the answer means, it has grown into a scheduler or an application, and should stop.

This page exists because Bicho sits between three other projects and the natural
drift is to absorb all of them. Every neighbouring concern below has an owner, and
none of them is Bicho.

---

## 1. The division, stated once

| question | owner | why not Bicho |
|---|---|---|
| what a rune, mantle or holiday *is* | **Void Core** | Bicho owns none of Core's vocabulary |
| which peer can run this? | **Palabra** | it is a capability declaration, and Palabra already declares tiers |
| what goes in the prompt? | **Palabra** | a prompt is a `scry` over a named cut; Core already has the operation |
| get the weights onto this device | **Bicho** | — |
| load, unload, quantize, pick a backend | **Bicho** | — |
| run it, once, with a bound | **Bicho** | — |
| what did it cost? | **Bicho** | it is the only party that knows |
| may I afford it? | **Bicho** *reports*, **caller** decides | see the railguard |
| record what happened, provably | **Palabra** | an utterance with provenance |
| *when* does this agent run at all? | **Latin-OS** | `LatinOS:/design/direction.md` §2 already designs it |
| what does the answer mean? | **the application** | Bicho returns bytes and numbers |

The last two rows are the ones that will be argued about. Both are refusals, and
both are load-bearing — see §4.

---

## 2. Why Bicho may compute, when Core may not

`VoidCore:/design/what-voidcore-is-not.md` forbids Core from computing the
application's results. Bicho appears to violate this and does not, for the same
reason Latin-OS does not: **the railguard bounds Void Core, not everything built on
it.** Bicho is a host-side library — the drift test's boundary does not break, it
moves to its correct place. Core describes and orchestrates; Bicho is one of the
things being orchestrated.

The precise statement: **Bicho is a holiday implementation**
(`VoidCore:/concepts/holiday.md`). Core's holiday page already names *LLM backends*
as a holiday kind
and defines the interface (`query`, `get`, `insert`, `describe`); the generic
`effect <op> [args…]` verb already routes arbitrary host operations through the
effect seam and returns the result as `data`. So Bicho needs **no change to Void
Core to be reachable** — which is the same thing that was true of Palabra's
persistence, and for the same reason.

---

## 3. Neither sibling imports the other

**Ruled at founding.** `VoidBicho` does not depend on `VoidPalabra`, and
`VoidPalabra` does not depend on `VoidBicho`. Both depend on Void Core.

The failure modes this avoids are concrete and symmetric:

- **If Bicho imported Palabra**, you could not run a model on a device that is not
  syncing anything — a single laptop with no peers would need a version-control
  library to summarize a document. Absurd, and it would kill the simplest use case.
- **If Palabra imported Bicho**, every peer in the mesh would need a model runtime
  to reconcile state. An ESP32 is a `State`-tier peer precisely so it can
  participate without carrying what it cannot hold; making inference a dependency of
  sync would undo that in one line.

### The two shapes they agree on

They meet as **shared vocabulary**, which is not a dependency because either side can
produce or ignore it without knowing the other exists.

**(a) The capability fragment.** Bicho can describe what it can run:

```jsonc
{ "kind": "llm", "id": "…", "ctx": 8192, "via": "<holiday>" }
```

Palabra's peer declaration embeds a list of these
(`VoidPalabra:/concepts/peer-and-tier.md`). Bicho emits it because self-description
is useful on one device anyway; Palabra carries it without interpreting it. Neither
needs the other's code.

**(b) The provenance stamp.** Bicho returns, alongside every result:

```jsonc
{ "model": "…", "params": { … }, "seed": …, "cost": { … }, "deterministic": false }
```

Palabra records it in an utterance (`VoidPalabra:/concepts/utterance.md`) if there is
a Palabra present; otherwise it is a log line. This is Core's existing
`materialize(stamp=)` provenance idiom, which both siblings are copying rather than
inventing.

> **The test for any future coupling:** if a proposed shared thing is a *data shape*,
> it is fine. If it is a *function call*, one library is about to depend on the other
> and the proposal should be rejected.

---

## 4. The two refusals, argued

### 4.1 Bicho does not schedule

Latin-OS's founding rejection is *no single central scheduler*, and the argument is
mathematical rather than aesthetic: Core's composability comes from **locality**, and
a central scheduler re-introduces a global total order, making "what happens next" a
property of a queue instead of a property of the graph.

`LatinOS:/design/direction.md` §2 then designs the alternative, and it is already
good: an agent is a rune participating in a **task** mantle and a **compute** mantle
at once; scheduling is **reduction over the task×compute net**; `opaque` marking is
*paused*; the `max_steps` termination guard is a **budget**; `layout.edges` weights
carry cost.

Bicho's job in that picture is small and specific: **be the thing on the other end of
the compute edge, and put an honest number on the wire.** If Bicho maintained a queue
of pending work and decided the order, it would be the central scheduler under a new
name — and it would be one *per device*, which is exactly the "1 device, 1 client"
assumption the whole design rejects.

**The practical line:** Bicho may refuse (out of memory, over budget, model absent)
and may run one thing at a time if a backend requires it. It may not *prioritize*.

### 4.2 Bicho does not interpret

Bicho returns bytes, tokens, embeddings and numbers. It does not parse the model's
answer into application meaning, does not retry on a "bad" answer, and does not
decide that a refusal was a refusal.

This is Core's honesty principle (*never a silent wrong answer*) applied where it is
easiest to violate: a library that quietly re-prompts until the output parses is
manufacturing a result and reporting it as the model's. If an application wants
retries, it writes a loop, and the loop's every attempt is visible and attributable.

---

## 5. Where this leaves the DINO/JEPA question

`VoidPalabra:/design/world-models.md` answered *whether* learned world models belong
in Palabra (mostly no; four narrow places yes). It did not answer *where they would
run*, and the answer is here: **a world model is another [model](/concepts/model.md)
in Bicho** — a rune with `kind: "world"` or `kind: "embed"`, loaded by a
[runtime](/concepts/runtime.md), invoked with a budget, stamped with provenance.

That is the whole integration. It is deliberately boring, and being boring is the
point: if adding a fundamentally different model architecture requires a new
subsystem, the vocabulary was wrong.

---

## 6. What Bicho is not

- **Not a training system.** Fine-tuning, LoRA production, and dataset curation are
  out of scope at founding. Bicho *loads* an adapter; it does not make one.
  (`VoidCore:/design/needle-finetune.md` is the one live training track and it is
  Core's.)
- **Not an agent framework.** No planner, no tool-calling loop, no memory manager.
  Core already rules that durable agent memory is *a rune in a `memory` mantle* and
  that agent tools are ~40 app-defined Voidscript snippets over dispatcher verbs
  (`VoidCore:/design/agent-tools-memory.md`). Bicho adds nothing there.
- **Not a router with opinions.** It will not silently substitute a cheaper model.
  Selection is the caller's tag query ([model](/concepts/model.md)); a fallback chain
  is a thing the caller declares, not a thing Bicho infers.
- **Not a server.** Same stance as Palabra's. If a model runs on another device, that
  device is a **peer** and Palabra addresses it.
