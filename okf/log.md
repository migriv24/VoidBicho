# Bundle Update Log

## 2026-10-11 — The cache moved into the store; SAM 3, CLAP, MiniLM and BLIP behind the contract

Written from the Void Squid session. The author: *"take those next steps to really integrate
these other models, if you found them in my cache, move them over somewhere more useful."*

**Moved.** Eight models found in the author's Hugging Face cache now live in
`%USERPROFILE%/.voidbicho/models/hf/hub`, and `core.py` points `HF_HUB_CACHE` there, so every
adapter finds them without a download. About 8 GB in all; SAM 3 is the largest at 3.3 GB. CLAP was downloaded there new.

**Built** (catalogue: ten models; `python/tests/test_core.py` passes):

* **`segment-text`, SAM 3.** A noun phrase returns masks of every instance. The repackaged
  checkpoint prefixes every key with `detector.`. Loaded as published, the model silently
  kept random weights and found nothing. The adapter now loads the weights itself and
  **refuses if any key is missing**. It runs under bfloat16 autocast on the 6 GB GPU and
  needed `triton-windows`.
* **`label-audio`, CLAP.** Ranks sound files against descriptions. Void Squid used it to pick
  12 effects from 2,543 decoded waves (Super Mario Galaxy and Mario Kart DS).
* **`embed`, all-MiniLM-L6-v2**, and **`caption`, BLIP base.**

**Measured.** SAM 3 on a Super Mario Galaxy render: *"toy"* found the Octoomba at 0.88, and
*"enemy"* and *"octopus"* found nothing. Role is not appearance. The query `"embed"` resolved
to CLIP before MiniLM, because both carry the tag. Callers who want the small text model say
`"embed AND small"`. Selection by tags worked as designed, and the surprise was the caller's.

**Found.** The test's "no match" probe was `"speech"` until Kokoro arrived and matched it.
It is now `"teleportation"`. A catalogue that grows can turn a negative test positive, so
negative probes must name something no model will ever claim.

---

## 2026-10-10 (night) — First code: a perception runtime, SAM 2.1 and CLIP behind the contract

Written from the Void Squid session, at the author's direction: *"void jelly is gonna need
computer vision stuff. not within itself, but utilizing a library heavily (library provided
by void bicho)."* And on size: *"1gig or 2 is fine."*

**Built** (`python/bicho/`, a Python package; `python/tests/test_core.py` passes):

* **The catalogue** (`catalogue.json`): three model runes in shape (spirit id, tags, facets
  who/what/where/how/licence, content kind). **Selection is a tag query** in Core's grammar
  (`segment-2d AND large`).
* **The invocation contract** (`core.py`), as [invocation](/concepts/invocation.md) specifies:
  every reply carries ok, output, the model that actually ran, the params as applied, cost,
  deterministic, stopped. **Refusal is a value**: unknown model, missing weights (with the
  command that fixes it), adapter error.
* **Acquire** (`python -m bicho fetch`): weights into `%USERPROFILE%/.voidbicho/models`, never
  into a repository. SAM 2.1 Large: 898,083,611 bytes, as catalogued.
* **Adapters:** `segment-2d` (SAM 2.1 Hiera-L: automatic or prompted masks; masks go to a
  file, the reply stays small) and `label` (OpenCLIP ViT-B/16 LAION-2B: zero-shot labels for
  images or for masked crops, with an optional red-outline context crop).
* **`serve`**: one JSON request per line on stdin, one reply per line on stdout. Models stay
  loaded for a session; a host drives it as a process holiday.

**Measured:** SAM 2.1 Large took 172 s on the CPU and about 6 s on the 6 GB RTX A1000 per
512² view. The same image gave **68 masks on the CPU and 72 on the GPU**, so `deterministic:
false` is a fact, not modesty. The perception work these runtimes served, and its results,
are in `VoidSquid:/design/seeing-what-was-decompiled.md`.

**Deviations from the roadmap, said plainly.** Phase 1 named ONNX Runtime and Needle's C++
engine as the first runtimes. The first built is **PyTorch in a Python process**, because SAM
2 and OpenCLIP ship that way and the author wanted vision now. The contract is the same; the
runtime is a second one, not a replacement. `.venv/` holds CUDA PyTorch 2.11 (cu128) and
is git-ignored. Installing `sam2` from source silently replaced the CUDA build with a CPU
one; the fix (reinstall with `--no-deps`) is recorded for the next environment.


## 2026-10-10 — Needle moves here; the first two runtimes named; a void.json

Written from the Void Squid session; the author: Needle *"which the void core was already
thinking about implementing, but should probably be done at void bicho instead,"* and
*"we're gonna be working with bicho a lot."* **Still nothing built.**

* **[Needle](/design/needle.md)** takes over `VoidCore:/design/needle-finetune.md` as the
  plan of record. Upstream has moved since Core's plan: Needle 3 is 121M parameters (an
  engram memory), adds structured extraction, embeddings and speech, guarantees parseable
  output and an empty list instead of a guess, ships a C++ engine, is **Apache-2.0** (the
  local clone at `../needle` is the July MIT release), and has **telemetry on by default**,
  which any Bicho runtime must switch off. Core's curriculum, desugarer, state digest and
  `defer` class carry over unchanged. A message went to Void Core.
* **Roadmap, Phase 1**: the first two runtimes are ONNX Runtime (MobileSAM for perception)
  and Needle's engine, both CPU on this laptop, before llama.cpp.
* **`void.json`** written at the root, answering Void Mago's 2026-10-04 letter: `runtime`
  (a library), `0.0.1`, `concept`, no `requires` yet because nothing links anything.

## 2026-10-09 — Perception, the 3D landscape, and SAM 3D Objects as code

Written from the Void Squid session, at the author's request: *"VoidBicho might be the
best project to actually implement things like ai models interacting directly with void
based software … segmentation models, or models that can enrich the logs for the CLI …
they should be optional though."* **Nothing was built; Phase 0 is still first.**

* **`third_party/sam-3d-objects/`**: Meta's SAM 3D Objects, commit `f91db41`, code only
  (6.8 MB; git history, stock sample photos and a GIF removed for disk). SAM License.
  Needs Linux and a 32 GB GPU, so it cannot run on this machine (RTX A1000, 6 GB,
  Windows, CPU-only PyTorch). Kept as the reference `lift-3d` implementation. See
  `third_party/README.md`.
* **[Perception](/concepts/perception.md)**: the kinds (`segment-2d`, `segment-3d`,
  `lift-3d`, `caption`, `embed`), the contract applied (the host supplies a render whose
  pixels already know their runes; Bicho returns bytes; the host attaches annotations with
  provenance; never truth; optional by construction). No new machinery, which is the test
  boundaries §5 sets.
* **[The 3D-and-AI landscape](/references/3d-ai-landscape.md)**: what runs here and what
  must be a peer. The first adapter worth building is MobileSAM on CPU through ONNX
  Runtime: about 40 MB, no GPU, and it exercises the whole perception path.
* **Still owed** from Void Mago's 2026-10-04 letter: a `void.json`. Not written this
  session, because Bicho's own owner should decide its kind and edges; noted so it is not
  forgotten.

## 2026-07-27 — founding

* **Void Bicho founded**, by the author's ruling, out of Void Palabra's compute scope
  decision (`VoidPalabra:/concepts/compute.md`): *Palabra owns the naming, routing and
  history of compute; it does not own the computing.* Bicho is the other half of that
  sentence — loading AI models and using them within Void Core applications. A
  **library**, not an application. *Bicho*: bug, critter, and what you call a kid —
  the models are small things you keep and feed, and some of them are 26 million
  parameters.

* **Why it is not a Void Core subsystem.** The same argument that split Palabra out:
  Core does no I/O by definition (`VoidCore:SPEC.md §9`), and Core's own holiday page
  already names **LLM backends** as a holiday kind. So the seam exists and nothing
  fills it, and Bicho fills it from outside. **Bicho needs no change to Void Core** —
  the effect seam, the generic `effect <op>` verb, and `tag_match` over the FFI are
  all already there.

* **Neither sibling imports the other — ruled.** `VoidBicho` does not depend on
  `VoidPalabra` and vice versa; both depend on Core. The failure modes avoided are
  symmetric and concrete: if Bicho imported Palabra, a single laptop with no peers
  would need a version-control library to summarize a document; if Palabra imported
  Bicho, **every peer in the mesh would need a model runtime to reconcile state**,
  which would undo the `State` tier in one line. They meet at **two data shapes** —
  the capability fragment and the provenance stamp — and the standing test is: *a
  shared data shape is fine; a shared function call means one library is about to
  depend on the other.* Recorded in [boundaries](/design/boundaries.md) §3.

* **The load-bearing idea — a model is a rune.** Not a registry entry, not a config
  string: a rune in a `models` mantle, with facets, tags and a `spirit.id`. Which
  makes **model selection a tag query** (`find "vision AND local AND NOT metered"`)
  in Core's existing, conformance-tested grammar. Bicho therefore builds **no**
  registry, ID scheme, capability-metadata format, query language, or matcher — Core
  has all five. And a **model catalogue is an ordinary mantle**, so Palabra versions
  and syncs it with no work here. Everyone else in the field uses a string, and a
  string cannot be tagged, queried, versioned, attributed or synced.

* **Two refusals, both load-bearing** ([boundaries](/design/boundaries.md) §4):
  * **Bicho does not schedule.** It may *refuse* (local, immediate, against the
    bound this caller passed); it may not *prioritize* (global, needs a whole-graph
    view). A per-device component holding a queue **is** the central scheduler that
    `LatinOS:/design/direction.md` exists to reject. Bicho's job in Latin-OS's picture
    is to be the thing on the other end of the compute edge and put an honest number
    on the wire — which is what keeps *"can this agent afford to run?"* answerable
    **locally**, from one edge weight, with no central budget authority.
  * **Bicho does not interpret.** It returns bytes and numbers; it does not parse
    meaning, retry on a "bad" answer, or silently substitute a cheaper model. A
    library that re-prompts until the output parses is manufacturing a result and
    reporting it as the model's — Core's honesty principle in its easiest-to-violate
    location.

* **Refusal is a value, not an exception** ([budget](/concepts/budget.md)) — the
  mirror of `VoidPalabra:/concepts/conflict.md`, reached from a different direction.
  A refusal carries `estimate` vs `bound` (so the caller knows *how much* too
  expensive), is not a crash, and is **recordable** — *"we did not do this, and here
  is why"* is history worth having, and a stack trace is not.

* **The invocation contract is honesty, not capability**
  ([invocation](/concepts/invocation.md)). Four fields exist to close four silent
  wrong answers: `model` (which bicho *actually* ran, after a tag query resolved),
  `params` (as applied, defaults filled in), `stopped` (finished vs cut off), and
  `deterministic` (a claim Bicho must be able to **defend**, `true` only when the
  backend genuinely pins it). And an invocation **can never be an utterance**,
  because it is the textbook effect — Palabra had already drawn that line from the
  other side.

* **The joint property worth naming.** Palabra's addressable prompt (`prompt_cut:
  v:8c41f2…`) plus Bicho's provenance stamp make **an agent run a reproducible
  experiment**: the exact input state recoverable by hash, the exact model and
  parameters recorded beside it. Neither library can do this alone, and the seam
  costs neither a dependency. Recorded in [prior art](/references/prior-art.md) as
  the one thing here that is genuinely unbuilt anywhere.

* **Pipelines are mantles, not a new DSL** ([pipeline](/concepts/pipeline.md),
  `confidence:exploratory`). Stages are runes, wiring is `layout.edges`, cost rides
  edge weights. But the interaction-net fit is **partial and was scoped**: borrow the
  structure and the locality, **do not borrow the confluence** — `reduce` is
  effect-free by contract so it cannot execute a pipeline (it *plans*; Bicho
  *fires*), and two orderings of two nondeterministic model calls do not converge.
  Same caution `VoidPalabra:/references/academic-foundations.md` §4 makes one domain
  over.

* **World models placed, boringly.** `VoidPalabra:/design/world-models.md` answered
  *whether*; this bundle answers *where*: a JEPA-style model is a
  [model](/concepts/model.md) with `kind: "world"` — a rune, a runtime, a budget, a
  stamp. If a new model architecture required a new subsystem, the vocabulary was
  wrong.

* **Bundle created** — `README.md` plus 5 concepts, 2 design notes, 1 reference,
  roadmap and this log. Every concept is `status:planned` (nothing built), per the
  honesty convention inherited from Void Core.

* **Not done (deliberate):** no code; **Void Palabra is built first** by the author's
  ruling, so this roadmap is not scheduled; [prior art](/references/prior-art.md) was
  written from existing knowledge and **not freshly fetched**, and says so; naming is
  the author's call ([open questions](/design/open-questions.md) §1, where *bicho*
  itself is the obvious candidate for "a model").
