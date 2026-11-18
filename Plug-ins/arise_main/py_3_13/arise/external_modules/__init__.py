import os
import sys

RELATIVE_PATH = os.path.dirname(os.path.realpath(__file__))

if RELATIVE_PATH not in sys.path:
    sys.path.append(RELATIVE_PATH)
