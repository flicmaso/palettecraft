"""Top level package for palettecraft.

This package provides utilities for extracting dominant colors from images
using k‑means clustering and for generating complementary color schemes.

The main user interface is via the :mod:`palettecraft.cli` module, which
exposes a command‑line interface. Programmatic access is provided via
functions in :mod:`palettecraft.core`.

"""

from .core import extract_palette, generate_palette_image, rgb_to_hex, complementary_color

__all__ = [
    "extract_palette",
    "generate_palette_image",
    "rgb_to_hex",
    "complementary_color",
]
