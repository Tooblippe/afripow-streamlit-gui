import os
import sys
from pathlib import Path

sys.path.insert(
    0,
    "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src",
)


import pandas as pd
import streamlit as st
from PIL import Image


from afripow_pypsa.helpers.direcory_cases import find_int_named_subdirs

from afripow_pypsa.toolbox.toolbox import (
    generate_case_report,
    silence_warnings,
    set_cplex_licence_key,
)
from streamlit_extras.stylable_container import stylable_container


from pages.helpers.helpers import (open_location, package_version, select_folder, refresh_button, page_setup,
                                   list_directories_with_paths, find_all_images, apply_cell_colors, clip,
                                   find_files_containing_string, list_directories_containing_results, )



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
        clip(Path(image_path))
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, ldc, dispatch = st.tabs(
        [
            "study_years",
            "links_to_plant",
            "plant_group",
            "Capacity Plot",
            "Energy Plot",
            "LF Plot",
            "Links Plot",
            "MPDC Plot",
            'Dispatch'
        ]
    )
    with tab2:
        df = load_file(excel_file, "link_to_plant")
        styled_df = df.style.apply(apply_cell_colors, subset=["plot_color"], axis=1)
        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
    with tab3:
        df = load_file(excel_file, "plant_group")
        styled_df = df.style.apply(apply_cell_colors, subset=["plot_color"], axis=1)
        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
    with tab1:
        data = load_file(excel_file, "study_years")
        data.set_index("years", inplace=True)
        st.bar_chart(data)
    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            image_path = results_folder / "capacity_plot.png"
            show_image(image_path)

            image_path = results_folder / "capacity_plot_table.png"
            show_image(image_path)
        with c2:
            show_image(results_folder / 'capacity_delta_plot.png')

    with tab5:
        c1, c2 = st.columns(2)
        with c1:
            image_path = results_folder / "energy_plot.png"
            show_image(image_path)
            image_path = results_folder / "energy_plot_table.png"
            show_image(image_path)
        with c2:
            show_image(results_folder / "energy_delta_plot.png")
    with tab6:
        image_path = results_folder / "load_factor_plot_table.png"
        show_image(image_path)
    with tab7:
        links_plot_insert(results_folder)
    with ldc:

        ldc_imgs = find_files_containing_string(results_folder/"marginal_price", "_marginal_price_durtion_curve.png" )

        for ldc in ldc_imgs:
            image_path = results_folder / "marginal_price" /ldc
            show_image(image_path)
    with dispatch:

        ldc_imgs = find_files_containing_string(results_folder/"average_dispatch", "average_dispatch_" )

        for ldc in ldc_imgs:
            image_path = results_folder / "average_dispatch" / ldc
            show_image(image_path)

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



    excel_file_df = load_file(excel_file, "study_years")

    study_years = excel_file_df.loc[excel_file_df.select == 1].years.to_list()

    study_type = ct.selectbox("Select input folder",
            list_directories_containing_results(Path(base_dir) / Path(start_dir) / str(study_years[0])))

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
                open_location(Path(base_dir))
            if st.button(
                ":white[Results dir]", use_container_width=True, type="primary"
            ):
                open_location(results_folder)
            link_plot_color = st.text_input("Link plot color", "#4472C4")
            currency = st.selectbox("Unit", ["$/MWh", "R/MWh"])

    base_dir = st.session_state.folder_path

    # Input summary

    with st.container(border=True):
        excel_tabs(results_folder)

    refresh_button()



    with stylable_container(
        key="terminal",
        css_styles="""
                {
                  background-color: black;
                  color: #33FF33; /* Classic green terminal color */
                  font-family: 'Courier New', Courier, monospace; /* Monospaced font for that classic terminal look */
                  padding: 20px;
                  max-height: 800px; /* Maximum height */
                  overflow-y: auto; /* Enable vertical scrolling if the co
                }
                """,
    ):
        run_capacity_energy = st.sidebar.button(
            ":white[Generate Capacity/Energy Plots]",
            type="primary",
            use_container_width=True,
        )
        run_links = st.sidebar.button(
            ":white[Generate Link Profiles Plots]",
            type="primary",
            use_container_width=True,
        )
        run_all = st.sidebar.button(
            ":white[Generate All Plots]", type="primary", use_container_width=True
        )

        if run_capacity_energy:
            with st.spinner("Report is running. Output in terminal window."):
                generate_case_report(
                    start_dir,
                    excel_file,
                    Path(base_dir) / Path(start_dir),
                    study_type,
                    reports_to_run=["CAPACITY_ENERGY"], link_plot_color=link_plot_color,
                    currency_str = currency
                )
                st.toast(":green[Reporting done]")
                st.experimental_rerun()

        if run_links:
            with st.spinner("Report is running. Output in terminal window."):
                generate_case_report(
                    start_dir,
                    excel_file,
                    Path(base_dir) / Path(start_dir),
                    study_type,
                    reports_to_run=["LINK_PROFILES"],link_plot_color=link_plot_color),
                currency_str = currency

                st.toast(":green[Reporting done]")

        if run_all:
            with st.spinner("Report is running. Output in terminal window."):
                st.write("start_dir", start_dir)
                st.write("excel_file", excel_file)
                st.write(Path(base_dir) / Path(start_dir))
                st.write(study_type)

                generate_case_report(
                    start_dir,
                    excel_file,
                    Path(base_dir) / Path(start_dir),
                    study_type,
                    reports_to_run=["ALL"],link_plot_color=link_plot_color, currency_str=currency
                )
                st.toast(":green[Reporting done]")

else:
    st.write("No valid Excel file selected")

package_version()
