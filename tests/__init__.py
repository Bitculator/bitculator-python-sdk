"""Make the src-layout package importable when running the tests from a checkout."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
