"""Web interface for palettecraft.

This module defines a small Flask application that exposes a web UI
allowing users to upload an image and extract dominant colors. The app
leverages the same core algorithms as the command‑line interface, but
provides an interactive experience for demonstration purposes. The
palette is visualised using the :func:`generate_palette_image` helper.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import List, Tuple

from flask import Flask, render_template_string, request

from .core import extract_palette, generate_palette_image, complementary_color, rgb_to_hex


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        colors: List[Tuple[int, int, int]] = []
        comp_colors: List[Tuple[int, int, int]] = []
        preview_data: str | None = None
        message = None
        num_colors = 5
        complement_flag = False
        if request.method == "POST":
            file = request.files.get("image")
            num_colors = int(request.form.get("num_colors", 5))
            complement_flag = bool(request.form.get("complement"))
            if file and file.filename:
                # Save uploaded file to a temporary location
                temp_path = Path("/tmp") / file.filename
                file.save(temp_path)
                # Extract palette
                palette = extract_palette(str(temp_path), num_colors=num_colors)
                colors = [pc.rgb for pc in palette]
                if complement_flag:
                    comp_colors = [complementary_color(c) for c in colors]
                # Generate preview image
                image_colors: List[Tuple[int, int, int]] = colors.copy()
                image_colors.extend(comp_colors)
                preview = generate_palette_image(image_colors)
                buf = io.BytesIO()
                preview.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                preview_data = f"data:image/png;base64,{b64}"
            else:
                message = "Please upload an image."
        # Render a simple form and results
        return render_template_string(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>PaletteCraft</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .swatch { display: inline-block; width: 80px; height: 80px; margin: 4px; border: 1px solid #ccc; }
                    .hex-label { text-align: center; margin-top: 4px; font-size: 12px; }
                    .palette { margin-top: 20px; }
                    .palette img { max-width: 100%; }
                </style>
            </head>
            <body>
                <h1>PaletteCraft</h1>
                <p>Upload an image to extract its dominant colors.</p>
                {% if message %}<p style="color:red;">{{ message }}</p>{% endif %}
                <form method="post" enctype="multipart/form-data">
                    <label>Image file: <input type="file" name="image" accept="image/*" required></label><br><br>
                    <label>Number of colors: <input type="number" name="num_colors" value="{{ num_colors }}" min="1" max="12"></label><br><br>
                    <label><input type="checkbox" name="complement" {% if complement_flag %}checked{% endif %}> Include complementary colors</label><br><br>
                    <button type="submit">Extract Palette</button>
                </form>
                {% if colors %}
                    <div class="palette">
                        <h2>Palette</h2>
                        <div>
                        {% for c in colors %}
                            <div class="swatch" style="background-color: {{ rgb_to_hex(c) }};"></div>
                        {% endfor %}
                        </div>
                        <div>
                        {% for c in colors %}
                            <div class="hex-label">{{ rgb_to_hex(c) }}</div>
                        {% endfor %}
                        </div>
                        {% if comp_colors %}
                            <h2>Complementary Colors</h2>
                            <div>
                            {% for c in comp_colors %}
                                <div class="swatch" style="background-color: {{ rgb_to_hex(c) }};"></div>
                            {% endfor %}
                            </div>
                            <div>
                            {% for c in comp_colors %}
                                <div class="hex-label">{{ rgb_to_hex(c) }}</div>
                            {% endfor %}
                            </div>
                        {% endif %}
                        {% if preview_data %}
                            <h2>Preview Image</h2>
                            <img src="{{ preview_data }}" alt="Palette preview">
                        {% endif %}
                    </div>
                {% endif %}
            </body>
            </html>
            """,
            colors=colors,
            comp_colors=comp_colors,
            num_colors=num_colors,
            complement_flag=complement_flag,
            preview_data=preview_data,
            rgb_to_hex=rgb_to_hex,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
