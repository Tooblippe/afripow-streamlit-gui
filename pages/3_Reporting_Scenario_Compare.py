from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from afripow_pypsa.lib.capacity_plan_plot import remove_missing_links

from afripow_pypsa.Report.Report import Report

from afripow_pypsa.helpers.plot_order_colours import get_plot_order_colours

from afripow_pypsa.lib.stacked_bar_graph import study_stacked_bar_graph

from afripow_pypsa.lib.settings import global_figsize
from matplotlib import pyplot as plt

from afripow_pypsa.helpers.own_types import FigAxDF

from pages.helpers.helpers import select_folder, list_directories_with_paths, file_selector
from pages.helpers.study_types import STUDY_TYPES

st.set_page_config(layout="wide")

def generate_scanario_comparison_plot(
        case_name : str,                       # S1_No_MHPP
        base_directory : Path,                  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv')
        path_to_excel_settings : Path,          # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv\Reporting_setup_MPA_v3.0.xlsm')
        input_dir : Path|str,                   # Results_opt
        left_csv_file: Path,                    #
        right_csv_file: Path,                   #
        left_name: str,                         #
        right_name: str,
        title_prefix :str,
        y_label : str,
        ) -> FigAxDF:            #


    fig, ax = plt.subplots(figsize=global_figsize)

    r = Report(
        case_name=case_name,
        base_directory=base_directory,
        path_to_excel_settings=path_to_excel_settings,
        input_dir=input_dir,  # e.h. path to "Input_uc"
        create_output_directories=False
    )

    plot_order, colors_list = get_plot_order_colours(r.settings)

    try:
        left_df = pd.read_csv(left_csv_file, header=0, index_col='plant_group').transpose().sort_index()
    except FileNotFoundError:
        left_df = pd.DataFrame()

    try:
        right_df = pd.read_csv(right_csv_file, header=0, index_col='plant_group').transpose().sort_index()
    except FileNotFoundError:
        right_df = pd.DataFrame()

    sub_df = left_df.sub(right_df, fill_value=0)
    sub_df = sub_df[plot_order]
    plot_order, colors_list = remove_missing_links(
        sub_df, plot_order, colors_list, debug=False
    )

    sub_df.plot(
        ax=ax,
        kind="bar",
        color=colors_list,
        stacked=True,
    )

    # st.write(sub_df)

    study_stacked_bar_graph(
        fig, ax, f"{title_prefix} {left_name} vs {right_name}", y_label
    )

    # set max and steps
    max_val = ceil(sub_df[sub_df>0].sum(axis=1).max())
    min_val = ceil(sub_df[sub_df<0].sum(axis=1).min())
    step = round((max_val-min_val) / 5, -2)
    ytics_list = np.arange(min_val - step, max_val + step, step)
    ytics_list = [round(value/step) * step for value in ytics_list]
    plt.yticks(ytics_list)

    # 0 line
    ax.axhline(0, color='black', linewidth=1, zorder=1, )

    return fig, ax, sub_df


st_container = st.sidebar.container(border=True)

# Initial variables
base_dir = Path(r"C:\Users\apvse\PyPSA_csv\2407_MPA_csv")
report_base = r'reporting_outputs_'
capacity_data_file = 'capacity_plot_table.csv'
energy_data_file = 'energy_plot_table.csv'
output_folder_name = "scenario_compare"

# Select the base project folder
folder_select_button = st_container.button("Select folder containing cases", use_container_width=True, type="primary")
if folder_select_button:
    base_dir = Path(select_folder(start_directory=base_dir))

st_container.write(base_dir)

# handle the case directory
input_dirs = list_directories_with_paths(Path(base_dir))
left_dir = st_container.selectbox("Select left case", input_dirs.keys(), key="left_dir")
right_dir = st_container.selectbox("Select right case", input_dirs.keys(), key="right_dir")
excel_file = file_selector(Path(base_dir), st_container)
# study type selection [unconstrained, opt, opt etc]
study_type =  st_container.selectbox("Select study type", STUDY_TYPES.keys())
type_report_file_csv = st_container.selectbox("Energy Capacity", ['capacity_plot_table.csv', 'energy_plot_table.csv'])

st.markdown(f"## Scenario Capacity and Energy Comparison")
st.markdown(f"### {left_dir} vs. {right_dir}")



input_reporting_dir_left = base_dir / left_dir / (report_base + STUDY_TYPES[study_type]['output'])
input_reporting_dir_right = base_dir / right_dir / (report_base + STUDY_TYPES[study_type]['output'])



# -------------------
left_file_capacity =  input_reporting_dir_left / "capacity_plot_table.csv"
right_file_capacity = input_reporting_dir_right / "capacity_plot_table.csv"

left_file_energy =  input_reporting_dir_left / "energy_plot_table.csv"
right_file_energy = input_reporting_dir_right / "energy_plot_table.csv"

try:
    left_df = pd.read_csv(left_file_capacity, header=0, index_col='plant_group').transpose().sort_index()
except FileNotFoundError:
    st.write(f"left file {left_file_capacity} not found")
    left_df = pd.DataFrame()

try:
    right_df = pd.read_csv(right_file_capacity, header=0, index_col='plant_group').transpose().sort_index()
except FileNotFoundError:
    st.write(f"right file {right_file_capacity} not found")
    right_df = pd.DataFrame()


mw_mwh = "MW" if "capacity" in type_report_file_csv else "MWh"

if not left_df.empty and not right_df.empty:
    # drop columns for testing
    scenario_compare_plot_capacity =  generate_scanario_comparison_plot(
        left_dir,
        base_dir,
        excel_file,
        STUDY_TYPES[study_type]['output'],
        left_file_capacity,
        right_file_capacity,
        left_dir,
        right_dir,
        "Capacity Diff:",
        "MW"
        )

    scenario_compare_plot_energy = generate_scanario_comparison_plot(
        left_dir,
        base_dir,
        excel_file,
        STUDY_TYPES[study_type]['output'],
        left_file_energy,
        right_file_energy,
        left_dir,
        right_dir,
        "Energy Diff:",
        "MWh"
    )

    capacity_column, energy_column, = st.columns(2)
    with capacity_column:
        st.pyplot(
           scenario_compare_plot_capacity[0], use_container_width=True)
        sub_df = left_df.sub(right_df, fill_value=0)

        st.markdown(f"## Scenario comparison results data: ({mw_mwh})")
        st.write(sub_df)
        # st.write(left_df.sub(right_df, fill_value=0))
        st.markdown(f"## {left_dir} (left)")
        st.bar_chart(left_df)
        st.write(left_df)
        st.markdown(f"## {right_dir} (right)")
        st.bar_chart(right_df)
        st.write(right_df)

    with energy_column:
        st.pyplot(
           scenario_compare_plot_energy[0], use_container_width=True)

    # st.write(left_df)
    # st.write(right_df)


else:
    st.markdown(f"### Selections not valid : check study type:  *{STUDY_TYPES[study_type]['output']}*")
    st.markdown(
        f"### Selections not valid : check if the {left_dir} and {right_dir} have been solved and reporting run")

if left_dir == right_dir:
    st.markdown("### The two selected cases are the same")
