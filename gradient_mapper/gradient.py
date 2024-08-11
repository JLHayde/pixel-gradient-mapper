import time

import numpy as np
from PySide6.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from PIL import Image

from image_reader import create_color_image, find_closest_color


def generate_perlin_noise(width, height, scale=10):
    def interpolate(pa, pb, px):
        return pa + (pb - pa) * px

    def generate_gradient_grid(grid_width, grid_height):
        gradients = np.random.rand(grid_height, grid_width, 2) * 2 - 1
        gradients /= np.linalg.norm(gradients, axis=2, keepdims=True)
        return gradients

    def dot_grid_gradient(ix, iy, x, y, gradients):
        dx, dy = x - ix, y - iy
        gradient = gradients[iy % gradients.shape[0], ix % gradients.shape[1]]
        return dx * gradient[0] + dy * gradient[1]

    grid_width = width // scale + 1
    grid_height = height // scale + 1
    gradients = generate_gradient_grid(grid_width, grid_height)

    noise = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            x0, y0 = x // scale, y // scale
            x1, y1 = x0 + 1, y0 + 1
            sx, sy = (x % scale) / scale, (y % scale) / scale

            n0 = dot_grid_gradient(x0, y0, x / scale, y / scale, gradients)
            n1 = dot_grid_gradient(x1, y0, x / scale, y / scale, gradients)
            ix0 = interpolate(n0, n1, sx)

            n0 = dot_grid_gradient(x0, y1, x / scale, y / scale, gradients)
            n1 = dot_grid_gradient(x1, y1, x / scale, y / scale, gradients)
            ix1 = interpolate(n0, n1, sx)

            noise[y, x] = interpolate(ix0, ix1, sy)

    return noise


def create_gradient(width, height, start_color, end_color, pos1=0, pos2=1):
    """
        Create a gradient image from start_color to end_color.
    """
    gradient = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        ratio = 0
        if y / height < pos1:
            ratio = 0
        elif y / height > pos2:
            ratio = 1
        else:
            ratio = (y / height - pos1) / (pos2 - pos1)

        color = [
            int(start_color[channel] * (1 - ratio) + end_color[channel] * ratio)
            for channel in range(3)
        ]
        gradient[y, :] = color

    return gradient


def apply_noise(image, noise_level):
    """
        Apply random noise to an image.
    """
    np.random.seed(500)
    noise = np.random.randint(-noise_level, noise_level, (image.shape[0], image.shape[1], 1), dtype=np.int16)
    noisy_image = image.astype(np.int16) + noise
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

    return noisy_image


def generate_image(width, height, start, end, noise, use_colour, pos1, pos2, filters=()):
    """

    :param width:
    :param height:
    :param start:
    :param end:
    :param noise:
    :param use_colour:
    :param pos1:
    :param pos2:
    :param filters:
    :return:
    """


    gradient = create_gradient(width, height, start, end, pos1, pos2)
    noisy_gradient = apply_noise(gradient, noise)
    image_size = 16
    cached_images = {}
    image_map = {}

    for x, i in enumerate(noisy_gradient):
        for y, j in enumerate(i):
            nd_key = tuple(j)

            img_path, col = find_closest_color(nd_key, item_filter=filters)

            if use_colour:

                clip_board = create_color_image(col)
            else:

                cached_clip = cached_images.get(img_path)

                if cached_clip:
                    clip_board = cached_clip
                else:
                    clip_board = Image.open(img_path)
                    cached_images[img_path] = clip_board

            qim = ImageQt(clip_board)
            pixmap = QPixmap.fromImage(qim)
            image_map[(y * image_size, x * image_size)] = {"pixmap": pixmap,
                                                           "block_path": img_path}

    return 0, image_map


if __name__ == "__main__":
    start_color = (176, 176, 176)
    end_color = (28, 28, 28)
    generate_image(12, 32, start_color, end_color, 2)
