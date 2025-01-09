from __future__ import annotations

from typing import List

import pandas as pd
import pypsa
from matplotlib import pyplot as plt

from .capacity_plan_plot import remove_missing_links
from ..helpers.own_types import FigAxDF
from ..lib.settings import global_figsize
from ..lib.stacked_bar_graph import study_stacked_bar_graph


def build_study_time_series_df(
    years: List[int],
    networks: List[pypsa.Network],
    plant_links_df: pd.DataFrame,  # from settings, how to link links t plant_groups,
    component: str = "Link",
    attribute: str = "p0",
    grouby: str = "carrier",
    groupby_to_be_removed: List[str] = ["--"],
) -> pd.DataFrame:
    component_dfs: list = [n.pnl(component)[attribute] for n in networks]
    # component_dfs = [
    #     df.sum()
    #     .reset_index()
    #     .rename({"Link": "link"}, axis=1)
    #     .merge(plant_links_df, on="link", how="left")
    #     for df in component_dfs
    # ]
    component_dfs = [
        df[df > 0]  # added this to force sum to only possitive energy values e.g. BESS
        .sum()
        .reset_index()
        .rename({"Link": "link"}, axis=1)
        .merge(plant_links_df, on="link", how="left")
        for df in component_dfs
    ]

    component_dfs = [df.rename(columns={0: attribute}) for df in component_dfs]

    component_dfs = [
        df.loc[df["include_in_dispatch_profile"] > 0][[attribute, "plant_group"]]
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


def energy_plan_plot(
    case_name: str,
    study_years: List[int] = None,
    study_networks: List[pypsa.Network] = None,
    plant_links_df: pd.DataFrame = None,
    colors_list: List[str] = None,
    component: str = "Link",
    atrribute_capacity: str = "p0",
    groupby: str = "plant_group",
    groupby_to_be_removed: List[str] = ["--"],
    kind: str = "bar",
    stacked: bool = True,
    divider: float = 1000,
    plot_order: List[str] = None,  # list of plot order
) -> FigAxDF | None:
    energy_plot_df = build_study_time_series_df(
        study_years,
        study_networks,
        plant_links_df,
        component=component,
        attribute=atrribute_capacity,
        grouby=groupby,
        groupby_to_be_removed=groupby_to_be_removed,
    )

    plot_order, colors_list = remove_missing_links(
        energy_plot_df, plot_order, colors_list, debug=False
    )

    energy_plot_df = energy_plot_df / divider

    if not energy_plot_df.empty:
        fig, ax = plt.subplots(figsize=global_figsize)

        if plot_order:
            try:
                energy_plot_df = energy_plot_df[plot_order]
            except KeyError:
                print("The sort order could not be applied to the df.")

        energy_plot_df.plot(
            ax=ax,
            color=colors_list,
            kind=kind,
            stacked=stacked,
        )
        study_stacked_bar_graph(
            fig, ax, f"Energy plan for Scenario: {case_name}", "GWh"
        )
        return fig, ax, energy_plot_df
    else:
        return None
