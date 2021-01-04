from colorsys import rgb_to_hls, hls_to_rgb
import numpy as np
from skimage import io


def fix_channels(img, fix_invert=True, force_trans=-1):
    """
    Forces images to be in RGBA format.
    """
    try:
        height, width, channels = img.shape
    except ValueError:
        height, width = img.shape
        channels = 1
    pixels = np.int8(img.reshape(width, -1, channels))
    oned = []
    if channels == 1:
        for w in range(width):
            for h in range(height):
                pixel = pixels[w, h] % 255
                if force_trans < 0:
                    force_trans = 255
                oned.extend([pixel, pixel, pixel, force_trans])
    else:
        for w in range(width):
            # oned = []
            for h in range(height):
                if channels == 4 and force_trans < 0:
                    pixel = pixels[w, h]
                    if fix_invert:
                        oned.extend([pixel[2] % 255, pixel[1] % 255, pixel[0] % 255, pixel[3] % 256])
                    else:
                        oned.extend([pixel[0] % 255, pixel[1] % 255, pixel[2] % 255, pixel[3] % 256])
                else:
                    pixel = pixels[w, h]
                    if force_trans < 0:
                        force_trans = 255
                    if fix_invert:
                        oned.extend([pixel[2] % 255, pixel[1] % 255, pixel[0] % 255, force_trans])
                    else:
                        oned.extend([pixel[0] % 255, pixel[1] % 255, pixel[2] % 255, force_trans])
        # last.append(oned)
    ar = np.array(oned)
    ar = ar.reshape(height, -1, 4)
    return ar


def map_sat(r1, g1, b1, r2, g2, b2):
    h1, l1, s1 = rgb_to_hls(r1 / 255, g1 / 255, b1 / 255)
    h2, l2, s2 = rgb_to_hls(r2 / 255, g2 / 255, b2 / 255)
    r3, g3, b3 = hls_to_rgb(h2, l1, (s1 + s2) / 2)
    return int(r3 * 255), int(g3 * 255), int(b3 * 255)


def color_image(img, r, g, b):
    pixels = img
    height, width, channels = img.shape
    img_rows = []
    img_stitched = None
    for h in range(height):
        row_image = None
        for w in range(width):
            p = pixels[h, w]
            a = p[3] % 256
            if a > 0:
                # If we don't copy, it actually gets modified.
                i = p.copy()
                new = map_sat(i[0], i[1], i[2], r, g, b)
                i[0] = new[0]
                i[1] = new[1]
                i[2] = new[2]
                i[3] = a
            else:
                i = p
            i = i.reshape((1, 1, 4))
            if row_image is None:
                row_image = i
            else:
                row_image = np.concatenate((row_image, i), axis=1)

        img_rows.append(row_image)
    for i in img_rows:
        if img_stitched is None:
            img_stitched = i
        else:
            img_stitched = np.concatenate((img_stitched, i), axis=0)

    return img_stitched


def color_image_checked(img, r, g, b, check=True):
    img = fix_channels(img)
    if check and not is_grayscale(img):
        return img
    return color_image(img, r, g, b)


def load_and_color(img_path, r, g, b):
    img = io.imread(img_path)
    return color_image_checked(img, r, g, b)


def is_grayscale(img):
    pixels = img
    height, width, channels = img.shape
    if channels == 1:
        return True
    for h in range(height):
        for w in range(width):
            p = pixels[h, w]
            if p[0] == p[1] == p[2]:
                continue
            else:
                return False
    return True
