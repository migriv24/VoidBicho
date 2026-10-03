# Bundle Update Log

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
