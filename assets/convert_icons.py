#!/usr/bin/env python3
"""
assets/convert_icons.py — Convert SVG icons to PNG and ICO formats.

Tries conversion tools in order:
  1. cairosvg  (pip install cairosvg)
  2. rsvg-convert  (brew install librsvg)
  3. Inkscape  (brew install inkscape)

Usage:
  cd /Users/Matt/github/cross
  source .venv/bin/activate
  pip install cairosvg        # if not already installed
  python3 assets/convert_icons.py
"""

import os
import shutil
import subprocess
import sys

ASSETS = os.path.dirname(os.path.abspath(__file__))


def convert_cairosvg(svg_path, png_path, width, height):
    import cairosvg
    cairosvg.svg2png(url=svg_path, write_to=png_path,
                     output_width=width, output_height=height)


def convert_rsvg(svg_path, png_path, width, height):
    subprocess.run([
        'rsvg-convert', '-w', str(width), '-h', str(height),
        '-o', png_path, svg_path
    ], check=True)


def convert_inkscape(svg_path, png_path, width, height):
    subprocess.run([
        'inkscape', '--export-type=png',
        f'--export-width={width}', f'--export-height={height}',
        f'--export-filename={png_path}', svg_path
    ], check=True)


def find_converter():
    try:
        import cairosvg  # noqa
        print("Using: cairosvg")
        return convert_cairosvg
    except ImportError:
        pass
    if shutil.which('rsvg-convert'):
        print("Using: rsvg-convert")
        return convert_rsvg
    if shutil.which('inkscape'):
        print("Using: inkscape")
        return convert_inkscape
    print("ERROR: No SVG converter found.")
    print("  Install one:  pip install cairosvg")
    print("             or brew install librsvg")
    sys.exit(1)


def make_ico(png_paths, ico_path):
    """Bundle multiple PNGs into a .ico file using Pillow."""
    try:
        from PIL import Image
    except ImportError:
        print("  ICO: Pillow not found — run: pip install pillow")
        return
    images = [Image.open(p).convert('RGBA') for p in png_paths]
    images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images],
                   append_images=images[1:])
    print(f"  ICO: {ico_path}")


def main():
    convert = find_converter()

    jobs = [
        # (svg,                       png_out,                   w,   h)
        ('cross_icon_512.svg',   'cross_icon_512.png',   512, 512),
        ('cross_icon_128.svg',   'cross_icon_128.png',   128, 128),
        ('cross_favicon_32.svg', 'cross_favicon_32.png',  32,  32),
        ('cross_favicon_32.svg', 'cross_favicon_16.png',  16,  16),
    ]

    for svg_name, png_name, w, h in jobs:
        svg_path = os.path.join(ASSETS, svg_name)
        png_path = os.path.join(ASSETS, png_name)
        if not os.path.exists(svg_path):
            print(f"  SKIP: {svg_name} not found")
            continue
        convert(svg_path, png_path, w, h)
        print(f"  PNG: {png_path}  ({w}×{h})")

    # Bundle 32px and 16px into a .ico
    ico_sources = [
        os.path.join(ASSETS, 'cross_favicon_32.png'),
        os.path.join(ASSETS, 'cross_favicon_16.png'),
    ]
    if all(os.path.exists(p) for p in ico_sources):
        make_ico(ico_sources, os.path.join(ASSETS, 'favicon.ico'))

    # Also copy 512 PNG as the canonical GitHub avatar source
    src = os.path.join(ASSETS, 'cross_icon_512.png')
    if os.path.exists(src):
        print(f"\nDone. Files in {ASSETS}/")
        print("  cross_icon_512.png  — marketing / GitHub social preview / PyPI")
        print("  cross_icon_128.png  — app icon / README badge")
        print("  cross_favicon_32.png — favicon source")
        print("  cross_favicon_16.png — favicon source")
        print("  favicon.ico          — multi-size favicon for crossai.dev")


if __name__ == '__main__':
    main()

