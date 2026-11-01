"""Prepare the portrait: remove background (rembg), crop head+shoulders, grayscale, CLAHE.

Usage: python scripts/prep_photo.py [input] [output]
Output is a 16-bit-free RGBA PNG: L channel in RGB, subject mask in alpha.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "photo.jpg"
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets" / "portrait_prepped.png"

# Crop geometry, relative to the subject's bounding box.
CROP_W = 0.62   # crop width as a fraction of bbox width (shoulders)
TOP_PAD = 0.07  # headroom above the hair, as a fraction of crop size


def main() -> None:
    img = Image.open(SRC).convert("RGB")
    cut = remove(img, session=new_session("isnet-general-use"), alpha_matting=False)
    alpha = np.array(cut)[..., 3]
    alpha = cv2.morphologyEx((alpha > 128).astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ys, xs = np.where(alpha > 0)
    x0, x1, y0 = xs.min(), xs.max(), ys.min()

    # Square crop (the ASCII grid is ~square): centred on the head, from the hair down.
    head_cx = int(np.median(xs[ys < y0 + (ys.max() - y0) * 0.12]))
    size = int((x1 - x0) * CROP_W)
    top = max(0, int(y0 - size * TOP_PAD))
    left = int(np.clip(head_cx - size // 2, 0, img.width - size))
    box = (left, top, left + size, min(img.height, top + size))

    rgb = np.array(img)[box[1]:box[3], box[0]:box[2]]
    mask = alpha[box[1]:box[3], box[0]:box[2]]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6)).apply(gray)

    out = np.dstack([gray, gray, gray, mask])
    Image.fromarray(out, "RGBA").save(DST)
    print(f"bbox x[{x0},{x1}] top {y0}; crop {box}; wrote {DST}")


if __name__ == "__main__":
    main()
