from pathlib import Path

import anvil.server
import anvil.mpl_util
import anvil.tables as tables
import anvil.tables.query as q
from afripow_pypsa.helpers.direcory_cases import find_int_named_subdirs
from anvil.tables import app_tables


SERVER_CODE = "server_KNWCZUHD5SWB7REKG2WMXXSQ-TS26GMPFWK6K4QPO"
anvil.server.connect(SERVER_CODE)


def find_all_images(directory: Path) -> dict:
    """
    This function takes a directory as a Path object and returns a dictionary
    with the filename (without the extension) as the key and the full absolute
    path to the image file as the value.
    """
    images_dict = {}
    # Define supported image extensions
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

    # Iterate over all image files in the directory
    for image_path in directory.glob("*"):
        if image_path.suffix.lower() in image_extensions:
            # Use the stem (filename without extension) as the key
            images_dict[image_path.stem] = str(image_path.resolve())

    return images_dict


@anvil.server.callable
def send_images():
    print("here")
    year = "2039"
    p = Path(
        r"C:\Users\tobie\PycharmProjects\afripow-pypsa-reporting\case_bwa\Opti\reporting_outputs_Results_opt"
    ) / Path(year)
    print(p)
    all_images = find_all_images(p)
    print(all_images)

    images = []

    for link in all_images.keys():
        with open(all_images[link], "rb") as f:
            images.append(anvil.BlobMedia("image/png", f.read()))

    print(images)
    return images


anvil.server.wait_forever()
