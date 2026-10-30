---
type: Reference
title: The 3D-and-AI landscape, 2026-10
description: "Segmentation (SAM 3, SAM 2 tiny, MobileSAM), single-image-to-3D (SAM 3D Objects, TripoSR, Hunyuan3D-2 mini, TRELLIS), shape-as-code (MeshCoder) and 3D scene graphs for language models (ConceptGraphs, SceneGPT): what each does, what it needs, and whether it can run on this machine. Written for the author's request to look into 3D modelling mixed with AI, and for perception.md."
tags: [status:planned, audience:dev, confidence:asserted]
timestamp: 2026-10-09T00:00:00Z
---

> Gathered 2026-10-09 from a fetch of SAM 3D Objects' repository (verified) and web
> searches (third-party, `asserted`). VRAM figures from blogs are indicative only;
> check each project's README before relying on one. **This machine:** NVIDIA RTX
> A1000 laptop GPU with 6 GB, Windows 11, PyTorch 2.11 CPU-only build installed, 24 GB
> of free disk.

# Segmentation (2D)

| model | what | size and needs | here? | confidence |
|---|---|---|---|---|
| **SAM 3** (Meta, 2025-11-19; ICLR 2026) | segment anything *with concepts*: text or exemplar prompts find every instance | one checkpoint, ~848 M parameters; one lab measured ~8 GB VRAM for concept prompts | no, probably (6 GB) | asserted |
| **SAM 2 / 2.1 tiny** | promptable image and video segmentation | ~38.9 M parameters, ~78 MB; called CPU-friendly; ONNX export via `samexporter` | yes, CPU | asserted |
| **MobileSAM** | distilled SAM image encoder, same prompt decoder | ~10 M parameters, ~41 MB; ONNX export; ~3 s per image on a laptop CPU by its README | **yes, CPU: the first adapter** | asserted |

# Single image to 3D

| model | output | needs | here? | confidence |
|---|---|---|---|---|
| **SAM 3D Objects** (Meta, arXiv 2511.16624) | objects with pose, shape, texture, layout; splat or mesh | **Linux, 32 GB VRAM**, gated weights, SAM License | **no**; vendored as code in `third_party/` | verified |
| **TripoSR** | a mesh from one image | ~6 GB VRAM at defaults, by one guide | maybe, at the edge, with a CUDA PyTorch | asserted |
| **Hunyuan3D-2 mini** (Tencent) | shape (and texture, separately) | ~3–6 GB reported; the full model 12–16 GB, full texture pipeline ~29 GB | maybe, shape only | asserted |
| **TRELLIS / TRELLIS.2** (Microsoft) | structured 3D latents → mesh, splat, radiance field | 16 GB originally, ~8 GB optimised by a third party; TRELLIS.2 listed at 24 GB | no | asserted |

# Shape as structure

| work | what | why it matters here |
|---|---|---|
| **MeshCoder** (NeurIPS 2025) | point cloud → part-structured, editable Blender Python script | a *reader* whose output is structure; Blender is already the Polyp's host. `VoidSquid:/sources/meshcoder.md` (verified, abstract level) |

# 3D scenes for language models

| work | what | why it matters here |
|---|---|---|
| **ConceptGraphs** (ICRA 2024) | 2D masks fused into a 3D object graph with VLM tags and spatial relations | the object-centric graph is the representation; dense features do not scale |
| **SceneGPT** (2024) | that graph, as text, in a language model's context, training-free | the premise of Void Squid's smart logs. `VoidSquid:/sources/conceptgraphs-scenegpt.md` |

# What this means for Bicho's order

1. **Phase 0, the catalogue, first**, as already planned: each model above is a rune with
   `kind`, `needs` (VRAM, OS, licence) and `here` facets, which is exactly the
   "what could this device run, and what can it run now" question Phase 0 exists for.
2. **The first invocation is MobileSAM on CPU over ONNX Runtime** (`segment-2d`), the
   cheapest model that exercises the whole perception path. ONNX Runtime is already the
   prior-art choice for small non-LLM models (`/references/prior-art.md`).
3. **The big 3D models are peer or remote**, by measurement: this laptop cannot hold
   them. A remote GPU host is a `peer` with a capability declaration.

Disk note: each of these models' weights is tens of MB (MobileSAM) to several GB (the
3D generators). None has been downloaded.
