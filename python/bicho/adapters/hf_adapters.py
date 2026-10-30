"""hf_adapters.py - the models moved from the Hugging Face cache, behind Bicho's kinds.

  embed         all-MiniLM-L6-v2: {"texts": [...]} -> {"vectors": [[...]]}; with "queries", also cosine ranks
  caption       BLIP base: {"images": [paths]} -> {"captions": [...]}
  segment-text  SAM 3: {"image": path, "prompt": "a goomba", "out": masks.npz} -> masks of every instance
"""
import os
import numpy as np


class Embed:
    deterministic = True   # one forward pass, no sampling

    def __init__(self, model, device):
        from sentence_transformers import SentenceTransformer
        self.net = SentenceTransformer(model["facets"]["where"]["weights"].split(":", 1)[1], device=device)

    def run(self, inp, params):
        V = self.net.encode(inp["texts"], normalize_embeddings=True)
        out = {"vectors": V.tolist()} if inp.get("vectors", False) else {"dim": int(V.shape[1])}
        if "queries" in inp:
            Q = self.net.encode(inp["queries"], normalize_embeddings=True)
            S = Q @ V.T
            out["rank"] = {q: [[int(i), round(float(S[k, i]), 4)] for i in np.argsort(-S[k])[:int(inp.get("top", 5))]]
                           for k, q in enumerate(inp["queries"])}
        return out, {"count": len(inp["texts"])}


class Caption:
    deterministic = True   # greedy decoding

    def __init__(self, model, device):
        from transformers import BlipForConditionalGeneration, BlipProcessor
        name = model["facets"]["where"]["weights"].split(":", 1)[1]
        self.device = device
        self.pre = BlipProcessor.from_pretrained(name)
        self.net = BlipForConditionalGeneration.from_pretrained(name).to(device).eval()

    def run(self, inp, params):
        import torch
        from PIL import Image
        caps = []
        with torch.inference_mode():
            for p in inp["images"]:
                x = self.pre(images=Image.open(p).convert("RGB"), text=inp.get("prefix"), return_tensors="pt").to(self.device)
                caps.append(self.pre.decode(self.net.generate(**x, max_new_tokens=30)[0], skip_special_tokens=True))
        return {"captions": caps}, {"max_new_tokens": 30, "decoding": "greedy"}


class Sam3:
    deterministic = False

    def __init__(self, model, device, store):
        from sam3.model_builder import build_sam3_image_model
        from sam3.model.sam3_image_processor import Sam3Processor
        repo, fn = "models--1038lab--sam3", "sam3.pt"
        snap = os.path.join(store, "hf", "hub", repo, "snapshots")
        ckpt = next(os.path.join(snap, d, fn) for d in os.listdir(snap) if os.path.exists(os.path.join(snap, d, fn)))
        # The repackaged checkpoint prefixes every key with "detector."; load it explicitly so a
        # silent mismatch can never leave the model with random weights (found 2026-10-11).
        import torch
        sd = torch.load(ckpt, map_location="cpu", weights_only=False)
        det = {k[len("detector."):]: v for k, v in sd.items() if k.startswith("detector.")}
        self.net = build_sam3_image_model(checkpoint_path=None, load_from_HF=False, device=device)
        r = self.net.load_state_dict(det, strict=False)
        if r.missing_keys:
            raise RuntimeError("SAM 3 weights incomplete: %d missing keys" % len(r.missing_keys))
        self.net.eval()
        self._proc = {}
        self.Proc = Sam3Processor

    @property
    def proc(self):
        return self._proc.setdefault(self.threshold, self.Proc(self.net, confidence_threshold=self.threshold))

    threshold = 0.4

    def run(self, inp, params):
        import torch
        from PIL import Image
        self.threshold = float(params.get("threshold", 0.4))
        img = Image.open(inp["image"]).convert("RGB")
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=torch.cuda.is_available()):
            state = self.proc.set_image(img)
            out = self.proc.set_text_prompt(state=state, prompt=inp["prompt"])
        masks = np.asarray(out["masks"].float().cpu()).reshape(-1, img.height, img.width) > 0.5 if len(out["masks"]) else np.zeros((0, img.height, img.width), bool)
        scores = [float(s) for s in np.asarray(out["scores"].float().cpu()).reshape(-1)]
        path = inp.get("out") or os.path.splitext(inp["image"])[0] + ".sam3.npz"
        np.savez_compressed(path, masks=np.packbits(masks, axis=-1), shape=np.array(masks.shape))
        return {"masks": path, "count": len(scores), "scores": scores, "prompt": inp["prompt"]}, {"prompt": inp["prompt"], "threshold": self.threshold}


def make(kind, model, device, store):
    if kind == "embed":
        return Embed(model, device)
    if kind == "caption":
        return Caption(model, device)
    if kind == "segment-text":
        return Sam3(model, device, store)
    raise ValueError(kind)
