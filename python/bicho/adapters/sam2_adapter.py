"""sam2_adapter.py - kind segment-2d: Segment Anything 2.1 on one image.

input:  {"image": path, "out": path.npz,                       automatic: a point grid
         "points": [[x, y], ...], "labels": [1, 0, ...],        or prompted (1 = in, 0 = out)
         "boxes": [[x0, y0, x1, y1], ...]}
output: {"masks": path.npz (bool, N x H x W), "count": N,
         "meta": [{"area", "bbox": [x, y, w, h], "predicted_iou", "stability_score"}]}
Masks are class-agnostic: SAM says *where* things are, never *what* they are.
"""
import os
import numpy as np


class Sam2:
    deterministic = False   # CUDA kernels are not pinned; the same image can give slightly different masks

    def __init__(self, model, store, device):
        import torch
        from sam2.build_sam import build_sam2
        w = model["facets"]["where"]
        self.device = device
        self.torch = torch
        self.net = build_sam2(w["config"], os.path.join(store, w["weights"]), device=device)
        self._auto = None
        self._pred = None

    def run(self, inp, params):
        from PIL import Image
        img = np.array(Image.open(inp["image"]).convert("RGB"))
        out = inp.get("out") or os.path.splitext(inp["image"])[0] + ".masks.npz"
        applied = {}
        with self.torch.inference_mode(), self.torch.autocast(self.device, dtype=self.torch.bfloat16, enabled=self.device == "cuda"):
            if "points" in inp or "boxes" in inp:
                from sam2.sam2_image_predictor import SAM2ImagePredictor
                self._pred = self._pred or SAM2ImagePredictor(self.net)
                self._pred.set_image(img)
                masks, scores, _ = self._pred.predict(
                    point_coords=np.array(inp["points"], np.float32) if "points" in inp else None,
                    point_labels=np.array(inp.get("labels", [1] * len(inp.get("points", []))), np.int32) if "points" in inp else None,
                    box=np.array(inp["boxes"], np.float32) if "boxes" in inp else None,
                    multimask_output=params.get("multimask", True))
                masks = masks.reshape(-1, *masks.shape[-2:]) > 0.5
                scores = np.asarray(scores).reshape(-1)
                meta = [{"area": int(m.sum()), "predicted_iou": float(s)} for m, s in zip(masks, scores)]
                applied = {"mode": "prompted", "multimask": params.get("multimask", True)}
            else:
                from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
                applied = {"mode": "automatic", "points_per_side": params.get("points_per_side", 32),
                           "pred_iou_thresh": params.get("pred_iou_thresh", 0.7),
                           "stability_score_thresh": params.get("stability_score_thresh", 0.85),
                           "min_mask_region_area": params.get("min_mask_region_area", 40)}
                gen = SAM2AutomaticMaskGenerator(self.net, points_per_side=applied["points_per_side"],
                                                 pred_iou_thresh=applied["pred_iou_thresh"],
                                                 stability_score_thresh=applied["stability_score_thresh"],
                                                 min_mask_region_area=applied["min_mask_region_area"])
                res = gen.generate(img)
                res.sort(key=lambda r: -r["area"])
                masks = np.array([r["segmentation"] for r in res], bool) if res else np.zeros((0, *img.shape[:2]), bool)
                meta = [{"area": int(r["area"]), "bbox": [float(v) for v in r["bbox"]],
                         "predicted_iou": float(r["predicted_iou"]), "stability_score": float(r["stability_score"])} for r in res]
        np.savez_compressed(out, masks=np.packbits(masks, axis=-1), shape=np.array(masks.shape))
        return {"masks": out, "count": len(meta), "meta": meta}, applied


def load_masks(path):
    """Unpack what run() saved: -> bool array N x H x W."""
    z = np.load(path)
    n, h, w = z["shape"]
    return np.unpackbits(z["masks"], axis=-1)[..., :w].astype(bool).reshape(n, h, w)
