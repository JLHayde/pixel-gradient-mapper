import image_reader
import os
import shutil
if __name__ == "__main__":

    for k, v in image_reader.load_texture_mappings()["mappings"].items():

        from_ = k
        to_ = os.path.join(os.path.dirname(__file__), "pallete", os.path.basename(k))
        print(f"Copying {from_} to {to_}")
        shutil.copy(from_, to_)

