"""clip_adapter.py - kind label: CLIP zero-shot labels for images or masked crops.

input:  {"labels": ["a road", ...], "template": "a screenshot of {} in a video game",
         "images": [path, ...]}                                  whole images, or
        {"image": path, "masks": path.npz, "indices": [..]}       one crop per mask: the mask's box,
                                                                  everything outside the mask greyed
output: {"probs": [[p per label] per input], "top": [[label, p], ...]}
The vocabulary is the caller's: CLIP can only choose among the words it is given.
"""
import numpy as np


class Clip:
    deterministic = False

    def __init__(self, model, device):
        import open_clip, torch
        arch, tag = model["facets"]["where"]["weights"].split(":", 1)[1].split("/")
        self.torch = torch
        self.device = device
        self.net, _, self.pre = open_clip.create_model_and_transforms(arch, pretrained=tag, device=device)
        self.net.eval()
        self.tok = open_clip.get_tokenizer(arch)
        self._text = {}

    def text(self, labels, template):
        key = (tuple(labels), template)
        if key not in self._text:
            with self.torch.inference_mode():
                t = self.net.encode_text(self.tok([template.format(l) for l in labels]).to(self.device))
                self._text[key] = t / t.norm(dim=-1, keepdim=True)
        return self._text[key]

    def crops(self, inp):
        from PIL import Image
        if "images" in inp:
            return [Image.open(p).convert("RGB") for p in inp["images"]]
        from .sam2_adapter import load_masks
        img = np.array(Image.open(inp["image"]).convert("RGB"))
        masks = load_masks(inp["masks"])
        out = []
        style = inp.get("crop", "isolate")
        for i in inp.get("indices", range(len(masks))):
            if style == "context":
                out.append(self.context_crop(img, masks[i]))
                continue
            m = masks[i]
            ys, xs = np.nonzero(m)
            if len(xs) == 0:
                out.append(Image.fromarray(np.full((8, 8, 3), 128, np.uint8)))
                continue
            pad = 4
            y0, y1 = max(0, ys.min() - pad), min(img.shape[0], ys.max() + pad + 1)
            x0, x1 = max(0, xs.min() - pad), min(img.shape[1], xs.max() + pad + 1)
            c = img[y0:y1, x0:x1].copy()
            c[~m[y0:y1, x0:x1]] = 128
            out.append(Image.fromarray(c))
        return out

    @staticmethod
    def context_crop(img, m):
        """The part in its surroundings: a box twice the mask's size, everything outside the mask
        dimmed, and a red outline around the mask (CLIP attends to drawn red marks: Shtedritski
        et al., 'What does CLIP know about a red circle?', ICCV 2023)."""
        from PIL import Image, ImageFilter
        ys, xs = np.nonzero(m)
        if len(xs) == 0:
            return Image.fromarray(np.full((8, 8, 3), 128, np.uint8))
        H, W = m.shape
        cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
        half = max(ys.max() - ys.min(), xs.max() - xs.min(), 24)
        y0, y1 = int(max(0, cy - half)), int(min(H, cy + half + 1))
        x0, x1 = int(max(0, cx - half)), int(min(W, cx + half + 1))
        c = img[y0:y1, x0:x1].astype(np.float32)
        mm = m[y0:y1, x0:x1]
        c[~mm] *= 0.45
        edge = np.array(Image.fromarray((mm * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES)) > 0
        edge = np.array(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
        c[edge] = (255, 0, 0)
        return Image.fromarray(c.clip(0, 255).astype(np.uint8))

    def run(self, inp, params):
        labels = inp["labels"]
        template = inp.get("template", "a screenshot of {} in a video game")
        ims = self.crops(inp)
        probs = []
        with self.torch.inference_mode():
            t = self.text(labels, template)
            for k in range(0, len(ims), 64):
                x = self.torch.stack([self.pre(im) for im in ims[k:k + 64]]).to(self.device)
                f = self.net.encode_image(x)
                f = f / f.norm(dim=-1, keepdim=True)
                p = (100.0 * f @ t.T).softmax(dim=-1).float().cpu().numpy()
                probs.extend(p.tolist())
        top = [[labels[int(np.argmax(p))], float(max(p))] for p in probs]
        return {"probs": probs, "top": top, "labels": labels}, {"template": template, "count": len(ims), "crop": inp.get("crop", "isolate")}
