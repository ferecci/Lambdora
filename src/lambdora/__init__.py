"""Lambdora - A minimalist Lisp-inspired functional language."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("lambdora")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development/testing
    __version__ = "dev"
