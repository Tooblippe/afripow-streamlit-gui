import pdb
from typing import Tuple, Any, List

import numpy as np
import pandas as pd
import pypsa
from addict import Dict
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .year_hour_to_day import format_with_commas
from ..lib.settings import global_figsize
import matplotlib.ticker as tkr


def marginal_price_durtion_curve_plot(
    networks: List[pypsa.Network],
    study_years: List[int],
    case_name: str,
    marginal_price_bus: str,
    settings: Dict,
    y_lim=(0, 500),
    network_component_type="Link",  # Link or Bus
    currency_str="$/MWh",
    **kwargs,
) -> Tuple[Figure, Axes, pd.DataFrame]:
    marginal_price_durtion_curve_df = pd.DataFrame()

    title_settings = {"fontsize": "x-large", "pad": 20}

    fig, ax = plt.subplots(figsize=global_figsize)

    dfs = []

    if network_component_type == "Bus":
        curve_type = "Price"
    elif network_component_type == "Link":
        curve_type = "Cost"

    def get_base_data(n):
        if network_component_type == "Bus":
            return pd.DataFrame(n.buses_t["marginal_price"][marginal_price_bus])
        elif network_component_type == "Link":
            return pd.DataFrame(n.links_t["marginal_cost"][marginal_price_bus])

    for i, n in enumerate(networks):
        try:
            ldc_vals_this_year = (
                # pd.DataFrame(n.buses_t["marginal_price"][marginal_price_bus])
                get_base_data(n)
                .sort_values(by=marginal_price_bus, ascending=False)
                .reset_index(drop=True)
            )
            dfs.append(ldc_vals_this_year)
        except:
            # print(f"Not found in in this year network: {marginal_price_bus}")
            pass

    # Build the plotting cuve
    for ix, df in enumerate(dfs):
        marginal_price_durtion_curve_df[str(study_years[ix])] = df[marginal_price_bus]

    marginal_price_durtion_curve_df.plot(ax=ax)
    plt.title(
        f"Marginal {curve_type} Duration Curve ({marginal_price_bus})",
        **title_settings,
    )

    # plt.ylabel("$/MWh")  # Set the label text here
    # ax.set_ylim(y_lim)
    plt.ylabel(currency_str, fontsize="large")
    plt.xlabel("Sequential hours in year", fontsize="large")
    plt.yticks(fontsize="medium")

    plt.ylim((0, marginal_price_durtion_curve_df.max().max()))
    plt.xlim(0, 8760)

    x_ticks_labels = np.arange(0, 8761, 730)
    plt.xticks(ticks=x_ticks_labels, labels=x_ticks_labels)
    plt.xticks(rotation=90)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.45, -0.20),
        frameon=False,
        shadow=True,
        ncol=8,
        fontsize="small",
    )

    # apply kwargs
    if "marginal_price_durtion_curve_plot" in kwargs.keys():
        if "plt" in kwargs["marginal_price_durtion_curve_plot"].keys():
            plt.ylim(kwargs["marginal_price_durtion_curve_plot"]["plt"]["ylim"])

    formatter_commas = tkr.FuncFormatter(format_with_commas)
    ax.yaxis.set_major_formatter(formatter_commas)
    ax.xaxis.set_major_formatter(formatter_commas)

    return fig, ax, marginal_price_durtion_curve_df
