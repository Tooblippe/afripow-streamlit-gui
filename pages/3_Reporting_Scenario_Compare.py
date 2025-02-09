import os
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

from pages.helpers.helpers import (
    select_folder,
    list_directories_with_paths,
    file_selector,
    clip,
    find_files_containing_string,
    get_startup_directory,
    base_directory_input,
    case_directory_input,
    study_type_input,
)
from pages.helpers.study_types import STUDY_TYPES

st.set_page_config(layout="wide")

# Initial variables
# BASE_DIR = Path(r"C:\Users\apvse\PyPSA_csv\2407_MPA_csv")
report_base = r"reporting_outputs_"
capacity_data_file = "capacity_plot_table.csv"
energy_data_file = "energy_plot_table.csv"
output_folder_name = "scenario_compare"


def generate_scanario_comparison_plot(
    case_name: str,  # S1_No_MHPP
    base_directory: Path,  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv')
    path_to_excel_settings: Path,
    # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv\Reporting_setup_MPA_v3.0.xlsm')
    input_dir: Path | str,  # Results_opt
    left_csv_file: Path,  #
    right_csv_file: Path,  #
    left_name: str,  #
    right_name: str,
    title_prefix: str,
    y_label: str,
) -> FigAxDF:  #

    fig, ax = plt.subplots(figsize=global_figsize)

    r = Report(
        case_name=case_name,
        base_directory=base_directory,
        path_to_excel_settings=path_to_excel_settings,
        input_dir=input_dir,  # e.h. path to "Input_uc"
        create_output_directories=False,
    )

    plot_order, colors_list = get_plot_order_colours(r.settings)

    try:
        left_df = (
            pd.read_csv(left_csv_file, header=0, index_col="plant_group")
            .transpose()
            .sort_index()
        )
    except FileNotFoundError:
        left_df = pd.DataFrame()

    try:
        right_df = (
            pd.read_csv(right_csv_file, header=0, index_col="plant_group")
            .transpose()
            .sort_index()
        )
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
    max_val = ceil(sub_df[sub_df > 0].sum(axis=1).max())
    min_val = ceil(sub_df[sub_df < 0].sum(axis=1).min())
    step = round((max_val - min_val) / 5, -2)
    ytics_list = np.arange(min_val - step, max_val + step, step)
    ytics_list = [round(value / step) * step for value in ytics_list]
    plt.yticks(ytics_list)

    # 0 line
    ax.axhline(
        0,
        color="black",
        linewidth=1,
        zorder=1,
    )

    return fig, ax, sub_df


def show_scanario_comparison_plot(
    case_name: str,  # S1_No_MHPP
    base_directory: Path,  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv')
    path_to_excel_settings: Path,
    # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv\Reporting_setup_MPA_v3.0.xlsm')
    input_dir: Path | str,  # Results_opt
    left_csv_file: Path,  #
    right_csv_file: Path,  #
    left_name: str,  #
    right_name: str,
    title_prefix: str,
    y_label: str,
):
    #
    fig, ax, df = generate_scanario_comparison_plot(
        case_name,  # S1_No_MHPP
        base_directory,  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv')
        path_to_excel_settings,
        # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv\Reporting_setup_MPA_v3.0.xlsm')
        input_dir,  # Results_opt
        left_csv_file,  #
        right_csv_file,  #
        left_name,  #
        right_name,
        title_prefix,
        y_label,
    )

    path_to_images_save = (
        base_directory
        / case_name
        / f"reporting_outputs_{input_dir}"
        / output_folder_name
    )

    if not os.path.exists(path_to_images_save):
        # Create the directory
        os.makedirs(path_to_images_save)

    image_type = "capacity" if y_label == "MW" else "energy__"

    fig_name = (
        path_to_images_save
        / f"scenario_compare_{image_type}_{case_name}_{input_dir}_to_{left_name}_{right_name}.png"
    )
    csv_file = (
        path_to_images_save
        / f"scenario_compare_{image_type}_{case_name}_{input_dir}_to_{left_name}_{right_name}.csv"
    )

    fig.savefig(fig_name)
    df.to_csv(csv_file)
    return (
        fig_name,
        csv_file,
        path_to_images_save,
        fig,
        ax,
        df,
    )  # returns paths to figure, csv, the fig obj, axes obj and the resultant df


st_container = st.sidebar.container(border=True)


BASE_DIR = base_directory_input(st_container)

# handle the case directory
input_dirs = list_directories_with_paths(Path(BASE_DIR)).keys()
input_dirs = [k for k in input_dirs if "report" not in k]
study_type = study_type_input(st_container)

left_dir = st_container.selectbox(
    "Select left case", input_dirs, key="left_dir", index=None
)
right_dir = st_container.selectbox(
    "Select right case", input_dirs, key="right_dir", index=None
)


excel_file = file_selector(Path(BASE_DIR), st_container, setting_key="excel_file")

st.markdown(f"## Scenario Capacity and Energy Comparison")
st.markdown(f"### {left_dir or 'Select left'} vs. {right_dir or 'Select right'}")

if left_dir:
    input_reporting_dir_left = (
        BASE_DIR / left_dir / (report_base + STUDY_TYPES[study_type]["output"])
    )
    left_file_capacity = input_reporting_dir_left / "capacity_plot_table.csv"
    left_file_energy = input_reporting_dir_left / "energy_plot_table.csv"

if right_dir:
    input_reporting_dir_right = (
        BASE_DIR / right_dir / (report_base + STUDY_TYPES[study_type]["output"])
    )
    right_file_capacity = input_reporting_dir_right / "capacity_plot_table.csv"
    right_file_energy = input_reporting_dir_right / "energy_plot_table.csv"

if left_dir and right_dir:
    scenario_compare_plot_capacity = show_scanario_comparison_plot(
        left_dir,
        BASE_DIR,
        excel_file,
        STUDY_TYPES[study_type]["output"],
        left_file_capacity,
        right_file_capacity,
        left_dir,
        right_dir,
        "Capacity Diff:",
        "MW",
    )

    scenario_compare_plot_energy = show_scanario_comparison_plot(
        left_dir,
        BASE_DIR,
        excel_file,
        STUDY_TYPES[study_type]["output"],
        left_file_energy,
        right_file_energy,
        left_dir,
        right_dir,
        "Energy Diff:",
        "MWh",
    )

    if (
        not scenario_compare_plot_capacity[-1].empty
        and not scenario_compare_plot_energy[-1].empty
    ):
        latest, existing = st.tabs(
            ["Current comparison", f"Existing comparisons with {left_dir}"]
        )
        with latest:
            (
                capacity_column,
                energy_column,
            ) = st.columns(2)
            with capacity_column:
                clip(Path(scenario_compare_plot_capacity[0]))
                st.image(scenario_compare_plot_capacity[0])
                st.write(scenario_compare_plot_capacity[-1])

            with energy_column:
                clip(Path(scenario_compare_plot_energy[0]))
                st.image(scenario_compare_plot_energy[0])
                st.write(scenario_compare_plot_energy[-1])
        with existing:
            (
                existing_capacity_column,
                existing_energy_column,
            ) = st.columns(2)
            all_comparisons = find_files_containing_string(
                scenario_compare_plot_capacity[2], ".png"
            )
            for file_name in all_comparisons:

                if "capacity" in file_name:
                    with existing_capacity_column:
                        clip(scenario_compare_plot_capacity[2] / file_name)
                        st.image(scenario_compare_plot_capacity[2] / file_name)

                elif "energy" in file_name:
                    with existing_energy_column:
                        clip(scenario_compare_plot_energy[2] / file_name)
                        st.image(scenario_compare_plot_capacity[2] / file_name)

    else:
        st.markdown(
            f"### Selections not valid : check study type:  *{STUDY_TYPES[study_type]['output']}*"
        )
        st.markdown(
            f"### Selections not valid : check if the {left_dir} and {right_dir} have been solved and reporting run"
        )
