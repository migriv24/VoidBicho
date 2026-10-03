# Void Bicho

**The compute layer for Void Core: how an application acquires a model, runs it,
and pays for it.** Founded 2026-07-27. A **library**, not an application — nothing
is built yet; the OKF comes before the code, as always.

*Bicho* — bug, critter; also what you call a kid. The models are the bichos: small
things you keep, feed, and put to work. Some are 26 million parameters and nearly
free. Some are enormous and expensive. Void Bicho is the vocabulary that covers
both without pretending they are the same animal.

One sentence: **Void Bicho turns "run a model" into something a Void Core
application can describe, select, budget, and audit — without embedding a model
runtime in the core, and without every app re-inventing the same loader.**

## Why it exists

Void Core does **no I/O by definition** (`VoidCore:SPEC.md §9`) — all real I/O is a
**holiday**, and Core's holiday page already names *LLM backends* as one of the
kinds. So the seam exists and nothing fills it. Every application that wants a model
is currently on its own: its own loader, its own prompt assembly, its own error
handling, its own idea of what a "model" is.

That is the same failure [Void Palabra](../VoidPalabra/) was split out to fix for
storage — and it is fixed the same way, by a library outside Core rather than a
subsystem inside it.

## The division of labour

Bicho and Palabra are siblings that meet at a seam, **not** dependencies.

| question | owner |
|---|---|
| *which peer can run this?* | **Palabra** |
| *how do I get the model onto this device, and into memory?* | **Bicho** |
| *what goes in the prompt?* | **Palabra** — a prompt is a scry over a named cut |
| *run it* | **Bicho** |
| *what did it cost, and can I afford it?* | **Bicho** |
| *what happened, and how do I prove it later?* | **Palabra** — an utterance with provenance |
| *when does this agent get to run at all?* | **Latin-OS** |

**Neither library imports the other.** Bicho works on a single device with no sync;
Palabra syncs fine on a device with no model runtime. They agree on two small data
shapes and nothing else — see [design/boundaries.md](okf/design/boundaries.md), which
is the page to read first if you only read one.

## The one idea worth having early

**A model is a rune.** Not a config entry, not a registry key — a rune in a `models`
mantle, with facets, tags, and a stable `spirit.id`. Which means **model selection
is a tag query**, using Core's existing grammar:

```
find "vision AND local AND NOT metered"
```

No new selection language, no new registry, no new matcher. See
[concepts/model.md](okf/concepts/model.md).

## Status

**Nothing is built.** Every concept in the bundle is `status:planned`, per the
honesty convention inherited from Void Core (no `status:current` without a
`resource:` link to real code). **Void Palabra is being developed first**, by the
author's ruling; this bundle exists so that the boundary is settled *before* either
side grows a shape the other cannot use.

Start reading at **[okf/index.md](okf/index.md)**.

## Siblings

- **[Void Core](../VoidCore/)** — the engine. Owns rune, mantle, holiday, glyph,
  dispatcher. Bicho owns none of them and is a holiday implementation.
- **[Void Palabra](../VoidPalabra/)** — the system layer: remembering, speaking,
  and the *naming* of compute. Bicho is the *doing* of it.
- **[Latin-OS](../LatinOS/)** — where agent scheduling and budget enforcement
  actually live. Bicho supplies the numbers; it does not decide who runs.
