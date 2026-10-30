"""clap_adapter.py - kind label-audio: CLAP, audio and text in one embedding space.

input:  {"audios": [path.wav, ...], "queries": ["a coin chime", ...], "top": 5}
output: {"rank": {query: [[index, cosine], ...]}}   the best audios for each query
        {"audios": [...], "labels": [...]}         or, with "labels", probabilities per audio
What a sound *is* comes back as a ranking against the caller's words; Bicho does not decide.
"""
import numpy as np


def _load_mono_48k(path, max_s=10.0):
    import wave
    w = wave.open(path, "rb")
    sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    raw = w.readframes(min(n, int(sr * max_s)))
    w.close()
    a = np.frombuffer(raw, {1: np.uint8, 2: np.int16}[sw]).astype(np.float32)
    a = (a - 128) / 128 if sw == 1 else a / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    if sr != 48000 and len(a) > 1:
        t = np.linspace(0, len(a) / sr, int(len(a) * 48000 / sr), endpoint=False)
        a = np.interp(t, np.arange(len(a)) / sr, a).astype(np.float32)
    return a if len(a) else np.zeros(4800, np.float32)


class Clap:
    deterministic = False

    def __init__(self, model, device):
        import torch
        from transformers import ClapModel, ClapProcessor
        name = model["facets"]["where"]["weights"].split(":", 1)[1]
        self.torch, self.device = torch, device
        self.net = ClapModel.from_pretrained(name).to(device).eval()
        self.pre = ClapProcessor.from_pretrained(name)
        self._cache = {}

    def audio_embeddings(self, paths):
        missing = [p for p in paths if p not in self._cache]
        with self.torch.inference_mode():
            for k in range(0, len(missing), 32):
                batch = [_load_mono_48k(p) for p in missing[k:k + 32]]
                x = self.pre(audio=batch, sampling_rate=48000, return_tensors="pt", padding=True)
                x = {kk: v.to(self.device) for kk, v in x.items()}
                f = self.net.get_audio_features(**x)
                f = getattr(f, "pooler_output", f)
                f = (f / f.norm(dim=-1, keepdim=True)).float().cpu().numpy()
                for p, e in zip(missing[k:k + 32], f):
                    self._cache[p] = e
        return np.stack([self._cache[p] for p in paths])

    def text_embeddings(self, texts):
        with self.torch.inference_mode():
            x = self.pre(text=texts, return_tensors="pt", padding=True)
            x = {k: v.to(self.device) for k, v in x.items()}
            f = self.net.get_text_features(**x)
            f = getattr(f, "pooler_output", f)
            return (f / f.norm(dim=-1, keepdim=True)).float().cpu().numpy()

    def run(self, inp, params):
        A = self.audio_embeddings(inp["audios"])
        if "queries" in inp:
            T = self.text_embeddings(inp["queries"])
            S = T @ A.T
            top = int(inp.get("top", 5))
            rank = {q: [[int(i), round(float(S[k, i]), 4)] for i in np.argsort(-S[k])[:top]] for k, q in enumerate(inp["queries"])}
            return {"rank": rank}, {"top": top, "audios": len(A)}
        T = self.text_embeddings(inp["labels"])
        P = np.exp(100 * (A @ T.T)); P /= P.sum(1, keepdims=True)
        return {"probs": P.tolist(), "labels": inp["labels"]}, {"audios": len(A)}
