from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from math import ceil

from ..helpers.own_types import FigAxDF, NetworkList


def remove_missing_links(
    result_df: pd.DataFrame,
    plot_order: List[str],
    colors_list: List[str],
    debug: bool = False,
) -> Tuple[List[str], List[str]]:
    """
    Removes elements from plot_order and colors_list if they are not present in the capacity_plot_df index.

    Parameters:
    - capacity_plot_df (DataFrame): DataFrame containing the capacity data with an index for validation.
    - plot_order (list): List of items to plot.
    - colors_list (list): List of colors corresponding to items in plot_order.
    - debug (bool): If True, print debugging information. Default is False.

    Returns:
    - tuple: The modified plot_order and colors_list.
    """

    def dprint(message):
        """Helper function for conditional debug printing."""
        if debug:
            print(message)

    try:
        # Convert the DataFrame index to a set for easy comparison
        df_index = set(result_df.columns)
        print(result_df.columns)
        # Identify missing links by finding items in plot_order that are not in df_index
        missing_links = set(plot_order) - df_index

        # Find the indices in plot_order that correspond to missing links
        missing_plants_indices = [
            index for index, plant in enumerate(plot_order) if plant in missing_links
        ]

        # Debugging information
        dprint("--------------------------------------------------")
        dprint("Original Setup Summary")
        dprint("--------------------------------------------------")
        dprint(
            f"Initial Lengths - plot_order: {len(plot_order)}, colors_list: {len(colors_list)}"
        )
        dprint(f"Data entries in result DataFrame: {len(df_index)}")
        dprint(f"Missing links: {missing_links}")
        dprint(plot_order)
        dprint("--------------------------------------------------")

        # Remove items from plot_order and colors_list at the identified indices
        for missing_link_ix in sorted(missing_plants_indices, reverse=True):
            dprint(
                f"Removing: {plot_order[missing_link_ix]}, {colors_list[missing_link_ix]}"
            )
            del plot_order[missing_link_ix]
            del colors_list[missing_link_ix]

        # Debugging information after modification
        dprint("--------------------------------------------------")
        dprint(
            f"Updated Lengths - plot_order: {len(plot_order)}, colors_list: {len(colors_list)}"
        )
        dprint(f"Data entries in result DataFrame: {len(df_index)}")
        dprint("--------------------------------------------------")
        dprint(df_index)
        dprint(plot_order)
        dprint(colors_list)
        dprint("--------------------------------------------------")

        if debug:
            input("Press Enter to continue...")

        return plot_order, colors_list

    except Exception as e:
        dprint("--------------------------------------------------")
        dprint(f"Error: {e}")
        dprint("--------------------------------------------------")
        return (
            plot_order,
            colors_list,
        )  # Return the lists even if an error occurs, unmodified


def capacity_plan_plot(
    case_name: str,
    study_years: list = None,
    study_networks: NetworkList = None,
    plant_links_df: pd.DataFrame = None,
    colors_list: list = None,
    component: str = "Link",
    atrribute_capacity: str = "p_nom_opt",
    groupby: str = "plant_group",
    groupby_to_be_removed: List[str] = ["--"],
    kind: str = "bar",
    stacked: bool = True,
    divider: float = 1,
    plot_order: List[str] = None,  # list of plot order
) -> FigAxDF | None:
    #

    # plot_order and colors_list is a one to one map when it comes in
    # plot_order is a list of plant group ['E_HXB', ....]
    #  colors_list = plot color

    # so must check wich one is not in the list and remove it from the list at both positions

    capacity_plot_df = build_study_static_df(
        study_years,
        study_networks,
        plant_links_df,
        component=component,
        attribute=atrribute_capacity,
        grouby=groupby,
        groupby_to_be_removed=groupby_to_be_removed,
    )

    plot_order, colors_list = remove_missing_links(
        capacity_plot_df, plot_order, colors_list, debug=False
    )

    capacity_plot_df = capacity_plot_df / divider

    if not capacity_plot_df.empty:
        fig, ax = plt.subplots(figsize=global_figsize)

        if plot_order:
            try:
                capacity_plot_df = capacity_plot_df[plot_order]
            except KeyError:
                print("The sort order could not be applied to the df.")

        capacity_plot_df.plot(
            ax=ax,
            color=colors_list,
            kind=kind,
            stacked=stacked,
        )
        # do operations on the graph, this is shared between the two first graphs
        study_stacked_bar_graph(
            fig, ax, f"Capacity plan for Scenario: {case_name}", "MW"
        )

        # set max
        max_val = ceil(capacity_plot_df.sum(axis=1).max())
        step = max_val / 5

        step = round(step)

        ytics_list = np.arange(0, max_val + step, step)
        ytics_list = [round(value / 500) * 500 for value in ytics_list]
        plt.yticks(ytics_list)
        # we now have a fig and ax and df to return
        return fig, ax, capacity_plot_df
    return None


from ..lib.settings import global_figsize


from ..lib.stacked_bar_graph import study_stacked_bar_graph


def build_study_static_df(
    years: List[int],
    networks: NetworkList,
    plant_links_df: pd.DataFrame,  # from settings, how to link links t plant_groups
    component: str = "Link",
    attribute: str = "p_nom_opt",
    grouby: str = "plant_group",
    groupby_to_be_removed: List[str] = ["--"],
) -> pd.DataFrame:
    """Builds a Dataframe of a static component over the study periods

    years : contains a list of study years e.g. [2023, 2024 ... ]
    networks : list of Pypsa networks [N1, N2, N3 ... ]
    component : e.g. Link is where we want to do the aggregation
    attribute : which attribute we want to create the dataframe off - 'p_nom_opt'
    groud by: How do we want to group


    output : DataFrame for p_nom_opt over study period
              Carrier   2023    2024    2025    ...  2040
              BESS        20      30     120           20
               ...        ..
    """
    component_dfs: list = [n.df(component) for n in networks]
    component_dfs = [
        df.reset_index()
        .rename({"Link": "link"}, axis=1)
        .merge(plant_links_df, on="link", how="left")
        for df in component_dfs
    ]

    component_dfs = [
        df.loc[df["include_in_dispatch_profile"] > 0][["p_nom_opt", "plant_group"]]
        for df in component_dfs
    ]

    component_dfs = [df.groupby(grouby).sum() for df in component_dfs]

    static_df = pd.concat(
        [df[attribute] for df in component_dfs],
        axis=1,
        keys=[f"{years[i]}" for i in range(len(component_dfs))],
    ).transpose()

    for remove in groupby_to_be_removed:
        if remove in static_df.columns:
            static_df = static_df.round().drop(groupby_to_be_removed, axis=1)

    if "0" in static_df.columns:
        static_df = static_df.drop("0", axis=1)

    return static_df
