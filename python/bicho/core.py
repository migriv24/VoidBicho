"""core.py - the catalogue, tag queries, the invocation contract, and the model store."""
import json, os, re, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.environ.get("VOIDBICHO_MODELS") or os.path.join(os.path.expanduser("~"), ".voidbicho", "models")
# Hugging Face models live inside the store, not in the shared cache (moved there 2026-10-11)
os.environ.setdefault("HF_HUB_CACHE", os.path.join(STORE, "hf", "hub"))


def query(expr, tags):
    """Core's tag grammar, the small part Bicho needs: AND / OR / NOT / parentheses over tags."""
    toks = re.findall(r"\(|\)|[^\s()]+", expr)
    pos = 0

    def atom():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == "(":
            v = disj(); pos += 1
            return v
        if t.upper() == "NOT":
            return not atom()
        return t in tags

    def conj():
        nonlocal pos
        v = atom()
        while pos < len(toks) and toks[pos].upper() == "AND":
            pos += 1; v = atom() and v
        return v

    def disj():
        nonlocal pos
        v = conj()
        while pos < len(toks) and toks[pos].upper() == "OR":
            pos += 1; v = conj() or v
        return v

    return disj() if toks else True


class Bicho:
    def __init__(self, catalogue=None, device=None):
        self.catalogue = json.load(open(catalogue or os.path.join(HERE, "catalogue.json")))["models"]
        self._loaded = {}
        self._device = device

    # ── acquire ──
    def device(self):
        if self._device:
            return self._device
        try:
            import torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            self._device = "none"
        return self._device

    def available(self, m):
        w = m["facets"]["where"].get("weights", "")
        if m["facets"].get("how") == "rule":
            return True, "rule baseline: no weights, nothing to fetch"
        if w.startswith("hf:"):
            repo = w[3:].split("/")
            folder = os.path.join(STORE, "hf", "hub", "models--" + "--".join(repo[:2]))
            if m["facets"].get("how") == "none-yet":
                return False, "catalogued, no adapter yet"
            return True, folder if os.path.exists(folder) else "fetched by its library on first use into " + folder
        if w.startswith("open_clip:"):
            try:
                import open_clip  # noqa: F401
                return True, "open_clip installed; weights fetched on first use into its cache"
            except ImportError:
                return False, "open_clip not installed"
        path = os.path.join(STORE, w)
        return (os.path.exists(path), path if os.path.exists(path) else "weights missing: run `python -m bicho fetch %s`" % m["spirit"]["name"])

    def describe(self):
        out = []
        for m in self.catalogue:
            ok, why = self.available(m)
            out.append({"id": m["spirit"]["id"], "name": m["spirit"]["name"], "kind": m["content"]["kind"],
                        "tags": m["tags"], "can_run_now": ok and self.device() != "none", "why": why,
                        "device": self.device(), "bytes": m["content"].get("bytes")})
        return out

    def resolve(self, expr):
        for m in self.catalogue:
            if m["spirit"]["id"] == expr or m["spirit"]["name"] == expr:
                return m
        hits = [m for m in self.catalogue if query(expr, set(m["tags"]))]
        # prefer what can run now; among those, the first in catalogue order (stated, not hidden)
        hits.sort(key=lambda m: not self.available(m)[0])
        return hits[0] if hits else None

    def fetch(self, name):
        import urllib.request
        m = self.resolve(name)
        if not m:
            return {"ok": False, "why": "no model matches %r" % name}
        w = m["facets"]["where"]
        if "url" not in w:
            return {"ok": True, "why": "fetched by its library on first use"}
        os.makedirs(STORE, exist_ok=True)
        dst = os.path.join(STORE, w["weights"])
        if os.path.exists(dst):
            return {"ok": True, "path": dst, "why": "already present"}
        tmp = dst + ".part"
        urllib.request.urlretrieve(w["url"], tmp)
        os.replace(tmp, dst)
        return {"ok": True, "path": dst, "bytes": os.path.getsize(dst)}

    # ── run ──
    def _adapter(self, m):
        key = m["spirit"]["id"]
        if key not in self._loaded:
            kind = m["content"]["kind"]
            if kind == "segment-2d":
                from .adapters.sam2_adapter import Sam2
                self._loaded[key] = Sam2(m, STORE, self.device())
            elif kind == "label":
                from .adapters.clip_adapter import Clip
                self._loaded[key] = Clip(m, self.device())
            elif kind == "label-audio":
                from .adapters.clap_adapter import Clap
                self._loaded[key] = Clap(m, self.device())
            elif kind in ("embed", "caption", "segment-text"):
                from .adapters import hf_adapters
                self._loaded[key] = hf_adapters.make(kind, m, self.device(), STORE)
            elif kind == "propose":
                from .adapters.propose_adapter import Propose
                self._loaded[key] = Propose(m, self.device())
            else:
                raise ValueError("no adapter for kind %s" % kind)
        return self._loaded[key]

    def invoke(self, req):
        t0 = time.time()
        base = {"ok": False, "output": None, "model": None, "params": req.get("params", {}),
                "cost": {"wall_ms": 0, "spend": 0}, "deterministic": False, "stopped": "refused"}
        m = self.resolve(req.get("model", ""))
        if m is None:
            base["output"] = {"why": "no model in the catalogue matches %r" % req.get("model")}
            return base
        base["model"] = m["spirit"]["id"]
        ok, why = self.available(m)
        if not ok:
            base["output"] = {"why": why}
            return base
        bound = req.get("bound", {})
        try:
            ad = self._adapter(m)
            output, params = ad.run(req.get("input", {}), req.get("params", {}))
            base.update(ok=True, output=output, params=params, stopped="complete",
                        deterministic=bool(getattr(ad, "deterministic", False)))
        except Exception as e:  # a failure is reported, never swallowed
            base["output"] = {"why": "%s: %s" % (type(e).__name__, e), "trace": traceback.format_exc(limit=3)}
            base["stopped"] = "error"
        base["cost"] = {"wall_ms": int((time.time() - t0) * 1000), "spend": 0, "device": self.device()}
        if bound.get("wall_ms") and base["cost"]["wall_ms"] > bound["wall_ms"]:
            base["stopped"] = "bound:wall"   # completed, but over the caller's bound: say so
        return base
