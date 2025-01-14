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
import pandas as pd

def load_file(filename, sheet_name):
    """Loads an Excel file with pandas and turn the sheet into a dataframe"""
    df = pd.read_excel(filename, sheet_name=sheet_name)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    return df


def file_selector(folder_path, show_context):
    """Produces a file selector of all files meeting the criteria:
    ext = "xlsm" and
    __setup__ is found in the filenamee
    e.g. case_bwa\reporting_setup_and_settings_BWA.xlsm
    """
    filenames = os.listdir(folder_path)
    filenames = [f for f in filenames if "xlsm" in f]
    filenames = [f for f in filenames if "_setup_" in f]
    if filenames:
        selected_filename = show_context.selectbox("Select settings file", filenames)
        return os.path.join(folder_path, selected_filename)
    else:
        show_context.write("No Excel settings file in directory")
        return []


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
    from version import __version__
    return __version__


def get_current_git_branch():
    try:
        result = subprocess.check_output(["git", "branch", "--show-current"])
        return result.decode("utf-8").strip()
    except:
        return "Error getting git branch"


def package_version(sidebar=True):
    __version__ = get_package_version()
    st.sidebar.write(f":green[Application version :  {__version__}]")
    from pypsa import __version__ as pypsa_version
    st.sidebar.write(f":green[PyPSA version      :  {pypsa_version}]")
    git_branch = get_current_git_branch()

    if git_branch == 'dev':
        st.sidebar.write(f":red[Git branch          : {get_current_git_branch()}]")
    else:
        st.sidebar.write(f":green[Git branch        : {get_current_git_branch()}]")



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
            st.rerun()
    else:
        if st.button("Refresh"):
            st.rerun()


def apply_cell_colors(s):
    return ["background-color: %s" % color for color in s]


def find_files_containing_string(path, target_string):
    matching_filenames = (
        []
    )  # List to hold names of files containing the target string in their name
    for root, dirs, files in os.walk(path):
        for file in files:
            if target_string in file:
                matching_filenames.append(
                    file
                )  # Append the filename (not path) that contains the target string
    return matching_filenames


import os

import os


def list_directories_containing_results(input_path):
    """
    List all directories within the given input path that contain the string "Results_" in their name.

    :param input_path: Path to search for directories.
    :return: A list of directory names that contain the string "Results_".
    """
    directories_with_results = []
    # Ensure the input path is absolute
    input_path = os.path.abspath(input_path)

    # Check if the input path exists and is a directory
    if not os.path.exists(input_path) or not os.path.isdir(input_path):
        print(f"The path {input_path} does not exist or is not a directory.")
        return directories_with_results

    try:
        # List all entries in the given path
        for entry in os.listdir(input_path):
            full_path = os.path.join(input_path, entry)
            # Check if the entry is a directory and contains the string "Results_"
            if os.path.isdir(full_path) and "Results_" in entry:
                directories_with_results.append(entry)  # Append only the directory name
    except Exception as e:
        print(f"An error occurred: {e}")

    return directories_with_results


def clip(filepath, clip_type=win32clipboard.CF_DIB):
    if st.button(":scissors:", key=filepath):
        image = Image.open(filepath)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()
        st.info(f"Sent to clipboard", icon="✂️")
