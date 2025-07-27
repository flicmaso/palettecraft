"""Command‑line interface for palettecraft.

This module defines a ``palettecraft`` console command using the Click
library. Users can extract dominant colors from an image, generate a
preview swatch, and output palette information as JSON. It provides
options to compute complementary colors and adjust the number of
clusters for k‑means.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Tuple

import click

from .core import extract_palette, generate_palette_image, rgb_to_hex, complementary_color


@click.command(context_settings={"show_default": True})
@click.argument("image_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--colors", "num_colors", default=5, show_default=True, help="Number of dominant colors to extract.")
@click.option("--complement", is_flag=True, help="Also compute and display complementary colors.")
@click.option("--out-image", type=click.Path(dir_okay=False), help="Path to save a palette preview image (PNG).")
@click.option("--out-json", type=click.Path(dir_okay=False), help="Path to save palette information as JSON.")
@click.option("--resize", default=500, show_default=True, type=int, help="Resize the largest dimension to this size before clustering. Use 0 to disable.")
def main(image_path: str, num_colors: int, complement: bool, out_image: str | None, out_json: str | None, resize: int) -> None:
    """Extract a color palette from IMAGE_PATH using k‑means clustering.

    IMAGE_PATH is the path to the image from which to extract colors. The
    command will print the extracted palette (and optionally complementary
    palette) as hex codes. Use ``--out-image`` to save a preview image of
    the palette and ``--out-json`` to save palette information as JSON.
    """
    # Determine resize parameter
    resize_param = None if resize == 0 else resize
    palette_colors = extract_palette(image_path, num_colors=num_colors, resize=resize_param)

    # Extract complementary colors if requested
    if complement:
        comp_palette = [complementary_color(pc.rgb) for pc in palette_colors]
    else:
        comp_palette = []

    # Print palettes to stdout
    click.echo("Dominant colors:")
    for idx, pc in enumerate(palette_colors, start=1):
        click.echo(f"  {idx}. {rgb_to_hex(pc.rgb)} {pc.rgb}")
    if complement:
        click.echo("\nComplementary colors:")
        for idx, c in enumerate(comp_palette, start=1):
            click.echo(f"  {idx}. {rgb_to_hex(c)} {c}")

    # Save palette preview image
    if out_image:
        # Build list of colors (dominant + optional complementary)
        colors_to_render: List[Tuple[int, int, int]] = [pc.rgb for pc in palette_colors]
        if complement:
            colors_to_render.extend(comp_palette)
        img = generate_palette_image(colors_to_render)
        out_path = Path(out_image)
        img.save(out_path)
        click.echo(f"Saved palette image to {out_path}")

    # Save palette JSON
    if out_json:
        # Prepare JSON‑serializable data by converting NumPy types to built‑in
        # Python ints. Without this conversion, json.dump will raise a
        # TypeError because NumPy int64 objects are not serializable.
        def serialize_rgb(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
            return tuple(int(x) for x in rgb)

        data = {
            "dominant_colors": [
                {
                    "rgb": serialize_rgb(pc.rgb),
                    "hex": rgb_to_hex(pc.rgb),
                }
                for pc in palette_colors
            ],
        }
        if complement:
            data["complementary_colors"] = [
                {"rgb": serialize_rgb(c), "hex": rgb_to_hex(c)} for c in comp_palette
            ]
        out_jpath = Path(out_json)
        with out_jpath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        click.echo(f"Saved palette JSON to {out_jpath}")

    # If script is run interactively, return success code
    return None


if __name__ == "__main__":
    sys.exit(main())
