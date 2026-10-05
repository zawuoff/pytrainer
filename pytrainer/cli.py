"""The `pytrainer` command (and `python -m pytrainer`): start the server and open the app.

Works from a checkout (server.py next to the package) and from an installed wheel, where server.py
is shipped inside the package as `pytrainer.server`.
"""

from __future__ import annotations

import sys


def _server():
    try:
        from pytrainer import server  # installed: the wheel puts server.py inside the package
    except ImportError:
        import server  # a checkout: server.py sits next to the pytrainer package
    return server


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Run as a command, PyTrainer opens the browser unless asked not to (the server alone doesn't).
    if "--no-open" in argv:
        argv.remove("--no-open")
    elif "--open" not in argv:
        argv.append("--open")
    sys.argv = [sys.argv[0], *argv]
    _server().main()


if __name__ == "__main__":
    main()
