# import subprocess
import subprocess
import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import filedialog
import os
import streamlit as st
import win32clipboard
from PIL import Image

def page_setup(page_name="PyPSA UI"):
    st.set_page_config(
        page_title=page_name,
        page_icon="📈",
        layout="wide",
    )
    hide_streamlit_style = """
                <style>
                   
                    button {background-color: blue;}
                    footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def open_location(location):
    # Open Windows Explorer at the specified folder
    if os.path.exists(location):
        subprocess.run(["explorer", location])


def list_directories_with_paths(base_directory):
    """
    Returns a dictionary where keys are directory names and values are their full paths,
    for directories within the given base directory.

    :param base_directory: Path to the base directory
    :return: Dictionary of directory names and their full paths
    """
    directories = {}  # Dictionary to store directory names and paths
    with os.scandir(base_directory) as entries:
        for entry in entries:
            if entry.is_dir():  # Check if the entry is a directory
                directories[entry.name] = (
                    entry.path
                )  # Add directory name and path to the dictionary

    return directories


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

def get_package_version():
    from afripow_pypsa.Report.Report import __version__

    return __version__


def package_version(sidebar=True):
    __version__ = get_package_version()
    v = f":green[Toolbox version: {__version__}]"

    if sidebar:
        st.sidebar.write(v)
    else:
        st.sidebar.write(v)


def select_folder():
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    root.withdraw()
    folder_path = filedialog.askdirectory(master=root, initialdir=os.getcwd())
    root.destroy()
    return folder_path


def refresh_button(sidebar=True):
    if sidebar:
        if st.sidebar.button("Refresh", type="secondary", use_container_width=True):
            st.experimental_rerun()
    else:
        if st.button("Refresh"):
            st.experimental_rerun()


def apply_cell_colors(s):
    return ["background-color: %s" % color for color in s]


def find_files_containing_string(path, target_string):
    matching_filenames = []  # List to hold names of files containing the target string in their name
    for root, dirs, files in os.walk(path):
        for file in files:
            if target_string in file:
                matching_filenames.append(file)  # Append the filename (not path) that contains the target string
    return matching_filenames



def clip(filepath, clip_type=win32clipboard.CF_DIB ):
    if st.button(":scissors:",  key=filepath):
        image = Image.open(filepath)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()
        st.info(f"Sent to clipboard", icon='✂️')