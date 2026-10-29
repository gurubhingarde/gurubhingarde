#!/usr/bin/env python3
"""Double-clickable / `python run_gui.py` launcher for the GUI.

Works whether run from inside the package directory or one level up.
"""
import os
import sys

# allow running as a loose script (python actiway_pytool/run_gui.py) by making
# the parent importable as a package
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

try:
    from actiway_pytool.gui import main
except ModuleNotFoundError:
    # running from within the package dir without the parent on the path
    sys.path.insert(0, _here)
    from gui import main  # type: ignore

if __name__ == "__main__":
    main()
