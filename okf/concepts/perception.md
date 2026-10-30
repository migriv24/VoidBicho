---
type: Concept
title: Perception — models that enrich a log, optionally
description: "The author's 2026-10-09 direction: segmentation, 2D and 3D, and other models that 'enrich the logs for the CLI,' optional by design. A perception model is an ordinary Bicho model with a kind (segment-2d, segment-3d, lift-3d, caption, embed); its input is a render or an image a host supplies; its output is an annotation attached to runes the host already knows, with provenance; it never becomes truth. Where each kind is used by Void Squid, and what can run on this machine."
resource: python/bicho/adapters/sam2_adapter.py
tags: [status:current, audience:dev, audience:library, confidence:verified]
timestamp: 2026-10-09T00:00:00Z
---

> The author: *"we will wanna get used to segmentation models, or models that can
> enrich the logs for the CLI a bit more. they should be optional though."* And:
> *"VoidBicho might be the best project to actually implement things like ai models
> interacting directly with void based software."*
>
> **Nothing is built.** This page applies Bicho's existing contract (model, runtime,
> invocation, budget) to one family of models. It adds no new machinery, which is the
> test [boundaries](/design/boundaries.md) §5 sets: *if a fundamentally different model
> architecture requires a new subsystem, the vocabulary was wrong.*

# 1. Why Bicho, and not Jelly or Squid

- **Void Jelly** is pure: no effects, no clocks, no randomness beyond Core's id minting.
  A model invocation is the textbook effect ([invocation](/concepts/invocation.md)).
  Jelly answers *where things are* (its spatial queries); it never answers *what they
  look like*.
- **Void Squid** owns effects (files, windows, toolchains) but not models; its railguard
  would refuse a second inference stack inside an engine.
- **Bicho** exists to acquire, run and account for models. A segmenter is a model.

# 2. The kinds

Each is an ordinary [model](/concepts/model.md) rune with a `kind` tag, selected by tag
query like any other.

| kind | input | output | first use in Void Squid |
|---|---|---|---|
| `segment-2d` | an image, optionally prompts (points, boxes, text) | masks | decompilation: find the objects in a screenshot of a game nobody tagged |
| `segment-3d` | a point cloud or a mesh scene | per-point or per-part labels | splitting a decompiled level's monolithic mesh into turkeys |
| `lift-3d` | an image plus a mask | a 3D object: mesh or splat, pose, layout | asset generation; turning a decompiled sprite into a proposed model (SAM 3D Objects) |
| `caption` | an image region | text | the visual half of a smart log: *"a wooden crate, half in shadow"* |
| `embed` | text or image | a vector | the asset library: *"a red car"* → nearest presets |
| `segment-text` | an image and a noun phrase | masks of every instance, with scores | *"find every tree"* in a render of a decompiled zone (SAM 3, since 2026-10-11) |
| `label-audio` | sound files and descriptions | ranks per description | finding a game's sound effects by meaning when its sound table is not decoded (CLAP, since 2026-10-11) |

# 3. The contract, applied

**In.** The host supplies the image. For a perception call over a Void Squid scene that
image is a **render the host made** (the layer-2 ID buffer and colour buffer in
`VoidSquid:/design/smart-logs.md` §3), so every pixel already knows which rune it
belongs to. That is the bridge that lets a 2D mask be attached to a rune rather than
floating free.

**Out.** Bicho returns bytes and numbers and does not interpret them (boundaries §4.2).
The host turns them into annotations: *mask m covers 80% of rune crate_0's pixels; the
captioner said "wooden crate"*. Every annotation carries Bicho's provenance stamp
(model, params, seed, cost, `deterministic`), recorded the same way as any invocation.

**Never truth.** A model's label is a **proposal**. It enters the log as an annotation
with provenance, and enters the mantle only when a person or a rule accepts it, by an
ordinary dispatcher command. This is Void Squid's railguard (*owns no truth*) and
Bicho's (*does not interpret*) meeting at the same line.

**Optional by construction.** A host with no perception model loaded gets layers 0 to 2
of the smart log (structure, geometry, render) and a log line saying layer 3 was not
used. Nothing depends on a model being present. A refusal (no accelerator, model absent,
over budget) is a value, per [budget](/concepts/budget.md), never a silent omission.

# 4. What can run where

The full landscape is in [the 3D-and-AI landscape](/references/3d-ai-landscape.md). On
this laptop (RTX A1000, 6 GB). *Updated 2026-10-11: CUDA PyTorch is installed, and the
models below run on the GPU behind adapters.*

- **Runs today, with adapters:** SAM 2.1 Large and tiny (`segment-2d`), OpenCLIP ViT-B/16
  (`label`), SAM 3 (`segment-text`, under bfloat16 autocast), CLAP HTSAT (`label-audio`),
  all-MiniLM-L6-v2 (`embed`), BLIP base (`caption`).
- **Catalogued, no adapter yet:** DETR ResNet-50 (`detect`), Kokoro-82M (`speech`), GPT-2
  (`llm`). Their weights were found in the author's Hugging Face cache and moved into the
  store.

*As written on 2026-10-09, before the GPU was in use:*


- **Runs:** small 2D segmenters on CPU through ONNX Runtime (MobileSAM, SAM 2 tiny);
  small embedding models; possibly TripoSR or Hunyuan3D-2 mini on the GPU once a CUDA
  PyTorch is installed (third-party figures; to measure, not trust).
- **Does not run:** SAM 3D Objects (32 GB, Linux), the full Hunyuan3D-2, likely TRELLIS.
  These belong to Bicho's `peer` or `remote` backends.

The first adapter worth building is therefore **`segment-2d` with MobileSAM on CPU over
ONNX Runtime**: small (about 40 MB), no GPU, and it exercises the whole path (host render
→ invocation → mask → rune annotation → log line with provenance).

# 5. Status

*2026-10-10 (night): **built** for `segment-2d` (SAM 2.1 Hiera-L) and `label` (OpenCLIP
ViT-B/16), in Python behind the [invocation](/concepts/invocation.md) contract, run on the
GPU. The host render with an ID buffer exists too (Void Squid's toolbox), and the whole
path ran: host render → invocation → masks → labels → per-triangle annotations with
provenance. Measured results: `VoidSquid:/design/seeing-what-was-decompiled.md`. Still
planned: `segment-3d` as a native model (multi-view lifting covers it for now), `lift-3d`,
`caption`, `embed` through the catalogue, and the ONNX Runtime path. The text below is the
original plan.*

# 5a. Status as planned

`planned`. `third_party/sam-3d-objects/` holds a reference implementation of `lift-3d`
(code only, no weights; see its README). No adapter exists, no runtime exists, and
Bicho's Phase 0 (the model catalogue) is still the first rung.
