"""Download the GitHub avatar and prep it for ASCII conversion:
square crop, autocontrast, sharpen, 1024px PNG."""
import io
import os

import requests
from PIL import Image, ImageFilter, ImageOps

from theme import USERNAME

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "photo_prepped.png")

# Fractional crop box (l, t, r, b) applied before the square fit — tuned to
# frame head + shoulders in the current avatar. Set to None for no crop.
CROP = (0.14, 0.0, 0.58, 0.52)


def main():
    r = requests.get(f"https://github.com/{USERNAME}.png?size=1024", timeout=30)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img = ImageOps.exif_transpose(img)

    if CROP:
        w, h = img.size
        img = img.crop((int(CROP[0] * w), int(CROP[1] * h),
                        int(CROP[2] * w), int(CROP[3] * h)))

    side = min(img.size)
    img = ImageOps.fit(img, (side, side))
    img = img.resize((1024, 1024), Image.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=80))
    img.save(OUT)
    print(f"prepped avatar -> {OUT}")


if __name__ == "__main__":
    main()
