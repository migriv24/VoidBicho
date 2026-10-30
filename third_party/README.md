# third_party — model code Void Bicho holds but does not own

Each folder here is someone else's model code, kept as a **reference and an adapter
target**: Bicho's job is to acquire, run and account for models
(`okf/design/boundaries.md`), so the code for a model it may one day run lives beside
it. Nothing here is compiled into anything, linked by anything, or required by any
build. Weights are never committed.

| folder | upstream | commit | licence | runs on this machine? |
|---|---|---|---|---|
| `sam-3d-objects/` | https://github.com/facebookresearch/sam-3d-objects | `f91db411c50efee93d8db7aeb323885650f6f722` (2026-06-02) | SAM License (see its `LICENSE`) | **No.** Needs Linux and an NVIDIA GPU with at least 32 GB of VRAM; this laptop has an RTX A1000 with 6 GB, on Windows, and a CPU-only PyTorch |

## `sam-3d-objects/`

Added 2026-10-09 at the author's request, so that the family has a working reference
for single-image 3D reconstruction (image + mask → objects with pose, shape, texture and
layout; Gaussian splat or mesh). Vendored from a shallow clone, then trimmed to save
disk (the drive was at 98%):

- removed `.git/` (201 MB),
- removed `notebook/images/` (214 MB of sample photographs, licensed stock images),
- removed `doc/*.gif` (7.5 MB).

Kept: all code (`sam3d_objects/`), configs, `environments/`, the notebooks and their small
sample meshes, `doc/setup.md`, `LICENSE`. Total 6.8 MB.

**To run it** you need a Linux machine with a 32 GB GPU, the conda environment in
`environments/default.yml`, and access to the gated weights on Hugging Face
(`facebook/sam-3d-objects`). In Bicho's vocabulary that machine is a **peer** or a
**remote** runtime (`okf/concepts/runtime.md`); this laptop is not.

**Why it is here and not in Void Jelly or Void Squid:** Jelly is pure and holds no model
code; Squid owns effects, not models. A model is a rune in Bicho's catalogue, run by a
runtime, invoked with a budget and stamped with provenance (`okf/concepts/perception.md`).
