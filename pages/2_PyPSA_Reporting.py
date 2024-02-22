import os
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from afripow_pypsa.toolbox.toolbox import (
    generate_case_report,
    silence_warnings,
    set_cplex_licence_key,
)

#
# from ultraimport import ultraimport
#
# helpers_dir = "__dir__/helpers/helpers.py"
# find_int_named_subdirs = ultraimport(helpers_dir, "find_int_named_subdirs")
# open_location = ultraimport(helpers_dir, "open_location")
# package_version = ultraimport(helpers_dir, "package_version")
# select_folder = ultraimport(helpers_dir, "select_folder")
# refresh_button = ultraimport(helpers_dir, "refresh_button")
# page_setup = ultraimport(helpers_dir, "page_setup")
# list_directories_with_paths = ultraimport(helpers_dir, "list_directories_with_paths")


from pages.helpers.helpers import (
    open_location,
    package_version,
    select_folder,
    refresh_button,
    page_setup,
    list_directories_with_paths,
    find_all_images,
    find_int_named_subdirs,
)


page_setup(page_name="PyPSA Reporting")
silence_warnings()
set_cplex_licence_key()


def load_file(filename, sheet_name):
    """Loads a Excel file with pandas and turn the sheet into a dataframe"""
    df = pd.read_excel(filename, sheet_name=sheet_name)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    return df


def file_selector(folder_path, show_context):
    """Produces a file selector of all files meeting the criteria:
    ext = "xlsm" and
    __setup__ is found in the filename
    e.g. case_bwa\reporting_setup_and_settings_BWA.xlsm
    """
    filenames = os.listdir(folder_path)
    filenames = [f for f in filenames if "xlsm" in f]
    filenames = [f for f in filenames if "_setup_" in f]
    if filenames:
        selected_filename = show_context.selectbox("Select a file", filenames)
        return os.path.join(folder_path, selected_filename)
    else:
        show_context.write("No Excel settings file in directory")
        return []


def show_image(image_path):
    try:
        image = Image.open(image_path)
        st.image(image)
    except:
        st.write("Not found")


def links_plot_insert(results_folder):
    year = str(st.selectbox("Select year", find_int_named_subdirs(results_folder)))

    all_images = find_all_images(results_folder / Path(year))
    images = list(all_images.keys())

    for a, b, c in zip(images[::3], images[1::3], images[2::3]):
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text(a)
                show_image(all_images[a])
            with c2:
                st.text(b)
                show_image(all_images[b])
            with c3:
                st.text(c)
                show_image(all_images[c])


def excel_tabs(results_folder: Path):
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "study_years",
            "links_to_plant",
            "plant_group",
            "Capacity Plot",
            "Energy Plot",
            "LF Plot",
            "Links",
        ]
    )
    with tab2:
        st.data_editor(load_file(excel_file, "link_to_plant"))
    with tab3:
        st.data_editor(load_file(excel_file, "plant_group"))
    with tab1:
        data = load_file(excel_file, "study_years")
        data.set_index("years", inplace=True)
        st.bar_chart(data)
    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            image_path = results_folder / "capacity_plot.png"
            show_image(image_path)
        with c2:
            image_path = results_folder / "capacity_plot_table.png"
            show_image(image_path)
    with tab5:
        c1, c2 = st.columns(2)
        with c1:
            image_path = results_folder / "energy_plot.png"
            show_image(image_path)
        with c2:
            image_path = results_folder / "energy_plot_table.png"
            show_image(image_path)
    with tab6:
        image_path = results_folder / "load_factor_plot_table.png"
        show_image(image_path)
    with tab7:
        links_plot_insert(results_folder)


# set up sidebar
ct = st.sidebar.container(border=True)

if "folder_path" not in st.session_state:
    st.session_state["folder_path"] = os.getcwd()

folder_select_button = ct.button("Select Project Folder", use_container_width=True)
if folder_select_button:
    base_dir = select_folder()
    st.session_state.folder_path = base_dir
base_dir = st.session_state.folder_path


# Case selection
input_dirs = list_directories_with_paths(Path(base_dir))
start_dir = ct.selectbox(
    "Select case", [d for d in input_dirs.keys() if "__pycache__" not in d]
)

# Search for Excel file file
excel_file = file_selector(Path(base_dir), ct)

study_type = None
study_years = []
results_folder = None
if excel_file:
    study_type = ct.selectbox(
        "Select input folder", ["Results_uc", "Results_opt", "Results_opti"]
    )

    excel_file_df = load_file(excel_file, "study_years")

    study_years = excel_file_df.loc[excel_file_df.select == 1].years.to_list()

st.write(f"## PyPSA report generation")


if study_type:
    results_folder = (
        Path(base_dir) / Path(start_dir) / Path("reporting_outputs_" + study_type)
    )

if excel_file:
    C1, C2, *_ = st.columns([9, 2])
    with C1:
        with st.container(border=True):
            st.table(
                data={
                    "Project Directory": Path(base_dir),
                    "Path to case": Path(base_dir) / Path(start_dir),
                    "Path to Excel file": excel_file,
                    "Study Years Selected In Excel File": str(study_years),
                    "Inputs directory (load from)": study_type,
                    "Results folder (write to)": results_folder,
                },
            )
    with C2:
        with st.container(border=True):
            if st.button(
                ":white[Settings file]", use_container_width=True, type="primary"
            ):
                open_location(excel_file)
            if st.button(":white[Base dir]", use_container_width=True, type="primary"):
                open_location(base_dir)
            if st.button(
                ":white[Results dir]", use_container_width=True, type="primary"
            ):
                open_location(results_folder)

    base_dir = st.session_state.folder_path

    # Input summary

    with st.container(border=True):
        excel_tabs(results_folder)

    refresh_button()
    run_button = st.sidebar.button(
        ":white[Run Report]", type="primary", use_container_width=True
    )
    if run_button:
        with st.spinner("Report is running. Output in terminal window."):
            st.toast(":green[Reporting started...]")
            generate_case_report(
                start_dir, excel_file, Path(base_dir) / Path(start_dir), study_type
            )
            st.toast(":green[Reporting done]")
            st.experimental_rerun()



else:
    st.write("No valid Excel file selected")

package_version()
