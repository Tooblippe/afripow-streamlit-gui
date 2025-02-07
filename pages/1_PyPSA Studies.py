import os
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

from pages.helpers.excess_energy_optimisation import (
    excess_energy_optimisation,
    fetch_excess_energy_parameters,
)

# sys.path.insert(0, "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src", )

from afripow_pypsa.toolbox.toolbox import (
    run_incremental_demand_expansion,
    run_unconstrained_expansion,
    run_optimum_expansion,
    silence_warnings,
    set_cplex_licence_key,
)

from afripow_pypsa.helpers.direcory_cases import find_int_named_subdirs

from pages.helpers.helpers import (
    open_location,
    package_version,
    select_folder,
    refresh_button,
    page_setup,
    list_directories_with_paths,
    file_selector,
    get_startup_directory,
)
from pages.helpers.study_types import STUDY_TYPES

page_setup(page_name="PyPSA Studies")

silence_warnings()
set_cplex_licence_key()


st_container = st.sidebar.container(border=True)

# manage state
if "folder_path" not in st.session_state:
    st.session_state.folder_path = os.getcwd()

# handle study directory selection
selected_folder_path = st.session_state.get("folder_path", None)
folder_select_button = st_container.button(
    "Select project folder", use_container_width=True, type="primary"
)
# TODO - remove the actualy directory below and make a variable
if folder_select_button:
    BASE_DIR = select_folder(start_directory=get_startup_directory())
    st.session_state.folder_path = BASE_DIR
BASE_DIR = st.session_state.folder_path
st_container.text(BASE_DIR)

# handle the case directory
input_dirs = list_directories_with_paths(Path(BASE_DIR))
start_dir = st_container.selectbox(
    "Select case",
    input_dirs.keys(),
)

# study type selection [unconstrained, opt, opt etc]
study_type = st_container.selectbox("Select study type", STUDY_TYPES.keys())

# process inputs and show available years in case folder
years_in_directory = find_int_named_subdirs(Path(BASE_DIR) / start_dir)

years = st_container.multiselect(
    f"Study years found in {start_dir}",
    years_in_directory,
    placeholder="Select years",
    default=years_in_directory,
)

# refresh button


# Main screen
st.write(f"## {study_type}")

BASE_DIR = st.session_state.folder_path
load_from_dir = STUDY_TYPES[study_type]["input"]
save_to_dir = STUDY_TYPES[study_type]["output"]
doc = STUDY_TYPES[study_type]["doc"]
solver_function = STUDY_TYPES[study_type]["function"]

setttings_file = None
# Table summary
if study_type != "4. Excess Energy Optimisation":
    st.table(
        pd.DataFrame(
            [doc, BASE_DIR, start_dir, load_from_dir, save_to_dir, years],
            columns=["Value"],
            index=[
                "Study description",
                "Study base directory",
                "Selected Case",
                f"Case input directory [load from]",
                "Results output directory [write to]",
                "Selected Solver Years",
            ],
        )
    )
else:
    setttings_file = file_selector(Path(BASE_DIR), st)
    if setttings_file:
        excess_params = fetch_excess_energy_parameters(setttings_file)
        st.table(
            pd.DataFrame(
                [
                    doc,
                    BASE_DIR,
                    start_dir,
                    load_from_dir,
                    save_to_dir,
                    setttings_file,
                    years,
                    excess_params["excess_generator"],
                    excess_params["excess_energy_link_name"],
                    excess_params["excess_energy_link_pnom_max"],
                    excess_params["excess_energy_prices"],
                ],
                columns=["Value"],
                index=[
                    "Study description",
                    "Study base directory",
                    "Selected Case",
                    f"Case input directory [load from]",
                    "Results output directory [write to]",
                    "Setting file",
                    "Selected Solver Years",
                    "Excess Energy - Generator",
                    "Excess Energy - Link",
                    "Excess Energy - Link - pnom_max",
                    "Excess Energy - Prices",
                ],
            )
        )

# open case folder
if st.button("Open Case Directory", type="primary"):
    open_location(Path(BASE_DIR) / start_dir)

# run button
refresh_button()
v = "Run Study" if len(years) > 0 else "Select years to enable Run button"
run_button = st.sidebar.button(
    v, type="primary", disabled=len(years) == 0, use_container_width=True
)
if run_button:
    with st.spinner("Report is running. Output in terminal window."):
        f = STUDY_TYPES[study_type]["function"]
        f(
            BASE_DIR / Path(start_dir),
            [str(y) for y in years],
            load_from_dir,
            save_to_dir,
        )  # st.rerun()

package_version()

if __name__ == "__main__":
    print("..")
