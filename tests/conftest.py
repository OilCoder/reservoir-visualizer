"""
Pytest configuration for reservoir-visualizer.

Adds the project root to sys.path so that `src` is importable
without installing the package.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
