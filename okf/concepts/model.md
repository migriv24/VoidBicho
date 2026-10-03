---
type: Concept
title: Model
description: A model is a rune in a models mantle — so selection is a tag query in Core's existing grammar, and a catalogue is an ordinary mantle. The load-bearing idea of the bundle.
tags: [status:planned, audience:dev, audience:library, confidence:asserted, foundation]
timestamp: 2026-07-27T00:00:00Z
---

**A model is a rune.** Not a config entry, not a registry key, not a string in a
settings file — a rune in a `models` mantle, in exactly Void Core's sense of both
words (`VoidCore:/concepts/rune.md`, `VoidCore:/concepts/mantle.md`).

```jsonc
{
  "spirit": { "id": "rn_4f2a…", "name": "needle" },
  "glyph":  "model",
  "tags":   ["local", "gguf", "q4", "instruct", "tiny", "free"],
  "facets": {
    "who":   "HigherOrder / fine-tuned in-house",
    "what":  "26M NL → dispatcher command",
    "when":  "acquired 2026-…",
    "where": "~/.void/bichos/needle-26m.q4.gguf",
    "why":   "the default rune-sized agent; cheap enough to always be on",
    "how":   "llama.cpp runtime, ctx 2048"
  },
  "content": { "kind": "llm", "ctx": 2048, "params": 26e6, "quant": "q4_k_m", … }
}
```

This is the whole idea, and everything else in the bundle is downstream of it.

# Why this is worth insisting on

Because it means **Bicho does not build a selection language, a registry, a matcher,
or a query API.** Core already has all four, and they are already conformance-tested
and exposed over the FFI.

| the thing every model library builds | what Core already has |
|---|---|
| a model registry | a **mantle** |
| a model ID scheme | **`spirit.id`** — frozen, unique, minted |
| capability metadata | **facets** (who/what/when/where/why/how) |
| a capability query language | the **tag grammar**, `SPEC.md §5` |
| the matcher | **`tag_match`** over the C ABI — one implementation, 13/13 conformance |
| a catalogue file format | whatever `VoidPalabra:/concepts/persistence.md` decides |
| syncing the catalogue between devices | Palabra, for free, with no work here |

So model selection is:

```
find "vision AND local AND NOT metered"
ls --tag "instruct AND ctx-8k"
```

and that is not an analogy — it is the same evaluator the rest of Void Core uses.
A library that invented its own would be inventing a worse one, and the fact that
Core's tag axes fit this without strain is the strongest evidence the idea is right.

> **The corollary worth stating:** a **model catalogue is an ordinary mantle**, so it
> is versioned, diffable, taggable, attributable, and syncable with **no work in
> Bicho at all**. "This device knows about these models" becomes a piece of state
> like any other. Two devices reconciling their catalogues is a Palabra problem that
> Palabra already solved.

# Not every bicho is an LLM

The vocabulary must cover animals of very different sizes, or it will silently become
an LLM library and then break on the first embedding model. Declared by `content.kind`:

| kind | example | note |
|---|---|---|
| `llm` | a 7B instruct model, or a hosted API | the obvious one, and not the default |
| `tiny` | **Needle** — 26M, NL → dispatcher | the forcing client; cheap enough its compute edge is nearly free |
| `embed` | a sentence embedder | used by Palabra's semantic-search-over-history idea |
| `world` | a JEPA-style latent predictor | see `VoidPalabra:/design/world-models.md` |
| `classify` | a small task classifier | often the honest answer to something an LLM was reached for |
| `asr` / `tts` / `vision` | modality models | Core's glyphs already carry non-JSON content |

**The design pressure this is here to resist:** an application reaches for the
largest model available because selection was a config string and cost was invisible.
Making a model a rune with tags and a [budget](/concepts/budget.md) makes *"a 26M
classifier would have done"* a question the author can actually ask.

# The rune/model correspondence is not free of friction

Two places the analogy strains, recorded so they are not discovered later:

1. **A model has weights, and weights are large.** The rune holds a *manifest*, not
   the tensor bytes. Where the bytes live, how they are fetched, verified, deduped
   and shared across models that differ only by adapter is
   [runtime](/concepts/runtime.md)'s problem — and content-addressed blocks are
   exactly what `VoidPalabra:/concepts/persistence.md` is building for other reasons.
   **Bicho should not build a second blob store.**
2. **A rune is content-addressable; a running model is not.** The rune is the
   description; the loaded instance is [runtime](/concepts/runtime.md) state, and it
   is not versioned, not synced, and not part of anyone's history.

# Status

`planned`. Nothing built. **Unblocked** — this needs nothing from Palabra and nothing
new from Core; a `model` glyph and a `models` mantle are expressible today.
