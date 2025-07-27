"""Core functionality for the palettecraft package.

This module contains helper functions for extracting dominant colors from
images using k‑means clustering and computing complementary colors. The
implementation relies on NumPy, scikit‑learn and Pillow. The k‑means
algorithm groups pixel colors into clusters whose centroids form the
extracted palette; this technique is commonly used for color
quantization, where the continuous color space of an image is reduced to
a discrete palette of representative colors【722129937005762†L27-L55】.

Color theory functions such as :func:`complementary_color` use the HSL
color model. According to color theory, a hue rotated by 180° yields the
complement on the color wheel【572665502347611†L78-L86】. These helpers
provide simple ways to derive harmonious palettes.
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


@dataclass
class PaletteColor:
    """Represents a color in both RGB and hexadecimal formats."""

    rgb: Tuple[int, int, int]

    def to_hex(self) -> str:
        """Return the color as a hex string (e.g. ``#aabbcc``)."""
        return rgb_to_hex(self.rgb)


def rgb_to_hex(color: Tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a hexadecimal color string.

    Parameters
    ----------
    color : tuple of int
        The RGB values (0‑255 each).

    Returns
    -------
    str
        The corresponding hex string, starting with ``#``.
    """
    return "#" + "".join(f"{c:02x}" for c in color)


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """Convert a hex string to an RGB tuple.

    Parameters
    ----------
    value : str
        The hexadecimal color (with or without ``#`` prefix).

    Returns
    -------
    tuple of int
        The corresponding RGB values.
    """
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid hex color: {value}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def extract_palette(image_path: str, num_colors: int = 5, resize: int | None = 500) -> List[PaletteColor]:
    """Extract the dominant colors from an image using k‑means clustering.

    The function loads the image, optionally resizes it to speed up
    clustering, then reshapes the pixel data into a 2D array with one
    row per pixel and three columns for RGB. A k‑means model is fit
    using `num_colors` clusters. The cluster centroids represent the
    palette【722129937005762†L62-L66】. Colors are returned sorted by
    luminance (approximate brightness).

    Parameters
    ----------
    image_path : str
        Path to the input image.
    num_colors : int, default=5
        The number of dominant colors to extract.
    resize : int or None, optional
        If provided, the image's largest dimension will be scaled down to
        this size before clustering. Use ``None`` to disable resizing.

    Returns
    -------
    list of PaletteColor
        The extracted palette colors sorted from darkest to lightest.
    """
    # Load image and convert to RGB
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        # Optional downsample to speed up processing
        if resize is not None:
            max_dim = max(img.size)
            if max_dim > resize:
                scale = resize / max_dim
                new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                img = img.resize(new_size)
        data = np.array(img)

    # Flatten the image data into Nx3 array for k‑means【722129937005762†L62-L66】
    pixels = data.reshape(-1, 3)
    # Fit k‑means
    model = KMeans(n_clusters=num_colors, random_state=0)
    model.fit(pixels)
    centers = model.cluster_centers_.astype(int)

    # Sort palette by perceived brightness (luminance)
    def luminance(color: Tuple[int, int, int]) -> float:
        r, g, b = color
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    palette_sorted = sorted([tuple(c) for c in centers], key=luminance)
    return [PaletteColor(rgb=c) for c in palette_sorted]


def complementary_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Compute the complementary color for an RGB value using HSL rotation.

    This function converts an RGB color to HSL, rotates the hue by 180° to
    find the opposite hue on the color wheel, then converts back to RGB.
    According to color theory, the complement of a given hue lies on the
    opposite side of the wheel【572665502347611†L78-L86】.

    Parameters
    ----------
    color : tuple of int
        The RGB color for which to compute the complement.

    Returns
    -------
    tuple of int
        The complementary RGB color.
    """
    r, g, b = [c / 255.0 for c in color]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # Rotate hue by 180 degrees (0.5 in normalized units)
    h = (h + 0.5) % 1.0
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return (int(round(r2 * 255)), int(round(g2 * 255)), int(round(b2 * 255)))


def generate_palette_image(
    palette: List[Tuple[int, int, int]],
    width: int = 600,
    height: int = 100,
    border: int = 2,
    show_labels: bool = True,
    font_path: str | None = None,
) -> Image.Image:
    """Generate an image showing the palette colors as horizontal swatches.

    Parameters
    ----------
    palette : list of tuple
        A list of RGB colors to display.
    width : int
        Width of the generated image.
    height : int
        Height of the generated image.
    border : int
        Border thickness between swatches.
    show_labels : bool
        If ``True``, label each swatch with its hex code.
    font_path : str or None
        Optional path to a TrueType font to use for labels.

    Returns
    -------
    PIL.Image
        An image containing the palette.
    """
    from PIL import ImageDraw, ImageFont

    n = len(palette)
    swatch_width = (width - (n + 1) * border) // n
    swatch_height = height - 2 * border
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Load font
    if font_path is None:
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, 14)

    for i, color in enumerate(palette):
        x0 = border + i * (swatch_width + border)
        y0 = border
        x1 = x0 + swatch_width
        y1 = y0 + swatch_height
        draw.rectangle([x0, y0, x1, y1], fill=color)
        if show_labels:
            text = rgb_to_hex(color)
            text_width, text_height = draw.textsize(text, font=font)
            tx = x0 + (swatch_width - text_width) / 2
            ty = y0 + (swatch_height - text_height) / 2
            # Draw semi‑transparent background for readability
            bg_padding = 2
            bg_box = [
                tx - bg_padding,
                ty - bg_padding,
                tx + text_width + bg_padding,
                ty + text_height + bg_padding,
            ]
            draw.rectangle(bg_box, fill=(255, 255, 255, 200))
            draw.text((tx, ty), text, fill=(0, 0, 0), font=font)

    return img
