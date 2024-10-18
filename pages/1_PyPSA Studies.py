import os
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

from pages.helpers.excess_energy_optimisation import (excess_energy_optimisation, fetch_excess_energy_parameters, )

sys.path.insert(0, "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src", )

from afripow_pypsa.toolbox.toolbox import (run_incremental_demand_expansion, run_unconstrained_expansion,
                                           run_optimum_expansion, silence_warnings, set_cplex_licence_key, )

from afripow_pypsa.helpers.direcory_cases import find_int_named_subdirs

from pages.helpers.helpers import (open_location, package_version, select_folder, refresh_button, page_setup,
                                   list_directories_with_paths, file_selector, )

page_setup(page_name="PyPSA Studies")

silence_warnings()
set_cplex_licence_key()

STUDY_TYPES = {"1. Unconstrained Expansion"     : {"input"   : "Inputs", "output": "Results_uc",
                                                   "function": run_unconstrained_expansion,
                                                   "doc"     : "1) Adding Hydro Efficiency, 2) Fix Battery Capacity, 3) Add reserve constraints", },
               "2. Optimum Expansion"           : {"input"   : "Results_uc", "output": "Results_opt",
                                                   "function": run_optimum_expansion, "doc": "Add docs", },
               "3. Incremental Demand Expansion": {"input"   : "Results_opt", "output": "Results_opti",
                                                   "function": run_incremental_demand_expansion, "doc": "Add docs", },
               # "4. Excess Energy Optimisation": {
               #     "input": "Results_opt",
               #     "output": "Results_opti",
               #     "function": excess_energy_optimisation,
               #     "doc": "Optimise Excess Energy",
               # },
               }

st_container = st.sidebar.container(border=True)

# manage state
if "folder_path" not in st.session_state:
    st.session_state.folder_path = os.getcwd()

# handle study directory selection
selected_folder_path = st.session_state.get("folder_path", None)
folder_select_button = st_container.button("Select folder containing cases", use_container_width=True, type="primary")
if folder_select_button:
    base_dir = select_folder()
    st.session_state.folder_path = base_dir
base_dir = st.session_state.folder_path
st_container.text(base_dir)

# handle the case directory
input_dirs = list_directories_with_paths(Path(base_dir))
start_dir = st_container.selectbox("Select case", input_dirs.keys(), )

# study type selection [unconstrained, opt, opt etc]
study_type = st_container.selectbox("Select study type", STUDY_TYPES.keys())

# process inputs and show available years in case folder
years_in_directory = find_int_named_subdirs(Path(base_dir) / start_dir)

years = st_container.multiselect(f"Study years found in {start_dir}", years_in_directory, placeholder="Select years",
                                 default=years_in_directory, )

# refresh button


# Main screen
st.write(f"## {study_type}")

base_dir = st.session_state.folder_path
load_from_dir = STUDY_TYPES[study_type]["input"]
save_to_dir = STUDY_TYPES[study_type]["output"]
doc = STUDY_TYPES[study_type]["doc"]
solver_function = STUDY_TYPES[study_type]["function"]

setttings_file = None
# Table summary
if study_type != "4. Excess Energy Optimisation":
    st.table(pd.DataFrame([doc, base_dir, start_dir, load_from_dir, save_to_dir, years], columns=["Value"],
                          index=["Study description", "Study base directory", "Selected Case",
                                 f"Case input directory [load from]", "Results output directory [write to]",
                                 "Selected Solver Years", ], ))
else:
    setttings_file = file_selector(Path(base_dir), st)
    if setttings_file:
        excess_params = fetch_excess_energy_parameters(setttings_file)
        st.table(pd.DataFrame([doc, base_dir, start_dir, load_from_dir, save_to_dir, setttings_file, years,
                               excess_params["excess_generator"], excess_params["excess_energy_link_name"],
                               excess_params["excess_energy_link_pnom_max"], excess_params["excess_energy_prices"], ],
                              columns=["Value"], index=["Study description", "Study base directory", "Selected Case",
                                                        f"Case input directory [load from]",
                                                        "Results output directory [write to]", "Setting file",
                                                        "Selected Solver Years", "Excess Energy - Generator",
                                                        "Excess Energy - Link", "Excess Energy - Link - pnom_max",
                                                        "Excess Energy - Prices", ], ))

# open case folder
if st.button("Open Case Directory", type="primary"):
    open_location(Path(base_dir) / start_dir)

# run button
refresh_button()
v = "Run Study" if len(years) > 0 else "Select years to enable Run button"
run_button = st.sidebar.button(v, type="primary", disabled=len(years) == 0, use_container_width=True)
if run_button:
    with st.spinner("Report is running. Output in terminal window."):
        f = STUDY_TYPES[study_type]["function"]
        f(base_dir / Path(start_dir), [str(y) for y in years], load_from_dir, save_to_dir,
          )  # st.rerun()

package_version()

if __name__ == "__main__":
    print("..")
