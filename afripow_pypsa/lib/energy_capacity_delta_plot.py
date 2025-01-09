from __future__ import annotations

import pdb
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from ..helpers.own_types import FigAxDF

import math


# add the energy and capacity delta plot based on plot_type
def energy_capacity_delta_plot(
    plot_type: str, scenario: str, df: pd.DataFrame, colors: List[str]
) -> FigAxDF:
    # # Read the data into a dataframe
    # df = pd.read_csv(input_file, index_col=0)
    # df.fillna(0, inplace=True)
    # df = df.transpose().diff().transpose()

    # Define plot dimensions and aspect ratio
    desired_width = 10  # For example, 10 inches
    aspect_ratio = 16 / 9  # For a 16:9 aspect ratio
    desired_height = (
        desired_width / aspect_ratio
    ) * 1.1  # Calculate the height to maintain the aspect ratio

    # Set plot title and axis labels
    title = f"Annual {plot_type} Change for Scenario: {scenario}"
    y_label = "GWh" if plot_type != "Capacity" else "MW"
    x_label = "year"

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(desired_width, desired_height))
    df.transpose().plot(kind="bar", stacked=True, ax=ax, color=colors)

    # Add vertical lines to separate the groups of bars
    for i in range(len(df.transpose()) + 1):
        plt.axvline(x=i - 0.5, color="white", linestyle="-", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=1)

    # Remove the legend
    if ax.get_legend() is not None:
        ax.get_legend().remove()

    # Set y-axis ticks and labels
    min_max_df = df.reset_index().drop("plant_group", axis=1)
    # print(min_max_df)
    max_y_val = math.ceil(min_max_df[min_max_df > 0].sum(axis=0).max())
    min_y_val = math.floor(min_max_df[min_max_df < 0].sum(axis=0).min())
    interval = math.ceil((max_y_val - min_y_val) / 8)

    # print(max_y_val)
    # print(min_y_val)

    ticks_plus = list(np.arange(0, max_y_val + interval, interval))
    if min_y_val == 0:
        ticks_minus = []
    else:
        ticks_minus = list(np.arange(min_y_val, 0, interval))

    ticks = ticks_minus + ticks_plus
    # print(ticks)

    ax.set_yticks(ticks)
    plt.yticks(ticks=ticks, labels=ticks)
    # ax.set_yticklabels(["{:,}".format(int(x)) for x in ticks])

    # Create the table below the plot
    cell_text = []
    for row in df[::-1].itertuples():
        cell_text.append(["%1.0f" % x if not np.isnan(x) else "-" for x in row[1:]])
    cell_text.reverse()

    # print(df.index)
    # print(colors)
    #
    # input("enter")
    the_table = plt.table(
        cellText=cell_text,
        rowLabels=df.index,
        rowColours=colors,
        colLabels=df.columns,
        loc="bottom",
    )

    # Customize the table appearance
    for i, row in enumerate(df.index):
        cell = the_table.get_celld()[(i + 1, -1)]
        cell.set_facecolor(colors[i])
    plt.grid(axis="y")

    # add a small padding of 0.03 to all cells in the_table

    # Set axis labels and title
    plt.ylabel(y_label)
    plt.xticks([])
    # plt.title(title)
    plt.title(title, fontsize="x-large", pad=20)

    # Save the plot as an image

    # Adjust layout for the table
    plt.subplots_adjust(left=0.2, bottom=0.2)

    fig = plt.gcf()
    return fig, ax, df
