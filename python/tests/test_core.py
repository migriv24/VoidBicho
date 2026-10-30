"""test_core.py - the contract, with no model loaded: tag queries, resolution, refusal as a value.

    python python/tests/test_core.py          (exit 0 = pass)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from bicho import Bicho, query  # noqa: E402

failures = 0


def check(c, what):
    global failures
    if not c:
        failures += 1
        print("  FAIL", what)


# 1. Core's tag grammar, the part Bicho uses
tags = {"segment-2d", "local", "large"}
check(query("segment-2d AND local", tags), "AND")
check(not query("segment-2d AND NOT local", tags), "AND NOT")
check(query("label OR large", tags), "OR")
check(query("(label OR segment-2d) AND NOT tiny", tags), "parentheses")
check(query("", tags), "empty query matches everything")

# 2. Resolution: by id, by name, by tag query; nothing silently substituted
b = Bicho(device="cpu")
check(b.resolve("rn_sam21_hiera_large")["spirit"]["name"] == "sam2.1-hiera-large", "resolve by id")
check(b.resolve("sam2.1-hiera-tiny")["spirit"]["id"] == "rn_sam21_hiera_tiny", "resolve by name")
check(b.resolve("segment-2d AND tiny")["spirit"]["id"] == "rn_sam21_hiera_tiny", "resolve by tags")
check(b.resolve("teleportation") is None, "no match is None, not a fallback")

# 3. Refusal is a value with every field present
r = b.invoke({"model": "teleportation", "input": {}})
for k in ("ok", "output", "model", "params", "cost", "deterministic", "stopped"):
    check(k in r, "field %s present on refusal" % k)
check(r["ok"] is False and r["stopped"] == "refused", "unknown model is refused")
os.environ["VOIDBICHO_MODELS"] = "/nonexistent"
import importlib, bicho.core as core  # noqa: E402
importlib.reload(core)
r2 = core.Bicho(device="cpu").invoke({"model": "segment-2d AND tiny", "input": {"image": "x.png"}})
check(r2["stopped"] == "refused" and "weights missing" in r2["output"]["why"], "missing weights refused, with the fix named")
check(r2["model"] == "rn_sam21_hiera_tiny", "a refusal still says which model it resolved to")

# 4. The propose baseline: a deterministic proposer for the forge's match loop.
p = b.invoke({"model": "propose", "input": {"function": "CameraManGame::calc", "oracle": {"kind": "behaviour"}}})
check(p["ok"] is True, "propose resolves and runs")
check(p["stopped"] == "complete", "propose completes")
check(p["deterministic"] is True, "the baseline is deterministic")
check(p["model"] == "rn_propose_baseline", "propose resolves to the baseline")
cands = p["output"]["candidates"]
check(isinstance(cands, list) and len(cands) == 3, "the baseline returns three ordered candidates")
check(cands[-1] == "ok", "the best-guess slot is the placeholder 'ok'")
check(cands[0].endswith("-wip-1"), "the first candidate is the wip-1 slot")
check(p["output"]["kind"] == "baseline", "the output says it is a baseline")

print("bicho core: %s" % ("all checks passed" if not failures else "%d failure(s)" % failures))
sys.exit(1 if failures else 0)
