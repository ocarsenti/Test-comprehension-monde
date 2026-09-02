"""
Script ponctuel : détoure les images JOHN/john_2/john_3 (fond blanc uni)
en PNG transparent, façon les autres avatars (*-cutout.png), par
flood-fill depuis les coins — n'attaque que le fond connecté aux bords,
laisse intact le blanc à l'intérieur du personnage (col de chemise...).
"""

import numpy as np
from PIL import Image
from scipy.ndimage import label

WHITE_THRESHOLD = 235  # tolérance : pixel considéré "fond" si R,G,B tous au-dessus


def cutout(src_path: str, dst_path: str, pad_crop: bool = True):
    im = Image.open(src_path).convert("RGBA")
    arr = np.array(im)
    rgb = arr[:, :, :3].astype(int)

    is_bgish = np.all(rgb >= WHITE_THRESHOLD, axis=-1)

    labeled, _ = label(is_bgish)
    corner_labels = {
        labeled[0, 0], labeled[0, -1], labeled[-1, 0], labeled[-1, -1],
    }
    corner_labels.discard(0)

    bg_mask = np.isin(labeled, list(corner_labels)) if corner_labels else np.zeros_like(is_bgish)

    arr[:, :, 3] = np.where(bg_mask, 0, arr[:, :, 3])

    out = Image.fromarray(arr, mode="RGBA")

    if pad_crop:
        alpha = np.array(out)[:, :, 3]
        rows = np.any(alpha > 0, axis=1)
        cols = np.any(alpha > 0, axis=0)
        if rows.any() and cols.any():
            top, bottom = np.where(rows)[0][[0, -1]]
            left, right = np.where(cols)[0][[0, -1]]
            pad = 6
            top = max(0, top - pad)
            left = max(0, left - pad)
            bottom = min(out.height, bottom + pad + 1)
            right = min(out.width, right + pad + 1)
            out = out.crop((left, top, right, bottom))

    out.save(dst_path)
    print(f"{src_path} -> {dst_path} {out.size}")


if __name__ == "__main__":
    cutout("JOHN.png", "john-intro-cutout.png")
    cutout("john_2.png", "john-2-cutout.png")
    cutout("john_3.png", "john-3-cutout.png")
