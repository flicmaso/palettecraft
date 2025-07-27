# PaletteCraft

PaletteCraft is a Python library and command‑line tool for extracting dominant colors
from images and generating simple color schemes. It uses **k‑means clustering** to
group the pixels in an image and treat the resulting cluster centroids as a
palette of representative colors. Complementary colors are calculated by
rotating hues in the HSL color space by 180°. The project includes a small
Flask web application to demonstrate the functionality.

## Features

* Extracts dominant colors from any raster image using the k‑means algorithm.
* Returns colors as both RGB tuples and hexadecimal strings.
* Optionally computes complementary colors for the palette.
* Generates a preview image of the palette with labelled swatches.
* Command‑line interface for quick usage on local files.
* Web interface built with Flask for interactive experimentation.

## Installation

Clone this repository and install the package in editable mode. A virtual
environment is recommended.

```bash
git clone https://github.com/youruser/palettecraft.git
cd palettecraft
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

The core dependencies include [Pillow](https://python-pillow.org/),
[NumPy](https://numpy.org/), [scikit‑learn](https://scikit-learn.org/),
[Click](https://click.palletsprojects.com/) and [Flask](https://flask.palletsprojects.com/).

## Command‑line usage

The package installs a script called `palettecraft`. Running it with an image
path extracts the top five colors by default:

```bash
palettecraft path/to/your/image.jpg

# specify more or fewer colors
palettecraft path/to/image.png --colors 8

# include complementary colors and save a preview image
palettecraft path/to/image.jpg --complement --out-image my_palette.png

# output palette data to JSON
palettecraft path/to/image.jpg --out-json palette.json
```

### Options

```
Usage: palettecraft [OPTIONS] IMAGE_PATH

  Extract a color palette from IMAGE_PATH using k‑means clustering.

Arguments:
  IMAGE_PATH  Path to the input image [required]

Options:
  --colors INTEGER        Number of dominant colors to extract. [default: 5]
  --complement            Also compute and display complementary colors.
  --out-image PATH        Path to save a palette preview image (PNG).
  --out-json PATH         Path to save palette information as JSON.
  --resize INTEGER        Resize the largest dimension before clustering. Use 0
                          to disable. [default: 500]
  --help                  Show this message and exit.
```

## Web interface

A minimal web application is included for convenience. Launch it by running:

```bash
python -m palettecraft.webapp
```

The server will start on `http://127.0.0.1:5000/`. Upload an image through
the browser to see the dominant and complementary colors. The preview image
shows the palette horizontally with optional complementary colors appended.

## How it works

PaletteCraft reshapes the input image into an ``N×3`` array where each row
corresponds to a pixel’s RGB values. It then fits a k‑means clustering model
from scikit‑learn with ``k`` clusters. The cluster centroids are taken as the
dominant colors. K‑means iteratively assigns pixels to the nearest centroid
and recomputes centroids until convergence. Colors are sorted by luminance
for display purposes. Complementary colors are computed by converting an RGB
color to HSL, adding 180° to the hue, and converting back to RGB.

## License

PaletteCraft is released under the MIT License. See ``LICENSE`` for details.