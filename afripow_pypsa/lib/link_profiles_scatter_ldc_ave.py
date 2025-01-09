import pdb
from typing import Tuple, Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import pandas as pd
import pypsa
from addict import Dict

from ..lib.settings import global_figsize
from ..lib.year_hour_to_day import get_24hour_ricks

from matplotlib.pyplot import scatter, plot, show


def get_link_total_string(left_link, right_link, left_name, right_name, for_file=False):
    """generates the LEFT_LINK > RIGHT LING or replace > with _ if for file is True"""

    left_text = left_name
    right_text = right_name

    # add the filenames regardless - replaced the below
    if type(left_text) == float:
        left_text = ""

    if type(right_text) == float:
        right_text = ""

    to = ""
    if left_text and right_text:
        to = ">"
        if for_file:
            to = "_"

    return f"{left_text}{to}{right_text}"


def create_link_profiles_plot_df(
    network: pypsa.Network,
    study_year: int,
    left_link: str,
    right_link: str,
):
    """
    input twee links - p0

    1. scatter plot of the incoming and outgoing link, scatter both, second one p0 but negative,
       dus is die scatter plot potntial 8760 waardes bo, en 8760 waardes onder

    2. LDC - die naam van die link (positief of negatief) - twee kurwes

    3. average link in 24 hours (possitive or negatief) - twee kurwes, mean

    Note - Add days 1 to 7 also in the aggregation
         - Months
    """
    # create dataframe
    # TODO - error - if Link is not in case, print note and move on

    # print("Debugging info for left_link, right_link")
    # print(f"LEFT  - {left_link}, {type(left_link)} ")
    # print(f"RIGHT - {right_link}, {type(right_link)} ")

    if type(left_link) == float:
        # print("No left link")
        left_link = None

    if type(right_link) == float:
        # print("No right link")
        right_link = None

    if left_link and not right_link:
        # print("only left link, possive")
        left_data: pd.DataFrame = network.links_t["p0"][left_link]
        data = left_data

    if right_link and not left_link:
        # print("only right link, neagtive")
        right_data = network.links_t["p0"][right_link]
        data = right_data * -1
        # print(data)

    if left_link and right_link:
        # print("both links")
        left_data = network.links_t["p0"][left_link]
        right_data = network.links_t["p0"][right_link]
        data = left_data - right_data

    data = data.reset_index()
    data["hour"] = get_24hour_ricks(data)

    try:
        data.rename(columns={left_link: 0}, inplace=True)
    except:
        pass

    try:
        data.rename(columns={right_link: 0}, inplace=True)
    except:
        pass

    try:
        data = data.drop("snapshot", axis=1)
    except:
        data = data.drop(
            "period", axis=1
        )  # not sure but for some reason some files dont have the snapshot key

    return data


def link_profiles_scatter_plot(
    network: pypsa.Network,
    study_year: int,
    left_link: str,
    right_link: str,
    left_name: str,
    right_name: str,
    settings: Dict,
) -> Tuple[Figure, Axes, pd.DataFrame]:
    data = create_link_profiles_plot_df(network, study_year, left_link, right_link)

    config = settings.link_profiles.scatter
    # Scatter plot

    x = data.index
    y = data[0].values
    fig, ax = plt.subplots(figsize=global_figsize)

    ax.scatter(x, y, s=config.scatter_size, c=config.color)

    # set left to right string based on left and right link status
    link_total_string = get_link_total_string(
        left_link, right_link, left_name, right_name
    )

    plt.title(
        f"Scatter Plot for {link_total_string} in {study_year}",
        fontsize=15,
        pad=20,
        color="black",
    )
    ax.tick_params(axis="both", colors="black")

    plt.ylabel("MW", color="black")  # Set the label text here
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1000))
    ax.set_xticks(np.append(ax.get_xticks(), 8760))
    ax.set_xlim(left=-100)
    ax.set_xlim(right=8860)

    if min(y) >= 0:
        plt.ylim(bottom=0)  # Set the lower y-limit to 0

    # Optionally, you can format the tick labels as well
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: int(x)))
    ax.set_xlabel("Hour in calender year", labelpad=10, color="black")
    return fig, ax, data


def link_profiles_ldc_plot(
    network: pypsa.Network,
    study_year: int,
    left_link: str,
    right_link: str,
    left_name,
    right_name,
    settings: Dict,
) -> Tuple[Figure, Axes, pd.DataFrame]:
    config = settings.link_profiles.ldc
    data = create_link_profiles_plot_df(network, study_year, left_link, right_link)
    # Load duration curve
    fig, ax = plt.subplots(figsize=global_figsize)

    ldc_plot_data = (
        data[0].sort_values(ascending=False).reset_index().drop("index", axis=1)
    )
    ldc_plot_data.plot(ax=ax, color=config.color)

    link_total_string = get_link_total_string(
        left_link, right_link, left_name, right_name
    )

    plt.title(
        f"Duration Profile for {link_total_string} in {study_year}",
        fontsize=15,
        pad=20,
        color="black",
    )
    plt.legend([])
    ax.tick_params(axis="both", colors="black")
    plt.ylabel("MW", color="black")  # Set the label text here
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1000))
    ax.set_xticks(np.append(ax.get_xticks(), 8760))
    ax.set_xlim(left=-100)
    ax.set_xlim(right=8860)

    # if all the values are bigger than 0, then set the y-lim to 0
    # if min(ldc_plot_data) >= 0:
    #     plt.ylim(bottom=0)  # Set the lower y-limit to 0

    # plt.ylim(top=max(ldc_plot_data) * 1.2)  # Set the lower y-limit to 0

    # Optionally, you can format the tick labels as well
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: int(x)))
    ax.set_xlabel("Hour in calender year", labelpad=10, color="black")
    return fig, ax, data


def link_profiles_average_plot(
    network: pypsa.Network,
    study_year: int,
    left_link: str,
    right_link: str,
    left_name,
    right_name,
    settings: Dict,
) -> Tuple[Figure, Axes, pd.DataFrame]:
    config = settings.link_profiles.average
    data = create_link_profiles_plot_df(network, study_year, left_link, right_link)
    # Average hour plot
    fig, ax = plt.subplots(figsize=global_figsize)

    df = data.groupby("hour").mean()

    try:
        # df = df.iloc[:, 1]
        df.iloc[:, 1].plot(ax=ax, color=config.color)
    except IndexError:
        df.plot(ax=ax, color=config.color)

    link_total_string = get_link_total_string(
        left_link, right_link, left_name, right_name
    )
    plt.title(
        f"Avg Daily Profile for {link_total_string} in {study_year}",
        fontsize=15,
        pad=20,
        color="black",
    )
    plt.legend([])
    plt.xticks(np.arange(1, 25, 1))
    ax.tick_params(axis="both", colors="black")
    plt.ylabel("MW", color="black")  # Set the label text here
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_xticks(np.append(ax.get_xticks(), 24))
    ax.set_xlim(left=1)
    ax.set_xlim(right=24)

    if min(df[0]) >= 0:
        ax.set_ylim(bottom=0)

    # Optionally, you can format the tick labels as well
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: int(x)))
    ax.set_xlabel("Hour in the day", labelpad=10, color="black")
    ax.fill_between(df.index, df[0], facecolor=config.color, alpha=0.3)
    return fig, ax, data
