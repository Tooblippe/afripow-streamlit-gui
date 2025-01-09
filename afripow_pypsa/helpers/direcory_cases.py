# directory cases

import os
import re
from pathlib import Path


def find_input_directories(base_directory, input_dir):
    print(f"[ INFO ] - Loading from base directory: {base_directory}")
    print(f"[ INFO ] - Searching in output directories: {input_dir}")
    input_directories = {}
    # Get immediate subdirectories of the base directory
    for subdir in os.listdir(base_directory):
        full_subdir_path = os.path.join(base_directory, subdir)

        if bool(re.match(r"^[0-9]+$", subdir)):  # is this a year directory
            # Ensure that the path is a directory (not a file)
            if os.path.isdir(full_subdir_path):
                input_directories[subdir] = {}  # e.g set Base-31 Mai

                # Walk through all directories starting from the subdirectory
                for root, dirs, files in os.walk(full_subdir_path):
                    for dir in dirs:
                        if dir == input_dir:
                            print(input_dir)
                            print(
                                f"[ INFO ] - Found study network directory {root}\{dir}"
                            )
                            # Append the full path to the "Inputs" directory
                            # to the list associated with the current subdirectory
                            if dir == input_dir:
                                path = Path(os.path.join(root, dir))
                                year = int(path.parts[-2])
                                # input_directories[subdir].append(os.path.join(root, dir))  # add fullt path
                                input_directories[subdir][year] = path  # add fullt path
                            else:
                                print(f"[ INFO ] - Disgarding {dir}")

    return input_directories


def remove_non_directory_files(directory):
    if os.path.isdir(directory):  # Check if the directory exists
        print(f"Removing files from {directory}")
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                try:
                    os.remove(item_path)
                    print(f"Deleted file: {item_path}")
                except Exception as e:
                    print(f"Failed to delete {item_path}. Reason: {e}")
    else:
        print(f"The directory {directory} does not exist")
        os.makedirs(directory)
        print(f"Directory {directory} created")


# def find_int_named_subdirs(path):
#     """
#     Finds all subdirectories within the given path whose names can be cast to an integer.
#
#     :param path: The path to search within.
#     :return: A list of subdirectory names (as integers) that can be cast to an integer.
#     """
#     int_named_subdirs = []
#
#     # Walk through the directory structure starting at the given path
#     for root, dirs, _ in os.walk(path):
#         # Check each directory in dirs for subdirectories that can be cast to an integer
#         for dir_name in dirs:
#             if (
#                 dir_name.isdigit()
#             ):  # Check if the directory name can be cast to an integer
#                 full_dir_path = os.path.join(root, dir_name)
#                 # Add the directory name (as integer) to the list
#                 int_named_subdirs.append(int(dir_name))
#
#     return int_named_subdirs
def find_int_named_subdirs(path):
    """
    Finds all subdirectories within the given path whose names can be cast to an integer,
    but only at the first level of the directory.

    :param path: The path to search within.
    :return: A list of subdirectory names (as integers) that can be cast to an integer.
    """
    int_named_subdirs = []

    # List the directories in the given path (only first-level subdirectories)
    for dir_name in os.listdir(path):
        full_dir_path = os.path.join(path, dir_name)
        if (
            os.path.isdir(full_dir_path) and dir_name.isdigit()
        ):  # Check if it's a directory and can be cast to an integer
            int_named_subdirs.append(int(dir_name))

    return int_named_subdirs
