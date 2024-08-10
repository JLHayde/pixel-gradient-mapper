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

from PySide6.QtCore import QSettings

CACHE_FILE = "cache.grd"


def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

def get_average_color(image_path,):
    """
    Calculate the average color of an image.
    """

    #if dominant:
    #color_thief = ColorThief(image_path)
    #dominant_color = color_thief.get_color(quality=1)



    img = Image.open(image_path).convert('RGB')  # Ensure the image is in RGB format
    img = convert_to_srgb(img)
    np_img = np.array(img)

    if img.width == img.height:

        avg_color_per_channel = np.mean(np_img, axis=(0, 1))

        # Convert to integers for R, G, B values
        avg_color = tuple(avg_color_per_channel.astype(int))

        return avg_color

    #array1 = np.array(avg_color_per_channel)
    #array2 = np.array(dominant_color)
#
    ## Calculate the mean of the two arrays
    #avg_array = (array1 + array2) / 2
#
    #avg_color = tuple(avg_array.astype(int))








def map_average_colours(textures: list[str]):

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

    texture_mapping = {}

    if os.path.isfile(CACHE_FILE) and not rebuild:
        with open(CACHE_FILE, "rb") as cache:
            print("loading cache")
            texture_mapping = pickle.load(cache)
            cached_filter = texture_mapping["filtered_list"]
#
            if cached_filter != filter:
                print("Texture filter has changed")
                return load_texture_mappings(rebuild=True)
#
    else:

        palette_folder = os.path.join(os.path.dirname(__file__), "palette")

        textures = image_fetch.search_folder(palette_folder,
                                             "png")

        mapping = map_average_colours(textures)




        texture_mapping = {"mappings": mapping,
                            "filtered_list": constants.IGNORED_TEXTURES}
        with open(CACHE_FILE, "wb") as cache:
            print("Writing cache")
            pickle.dump(texture_mapping, cache)

    return texture_mapping

TEXTURES = load_texture_mappings()["mappings"]

@lru_cache(maxsize=None)
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

#target_color = (54, 54, 54)

#mappings = load_texture_mappings()["mappings"]

#print(mappings)

#c#losest_image_path, closest_color = find_closest_color(target_color, mappings)
#print(closest_image_path)

#im = Image.open(closest_image_path)

#target = create_color_image(target_color)
#match = create_color_image(closest_color)
#im2 = Image.from
#i#m.show()
#target.show()
#match.show()