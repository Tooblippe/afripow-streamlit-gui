from pathlib import Path

import numpy as np
import pandas as pd
from afripow_pypsa.lib.stacked_bar_graph import (
    study_stacked_bar_graph,
    format_zero_to_one,
)

from afripow_pypsa.lib.capacity_plan_plot import remove_missing_links

from afripow_pypsa.helpers.plot_order_colours import get_plot_order_colours

from afripow_pypsa.Report.Report import Report

from afripow_pypsa.lib.settings import global_figsize
from matplotlib import pyplot as plt

from afripow_pypsa.helpers.own_types import FigAxDF

# replace with Streamlit inputs
BASE_DIRECTORY = Path(r"C:\Users\apvse\PyPSA_csv\2407_MPA_csv")
CASE_NAME = "S1_No_MHPP"
LOAD_FACTOR_DATA_FILE = Path("load_factor_plot_table.csv")
OUTPUT_IMAGE = Path("load_factor_plot_img.png")
INPUT_DIR = "Results_opt"
RESULTS_DIR = "reporting_outputs_"


def generate_load_factor_plot(
    case_name: str,
    base_directory: Path,  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv')
    path_to_excel_settings: Path,
    input_dir: Path | str,  # Results_opt
    load_factor_data_file: Path | str,  # load_factor_plot_table
    plot_only_these_carriers=None,
    plot_only_these_years=None,
) -> FigAxDF:
    """
    This function creates the fig and df objects for the graph. It does not do any saving
    """
    #
    fig, ax = plt.subplots(figsize=global_figsize)

    # Get the reporting object
    r = Report(
        case_name=case_name,
        base_directory=base_directory,
        path_to_excel_settings=path_to_excel_settings,
        input_dir=input_dir,  # e.h. path to "Input_uc"
        create_output_directories=False,
    )

    # get the predefined plot order and colours from the excel file
    # this will be used later when the years or carriers are contrained
    plot_order, colors_list = get_plot_order_colours(r.settings)

    # read the CSV file containing the loadfactors for this case
    path_to_input_csv = (
        base_directory / case_name / f"{RESULTS_DIR}{input_dir}" / load_factor_data_file
    )
    df = pd.read_csv(path_to_input_csv, index_col="plant_group").transpose()

    # Check if we only asked for spesif years if not plot all
    if plot_only_these_years is None or []:
        plot_only_these_years = df.index

    # Check if only asked for spesific carriers, if not plot all
    if plot_only_these_carriers is None or []:
        plot_only_these_carriers = df.columns

    # clamp the dataframe to plot order, this should not have an effect most of the time, since the capacity
    # and energy plots have been created using this
    df = df[plot_order]

    # only show the selected years, carriers
    df = df.loc[plot_only_these_years, plot_only_these_carriers]

    # align the plot order and colours with the excel setup file
    plot_order, colors_list = remove_missing_links(
        df, plot_order, colors_list, debug=False
    )

    # make the plot
    df.plot(ax=ax, kind="bar", width=0.8, color=colors_list)

    # apply the APV graph rules
    study_stacked_bar_graph(
        fig,
        ax,
        f"Load factors for: {case_name}",
        "Load factor",
        custom_formatter=format_zero_to_one,
    )

    # set y-axis ticks from 0 to 1 in steps of 0.1
    ax.set_ylim(0, 1)
    ax.set_yticks(np.arange(0, 1.1, 0.1))

    # remove vertical gridlines
    ax.xaxis.grid(False)

    # add the value to the rop of the bar
    for container in ax.containers:
        labels = [
            f"{bar.get_height():.2f}" if bar.get_height() != 0 else ""
            for bar in container
        ]

        ax.bar_label(
            container,
            labels=labels,
            fmt="%.2f",  # Format string for 2 decimal places
            label_type="edge",
            rotation=90,
            padding=3,
        )

    # add a line in between every year
    for i in range(1, len(df.index)):
        ax.axvline(x=i - 0.5, color="black", linewidth=1, linestyle="--")

    return fig, ax, df


def show_load_factor_plot(
    case_name: str,
    base_directory: Path,  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv')
    path_to_excel_settings: Path,  # Path(r'C:\Users\apvse\PyPSA_csv\2407_MPA_csv\Reporting_setup_MPA_v3.0.xlsm')
    input_dir: Path | str,  # Results_opt
    load_factor_data_file: Path | str,  # load_factor_plot_table
    plot_only_these_carriers=None,
    plot_only_these_years=None,
):
    """
    This functioj requests the fig and dataframe obkects and decides how to save it.
    In this case only the generated graph will be saved
    """
    #
    fig, ax, df = generate_load_factor_plot(
        case_name,
        base_directory,
        path_to_excel_settings,
        input_dir,
        load_factor_data_file,
        plot_only_these_carriers,
        plot_only_these_years,
    )
    fig.show()


if __name__ == "__main__":
    show_load_factor_plot(
        CASE_NAME,
        BASE_DIRECTORY,
        BASE_DIRECTORY / "Reporting_setup_MPA_v3.0.xlsm",
        INPUT_DIR,
        LOAD_FACTOR_DATA_FILE,
        plot_only_these_years=["2030", "2031", "2032", "2033", "2037"],
        plot_only_these_carriers=["Hydro", "PV", "Gas", "Diesel", "UE", "DSM"],
    )
