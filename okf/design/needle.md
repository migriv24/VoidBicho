---
type: Design
title: Needle — the resident micro-model, moved from Void Core to Bicho
description: "The author, 2026-10-10: Needle (cactus-compute/needle) 'which the void core was already thinking about implementing, but should probably be done at void bicho instead.' Why Bicho is the right owner; what Needle is now (Needle 3: 121M parameters with an engram, tool calling, structured extraction, embeddings, speech; Apache-2.0; telemetry on by default) against what Void Core's plan assumed (26M, MIT, July 2026); what carries over from Core's fine-tune plan unchanged; and the three jobs it would do for Void Squid."
tags: [status:planned, audience:dev, confidence:asserted]
timestamp: 2026-10-10T00:00:00Z
---

> **Nothing is built and no weights are downloaded.** This page takes over
> `VoidCore:/design/needle-finetune.md` (2026-07-13) as the plan of record, keeps
> everything in it that still holds, and corrects what the upstream project has
> changed since.

# 1. Why Bicho, not Void Core

Void Core's own railguard asks *"are we making the core compute the application's
results?"*, and a resident model is the clearest case of computing. Core's plan put
Needle in the reserved `agent …` namespace as *"a default core component."* Bicho's
founding is the reason that is the wrong home: **acquiring, running and accounting for
a model is Bicho's whole job** ([boundaries](/design/boundaries.md)), and Bicho is
reached from Core through the existing `effect` seam with no change to Core at all.
What Core keeps is what Core owns: the verb catalogue that becomes Needle's tool set,
and the conformance suite that checks Needle's output by running it.

Sent to Void Core as
`../VoidCore/MESSAGE_FOR_VOIDCORE_voidsquid-needle-moves-to-bicho-2026-10-10.md`. The
decision on Core's side is Core's.

# 2. What Needle is now

Verified 2026-10-10 against `github.com/cactus-compute/needle` (README level):

| | Void Core's plan assumed (local clone `../needle`, 2026-07-01) | upstream today (Needle 3) |
|---|---|---|
| size | 26M parameters, encoder-decoder, attention-only | **121M**, most in an n-gram "engram" memory, *"the arithmetic of a 50M one"*; a single **8–29 MB** binary; depths 2 to 20 each deployable |
| jobs | single-shot function calling | **tool calling**, **structured extraction** against a schema, **text embeddings**, and **speech** (Whistle, 16.9 MB) |
| output | JSON calls, constrained decoding available | a byte-level grammar compiled from your schemas: *"the decode grammar guarantees the output parses"*; a **calibrated confidence** per answer; *"ask for something no tool covers and you get an empty list, not a guess"* |
| fine-tune | JSONL `{query, tools, answers}`, ≥120 examples per tool | local LoRA (`needle finetune`, CPU, CUDA or Metal through JAX) or a hosted full fine-tune |
| runtime | Python | a **C++ engine** loading `.cact` weights; prebuilt per platform; a Python package `cact-needle`; a CLI with `--serve` |
| licence | MIT | **Apache-2.0** |
| telemetry | — | **on by default in the binary**; off with `NEEDLE_TELEMETRY=0` and `DO_NOT_TRACK=1` |

Three of those rows matter more than the rest:

1. **Telemetry on by default.** A Bicho runtime that loads Needle sets both variables
   before the engine starts, always, and its `describe()` says so. The family's
   local-first stance (Verguenza, Palabra, Latin OS) does not survive a model that
   phones home silently.
2. **An empty list instead of a guess, and a confidence.** That is Bicho's own
   invocation contract (*never a silent wrong answer*) arriving from the vendor's side;
   `stopped: refused` and a confidence field map onto it directly.
3. **Embeddings in the same model.** The asset library Void Squid accepted on
   2026-10-10 (its S18) wants text → nearest presets; Needle can be that `embed` model
   without a second download.

# 3. What carries over from Core's plan, unchanged

Core's plan was careful and most of it is about **data**, which is model-independent:

- **One tool per verb operation**, snake-cased, with a deterministic desugarer back to a
  command line. Lossless, testable, no model involved.
- **A state digest** with every call, built from read verbs (`where`, `ls`, `axes`,
  `glyphs`): the skill being trained is copying names out of context.
- **The curriculum**: read routing first, tag filter expressions as the largest slice,
  `@expr` bulk targeting, then safe mutation, then `batch` as a static plan, then a
  trained **`defer`** answer for anything outward, irreversible or ambiguous (10–15% of
  the data).
- **Non-goals**: no Voidscript authoring, no rule authoring, no conversation.

What changes is only the budget arithmetic (Needle 3's context limits have to be
re-read from the new release before the tiering in Core's §3 is redone) and that the
model now also emits a confidence, which belongs in the provenance stamp.

# 4. Three jobs for Void Squid

1. **A command bar that routes to verbs.** Void Squid's tool set already exists as data:
   its `HostApp` declares effect ops with documentation (`open`, `make`, `sim`,
   `survey`, `near`, `look` …) and Void Maiz turns that into a briefing (`squid
   --describe`). That briefing *is* a tool list. "Run three traffic simulations and
   tell me which car arrives first" → `effect make traffic t.ink; effect open t.ink;
   effect sim new 3; effect sim step 200` as one `batch`, with outward effects gated
   exactly as for a person.
2. **The asset library's search** (`embed`): "a small red car" → the nearest presets
   in a catalogue mantle.
3. **Structured extraction for decompilation**: a recovered game's text (item tables,
   dialogue) into typed fields that become turkeys, with confidence carried into the
   ingress residual.

Each is an ordinary invocation: a model rune selected by tag, a runtime, a budget, a
stamp. None needs anything Bicho does not already define.

# 5. Order

Bicho's Phase 0 (the catalogue) first, then Phase 1's first two runtimes: **ONNX
Runtime** for small perception models (MobileSAM; [perception](/concepts/perception.md))
and **Needle's C++ engine** for routing, extraction and embeddings. Both run on this
laptop's CPU. Fine-tuning comes after one honest invocation works, and the
synthetic-data generator is the first thing to build for it, because it needs no model
at all: it walks a host's briefing and a Core instance and emits verified
`{query, tools, answers}` rows.
