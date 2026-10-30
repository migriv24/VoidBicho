"""python -m bicho  describe | fetch NAME | invoke '{json}' | serve

`serve` keeps models loaded and answers one JSON request per line on stdin with one JSON
response per line on stdout: the shape a host (Void Squid, a toolbox) drives as a process
holiday, so a model is loaded once per session rather than once per image.
"""
import json, sys
from .core import Bicho


def main(argv):
    cmd = argv[0] if argv else "describe"
    b = Bicho()
    if cmd == "describe":
        print(json.dumps(b.describe(), indent=1))
    elif cmd == "fetch":
        print(json.dumps(b.fetch(argv[1])))
    elif cmd == "invoke":
        print(json.dumps(b.invoke(json.loads(argv[1]))))
    elif cmd == "serve":
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                r = b.invoke(json.loads(line))
            except Exception as e:  # malformed request: still one line back
                r = {"ok": False, "stopped": "refused", "output": {"why": str(e)}}
            sys.stdout.write(json.dumps(r) + "\n")
            sys.stdout.flush()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
