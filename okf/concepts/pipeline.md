---
type: Concept
title: Pipeline
description: Multi-stage work as a mantle whose runes are stages and whose edges are wires — where the interaction-net shape genuinely fits, and the two places it does not.
tags: [status:planned, audience:dev, confidence:exploratory]
timestamp: 2026-07-27T00:00:00Z
---

Real work is rarely one [invocation](/concepts/invocation.md). It is: embed the
query → retrieve → assemble a prompt → generate → parse → maybe generate again. Every
model library eventually grows a way to express this, and most of them grow a bad one
(a DSL, a YAML graph, a decorator soup).

**Void Core already has the right one.** A **pipeline is a mantle**: stages are runes,
the wiring is `layout.edges`, and the stage kinds are glyphs. That is not an analogy —
it is the same net structure `VoidCore:/concepts/reduce.md` executes, pointed at a new
domain.

```
[query] --0:0--> [embed] --0:0--> [retrieve] --0:1--> [prompt] --0:0--> [generate] --> [parse]
                                                          ^
[cut: v:8c41f2…] ----------------------------------------┘
```

# Why this is more than tidiness

Four things come free, and each is a thing pipeline libraries build by hand:

1. **A pipeline is versioned and syncable.** It is a mantle, so
   `VoidPalabra:` handles it with no work here. *"Which pipeline produced this?"* is
   answerable by hash.
2. **Cost is on the edges.** `layout.edges` carry **weights**, so the cost model in
   [budget](/concepts/budget.md) is structural rather than bolted on — and a
   pipeline's total estimate is a walk over the graph.
3. **Stages are runes, so they are taggable.** `find "stage AND cached"` is the
   existing grammar again ([model](/concepts/model.md) makes the same argument).
4. **Locality.** Two stages that do not share an edge cannot affect each other. That
   is the property that makes parallel execution safe *by structure* rather than by a
   lock.

# Where the interaction-net shape genuinely fits — and where it does not

This is the part to be careful about, because the fit is partial and overclaiming it
would produce confident nonsense.

**It fits** for the *structure*: agents with principal and auxiliary ports, wires,
locality, and the fact that a stage fires when its inputs are present. Void Core's
`to_net`/`from_net` already bridge a mantle to a net, and port indices already ride
the edge `relation` as `"i:j"`. Nothing new is needed to *express* a pipeline this
way.

**It does not fit** in two specific places, and both matter:

- **Reduction is pure; a pipeline is not.** `reduce` is explicitly effect-free —
  *"effects never fire from inside it"* — and an [invocation](/concepts/invocation.md)
  is the definitive effect. So a pipeline **cannot** be executed by Core's `reduce`.
  The honest structure is: `reduce` **plans** (normalizes the graph, resolves
  references, computes what can fire), and Bicho **fires**, one effect at a time,
  outside the reducer. Conflating the two would drag effects into the pure layer and
  break the property that makes `reduce` worth having.
- **Confluence is not available here.** Two orderings of two model calls do **not**
  produce the same result, because the calls are nondeterministic. So the
  strong-confluence guarantee that makes `reduce`'s scheduling immaterial does not
  transfer. Where a pipeline's stages are genuinely independent, order is immaterial
  for the good reason (locality); where they are not, order is real and must be an
  edge.

> Stated as a rule: **borrow the net's structure and its locality; do not borrow its
> confluence.** `VoidPalabra:/references/academic-foundations.md` §4 makes the same
> caution about assuming confluence outside Core's restricted subset, and this is the
> same error one domain over.

# The obvious first pipeline

Retrieval: `embed → search → assemble → generate`. It is the one every application
wants, it exercises three of the five `content.kind`s in
[model](/concepts/model.md), and its `assemble` stage is where
`VoidPalabra:/concepts/compute.md`'s *prompt-is-a-scry* becomes literal — the stage's
content is a `Selector`, and the cut it reads from has a name.

# Status

`planned` and `confidence:exploratory` — the most speculative page in the bundle, and
the furthest out on the [roadmap](/roadmap.md). It is written now only because the
*shape* decision (a pipeline is a mantle, not a new DSL) is cheap to make early and
expensive to retrofit.
