---
okf_version: "0.1"
---

# Void Bicho — Knowledge Bundle (dev)

An Open Knowledge Format bundle describing **Void Bicho**: the compute layer for
Void Core — how an application **acquires** a model, **runs** it, **pays** for it,
and **tells the truth** about what it did. A library, not an application.

This is the **dev** bundle. **Nothing is built: every concept here is
`status:planned`**, per the honesty convention inherited from the Void Core bundle —
a concept may not claim `status:current` without a `resource:` link to the code that
backs it.

**Origin.** Founded 2026-07-27 by the author's ruling, out of Void Palabra's compute
scope decision (`VoidPalabra:/concepts/compute.md`): *Palabra owns the naming,
routing and history of compute; it does not own the computing.* Bicho is the other
half of that sentence. **Void Palabra is being built first**; this bundle exists now
so the seam is agreed before either side hardens.

## Read this first

Three claims shape everything else, and two of them are boundaries rather than
features.

1. **A model is a rune.** Not a registry entry. Which makes model selection a **tag
   query** in Core's existing grammar, and makes a model catalogue an ordinary
   mantle that Palabra can version and sync like anything else.
2. **Bicho computes; that is allowed, because Bicho is not Core.** Void Core's
   railguard (*"are we making the core compute the application's results?"*) bounds
   **Core**. Bicho is a host-side library and may do the thing Core must not.
3. **Bicho does not schedule.** Deciding *whether an agent runs* is Latin-OS's, and
   re-answering it here would rebuild the central scheduler that Latin-OS's founding
   rejection exists to prevent. Bicho reports cost and capability; something else
   decides.

# Concepts — the vocabulary

* [Model](/concepts/model.md) - a model is a rune; selection is a tag query — the load-bearing idea
* [Runtime](/concepts/runtime.md) - the backend seam: local weights, a remote peer, and a paid API under one vocabulary
* [Invocation](/concepts/invocation.md) - one bounded call across the effect boundary, and the provenance it must return
* [Budget](/concepts/budget.md) - cost as a first-class value, and refusal as a value rather than an exception
* [Pipeline](/concepts/pipeline.md) - multi-stage work as a mantle; where the interaction-net shape does and does not fit

# Design — the rationale

* [Boundaries](/design/boundaries.md) - **read this first**; what Bicho owns, what it refuses, and why neither sibling imports the other
* [Open questions](/design/open-questions.md) - what is genuinely undecided, and what blocks what

# References

* [Prior art](/references/prior-art.md) - what already exists to borrow, and the small part that does not

# Planned work

* [Roadmap](/roadmap.md) - the rungs, cheapest-useful-first
* [Log](/log.md) - what has changed in this bundle

# Naming

Concept names here are **descriptive and provisional**, following Void Palabra's
precedent — a Void-flavored set is deferred to the author. See
[open questions](/design/open-questions.md) §1.

# Sibling bundles

Void Core's ontology (rune, mantle, domain, holiday, glyph, dispatcher, Voidscript,
reduce/temper/scry) is defined authoritatively at
`C:\Users\migri\Documents\Projects\VoidCore\okf`. Void Palabra's at
`C:\Users\migri\Documents\Projects\VoidPalabra\okf`; Latin-OS's at
`C:\Users\migri\Documents\Projects\LatinOS\okf`. Cross-bundle references are written
`VoidCore:/concepts/mantle.md` (plain-text convention — OKF links are
bundle-root-relative, so foreign bundles cannot be linked directly).

**Bicho owns none of Core's vocabulary**, and none of Palabra's. It defines only
what it takes to hold a model, run it, and account for it.
