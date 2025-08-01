#!/usr/bin/env python3
import sys
import os

# 1) Insert the `src/` directory at the front of sys.path
HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# 2) Now import your package exactly the same way the one-dir build does
from gameController import GameController

if __name__ == "__main__":
    GameController().run()
