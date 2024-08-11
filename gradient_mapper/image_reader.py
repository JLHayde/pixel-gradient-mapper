import os.path
from functools import lru_cache

from PIL import Image
from PIL import ImageCms
import numpy as np
from scipy.spatial import distance
import io
import constants
import image_fetch
import pickle

CACHE_FILE = "cache.grd"


def convert_to_srgb(img):
    """
        Convert PIL image to sRGB color space (if possible)
    """
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img


def get_average_color(image_path, ):
    """
    Calculate the average color of an image.
    """

    img = Image.open(image_path).convert('RGB')
    img = convert_to_srgb(img)
    np_img = np.array(img)

    if img.width == img.height:
        avg_color_per_channel = np.mean(np_img, axis=(0, 1))

        # Convert to integers for R, G, B values
        avg_color = tuple(avg_color_per_channel.astype(int))

        return avg_color


def map_average_colours(textures: list[str]):
    """

    :param textures:
    :return:
    """

    colour_map = {}
    for image_paths in textures:
        average_colour = get_average_color(image_paths)
        if average_colour:
            colour_map[image_paths] = average_colour

    return colour_map


def create_color_image(color, width=16, height=16):
    """
        Create an image of a specified color.
    :param color: A tuple representing the RGB color (e.g., (255, 0, 0) for red).
    :param width: Width of the image.
    :param height: Height of the image.
    :return: A PIL Image object.
    """
    # Create an image with the given color
    img = Image.new("RGB", (width, height), color)
    return img


filters = constants.IGNORED_TEXTURES


def load_texture_mappings(rebuild=False, filter=filters):
    """
        Load the cached file of images mapped to their calculated average colour,
        Build cache if one does not exist or force rebuild if filter has changed.
    :param rebuild:
    :param filter:
    :return:
    """
    texture_mapping = {}

    if os.path.isfile(CACHE_FILE) and not rebuild:
        with open(CACHE_FILE, "rb") as cache:
            print("loading cache")
            texture_mapping = pickle.load(cache)
            cached_filter = texture_mapping["filtered_list"]
            if cached_filter != filter:
                print("Texture filter has changed")
                return load_texture_mappings(rebuild=True)
    else:

        palette_folder = os.path.join(os.path.dirname(__file__), "palette")
        textures = image_fetch.search_folder(palette_folder, "png")
        mapping = map_average_colours(textures)

        texture_mapping = {"mappings": mapping,
                           "filtered_list": constants.IGNORED_TEXTURES}
        with open(CACHE_FILE, "wb") as cache:
            print("Writing cache")
            pickle.dump(texture_mapping, cache)

    return texture_mapping


TEXTURES = load_texture_mappings()["mappings"]


@lru_cache(maxsize=None) # Use cache to save calculating the nearest colour
def find_closest_color(target_color, item_filter=()):
    closest_color = None
    min_dist = float('inf')
    closest_image_path = None

    for image_path, color in TEXTURES.items():
        if image_path not in item_filter:
            dist = distance.euclidean(target_color, color)
            if dist < min_dist:
                min_dist = dist
                closest_color = color
                closest_image_path = image_path

    return closest_image_path, closest_color
