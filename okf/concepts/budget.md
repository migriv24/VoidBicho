---
type: Concept
title: Budget
description: Cost as a first-class value and refusal as a value rather than an exception — the mirror of Palabra's conflict object, and the reason Bicho reports rather than decides.
tags: [status:planned, audience:dev, audience:library, confidence:asserted]
timestamp: 2026-07-27T00:00:00Z
---

Every [invocation](/concepts/invocation.md) costs something real: tokens, seconds,
watts, or money. **Bicho's job is to make that number visible and enforceable at the
call site.** It is not to decide whether the number is acceptable.

# Refusal is a value, not an exception

The mirror of `VoidPalabra:/concepts/conflict.md`, arrived at from a different
direction and for the same reason.

When a bound is exceeded, or would be, Bicho returns a **refusal** — an ordinary
result object with `ok: false` and a reason:

```jsonc
{ "ok": false,
  "refused": "budget",         // | "residency" | "absent" | "capability"
  "detail":  { "bound": { "spend": 0.05 }, "estimate": { "spend": 0.31 } },
  "cost":    { "wall_ms": 3 } } // refusing is cheap, but it is not free
```

Three consequences, all deliberate:

- **A refusal is inspectable.** `estimate` vs `bound` tells the caller *how much* too
  expensive, which is the difference between "try a smaller bicho" and "give up."
- **A refusal is not a crash.** An application that hits its budget is in a normal
  state, not a broken one — the same stance as *a mantle containing a conflict is
  still readable, still syncable, still valid.*
- **A refusal is recordable.** It has a shape, so it can be stamped and written into
  state exactly like a success. *"We did not do this, and here is why"* is history
  worth having, and an exception thrown into a stack trace is not.

# Estimate before, measure after — and never confuse them

Two numbers, and the discipline is that they are never the same field:

| | when | accuracy |
|---|---|---|
| **estimate** | before the call, from token count and the model's rune | approximate, and must be labelled so |
| **cost** | after the call, from what the runtime reports | actual |

An estimate presented as a cost is a silent wrong answer. Where a backend cannot
report actual cost, `cost` carries what is known and says the rest is unknown —
rather than quietly echoing the estimate back.

# Bicho reports; the caller decides

This is [boundaries](/design/boundaries.md) §4.1 in its most concrete form, and the
distinction is narrow enough to be worth stating twice:

- **Bicho may refuse** — this call, against the bound this caller passed. That is
  local, immediate, and requires no knowledge of anything else in the system.
- **Bicho may not prioritize** — it holds no queue, ranks no pending work, and has no
  opinion about which of two callers matters more. That is scheduling, it needs a
  global view, and a per-device component that has one *is* the central scheduler
  that `LatinOS:/design/direction.md` exists to reject.

The distinction is *local enforcement vs global allocation*. Bicho does the first;
the second belongs to whoever holds the whole graph.

# Cost belongs on the wire

Latin-OS's design already puts this in the right place: the compute mantle's runes
are models and accelerators, and **`layout.edges` carry weights — so cost lives on
the edge, where both sides can see it**. Bicho's contribution is supplying an honest
weight rather than inventing a parallel accounting system.

The consequence, which is the interesting part: once cost is graph structure, *"can
this agent afford to run?"* is answerable **locally**, by looking at one edge — no
central budget authority, no global counter, no shared queue. That is why the
no-scheduler stance survives contact with real resource limits, and it is the piece
that would break first if Bicho started keeping its own books.

# What counts as cost

Deliberately plural, because optimizing one while hiding the others is how a system
becomes unusable on a laptop:

- **tokens** in and out — the unit remote backends bill in
- **wall time** — the unit a user actually feels
- **spend** — real money, and the only one that is irreversible
- **energy / thermal** — the unit a phone and a Void Buzz device care about
- **residency** — VRAM held, which is a cost paid by *everything else* on the device

The last one is the easiest to forget and the most likely to make an application feel
broken for reasons no profile explains.

# Status

`planned`. Nothing built. The refusal shape is the piece worth settling first, since
[invocation](/concepts/invocation.md)'s response type has to accommodate it from the
start rather than acquire it later.
