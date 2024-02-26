# import subprocess
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import os
import streamlit as st


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
                directories[
                    entry.name
                ] = entry.path  # Add directory name and path to the dictionary

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


def find_int_named_subdirs(path):
    """
    Finds all subdirectories within the given path whose names can be cast to an integer.

    :param path: The path to search within.
    :return: A list of subdirectory names (as integers) that can be cast to an integer.
    """
    int_named_subdirs = []

    # Walk through the directory structure starting at the given path
    for root, dirs, _ in os.walk(path):
        # Check each directory in dirs for subdirectories that can be cast to an integer
        for dir_name in dirs:
            if (
                dir_name.isdigit()
            ):  # Check if the directory name can be cast to an integer
                full_dir_path = os.path.join(root, dir_name)
                # Add the directory name (as integer) to the list
                int_named_subdirs.append(int(dir_name))

    return int_named_subdirs


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
        if st.sidebar.button("Refresh", type="primary", use_container_width=True):
            st.experimental_rerun()
    else:
        if st.button("Refresh"):
            st.experimental_rerun()


def apply_cell_colors(s):
    return ['background-color: %s' % color for color in s]