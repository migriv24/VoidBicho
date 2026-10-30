"""propose_adapter.py - the proposer behind the forge's match loop.

Contract (Bicho kind `propose`):
  input   {"function": str, "oracle": dict (optional)}
  output  {"function": str, "candidates": [str, ...], "oracle": dict,
           "kind": "baseline", "deterministic": true,
           "honest": "deterministic rule baseline; no learned model, no decompilation"}

This is a deterministic rule baseline: it does NOT decompile. It slugs the function
name and returns an ordered candidate list:

  ["<slug>-wip-1", "<slug>-wip-2", "ok"]

The trailing "ok" is a fixed best-guess placeholder — the slot a learned proposer will
one day fill with a real candidate, and the marker the forge's synthetic verifier
accepts today. The loop budgets how many are tried; this adapter only orders them.

No weights, no model runtime, no fetch. `deterministic` is True, so `Bicho.invoke`
reports it honestly.
"""
import re


class Propose:
    deterministic = True

    def __init__(self, model, device):
        # The contract shape keeps the model and device; a rule baseline uses neither.
        self._device = device

    @staticmethod
    def slug(name):
        s = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
        return s or "function"

    def run(self, inp, params):
        fn = str(inp.get("function", "function"))
        s = self.slug(fn)
        candidates = [f"{s}-wip-1", f"{s}-wip-2", "ok"]
        out = {
            "function": fn,
            "candidates": candidates,
            "oracle": inp.get("oracle") or {},
            "kind": "baseline",
            "deterministic": True,
            "honest": "deterministic rule baseline; no learned model, no decompilation",
        }
        return out, {"kind": "baseline"}
