import os
from importlib import reload

import constants


def search_folder(directory, file_extension=None):
    """
    Recursively search for files in a directory.
    :param directory: The directory to search in.
    :param file_extension: If specified, only files with this extension will be listed.
    :return: List of file paths.
    """
    reload(constants)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not any(map(file.__contains__, constants.IGNORED_TEXTURES)):
                if file_extension is None or file.endswith(file_extension):
                    yield os.path.join(root, file)
