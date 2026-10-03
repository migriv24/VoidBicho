---
type: Concept
title: Invocation
description: One bounded call across the effect boundary — what goes in, what must come back, and why honesty about nondeterminism is the whole contract.
tags: [status:planned, audience:dev, audience:library, confidence:asserted, foundation]
timestamp: 2026-07-27T00:00:00Z
---

An **invocation** is one bounded call to a [model](/concepts/model.md) through a
[runtime](/concepts/runtime.md). It is the moment Bicho crosses the **effect
boundary**, and it is the only place in Void Core's world where a caller may not
assume that the same inputs give the same output.

```jsonc
// in
{ "model":  "<tag query or spirit.id>",
  "input":  { … },              // tokens, text, image bytes, a batch
  "params": { "temperature": …, "seed": …, "max_tokens": … },
  "bound":  { "tokens": …, "wall_ms": …, "spend": … } }   // see /concepts/budget.md

// out — every field required, none optional
{ "ok":       true,
  "output":   { … },
  "model":    "rn_4f2a…",       // which bicho ACTUALLY ran, resolved from the query
  "params":   { … },            // as actually applied, including defaults filled in
  "cost":     { "tokens_in": …, "tokens_out": …, "wall_ms": …, "spend": … },
  "deterministic": false,       // whether this call can be reproduced
  "stopped":  "complete" | "bound:tokens" | "bound:wall" | "bound:spend" | "refused" }
```

# The contract is honesty, not capability

Void Core's principle is *never a silent wrong answer*. An inference call is the
easiest place in the entire system to violate it, in four specific ways — so all
four are closed by the shape above:

1. **Which model actually ran.** If selection was a tag query, the caller asked for
   *a* model and got *one*. Returning `model` as a resolved `spirit.id` makes a
   fallback visible. **Bicho never silently substitutes** — see
   [boundaries](/design/boundaries.md) §6.
2. **What the params actually were.** Defaults filled in by a backend are part of the
   answer. A result reproduced with different unstated defaults is a different result.
3. **Whether it finished.** `stopped` distinguishes *the model was done* from *we cut
   it off*, and truncation reported as completion is a wrong answer with a confident
   face.
4. **Whether it is reproducible.** `deterministic` is a **claim Bicho must be able to
   defend**: `true` only when the backend actually pins it (greedy decode, fixed
   seed, deterministic kernels). Most of the time it is `false`, and saying so is the
   feature.

# Why it can never be an utterance

`VoidPalabra:/concepts/utterance.md` allows only **pure** changes into history,
because an effect is not replayable, not invertible, and not addressable by its
result. An invocation is the textbook effect. So the boundary falls exactly here, and
Palabra has already drawn it from the other side:

| step | kind | recorded |
|---|---|---|
| build the prompt | pure — a `scry` over a named cut | nothing; derivable |
| **the invocation** | **effect** | **never** |
| write the result into state | pure | an utterance, with provenance |

Bicho's contribution to that third row is the **provenance stamp** — `model`,
`params`, `seed`, `cost`, `deterministic` — which Palabra copies into the utterance if
a Palabra is present, and which is a log line if not. Neither library calls the
other; they agree on a shape ([boundaries](/design/boundaries.md) §3).

The property this buys, jointly, is worth naming because nobody else has it: with
Palabra's addressable prompt (`prompt_cut: v:8c41f2…`) plus Bicho's stamp, **an agent
run is a reproducible experiment** — the exact input state can be recovered by hash,
and the exact model and parameters are recorded beside it. When
`deterministic: true`, it can be re-run and checked. When `false`, you at least know
precisely what could not be reproduced.

# Sessions — the stateful case

A conversation is not *n* independent invocations: a KV cache makes the second turn
far cheaper than re-sending the first. So a **session** is an optional handle
threading invocations together.

The discipline: a session is a **runtime optimization and nothing else**. It may be
dropped at any time and the caller must still get a correct answer — more slowly.
The moment correctness depends on a session surviving, Bicho has grown hidden state
that no one can version, sync, or audit.

# Streaming, and the one thing it must not break

Tokens arriving incrementally is a UI requirement, not a semantic one. Whatever
shape streaming takes, **the final object above must still be produced**, complete —
a stream that ends without `cost` and `stopped` is an invocation that lied by
omission.

# Status

`planned`. Nothing built. The response shape is the part worth getting right first;
it is the thing every other page here assumes.
