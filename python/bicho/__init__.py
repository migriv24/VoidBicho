"""Void Bicho, first runtime (2026-10-10): local models behind one invocation contract.

    from bicho import Bicho
    b = Bicho()
    r = b.invoke({"model": "segment-2d AND local", "input": {"image": "view.png"}})
    r["ok"], r["model"], r["stopped"], r["output"]

The contract is okf/concepts/invocation.md: every response carries ok, output, the model that
actually ran (resolved from the tag query), the params as applied, cost, deterministic and
stopped. A refusal is a value (`stopped: "refused"` with a reason), never an exception.
Bicho returns bytes and numbers and does not interpret them (okf/design/boundaries.md §4.2):
what a mask *is* is the host's business.
"""
from .core import Bicho, query  # noqa: F401
