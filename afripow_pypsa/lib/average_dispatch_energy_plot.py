from typing import Tuple, Any

import matplotlib.figure
import pandas as pd
import pypsa
from addict import Dict
from matplotlib import pyplot as plt
from matplotlib.pyplot import show

from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter


from .year_hour_to_day import format_with_commas, format_with_decimals, year_to_day_ave
import numpy as np
import matplotlib.ticker as tkr

from ..helpers.plot_order_colours import get_plot_order_colours


def average_dispatch_energy_plot(
    n: pypsa.Network, case_name: str, year: int, settings: Dict, currency_str=None
) -> Tuple[matplotlib.figure.Figure, Axes, pd.DataFrame]:
    # Get the energy flow

    dispatch_settings_from_excel = settings.xlxs_settings["dispatch_setup"]
    marginal_price_bus = dispatch_settings_from_excel["marginal_price_bus"].tolist()[0]
    print(f"Found price bus {marginal_price_bus}")
    load_busses = dispatch_settings_from_excel["load_bus"].tolist()
    print(f"Found load busses {load_busses}")

    if not currency_str:
        y2_label = "$/MWh"
    else:
        y2_label = currency_str

    # energy df
    energy_df_8760 = n.links_t["p0"]
    energy_df = year_to_day_ave(energy_df_8760).drop("__Hour", axis=1).transpose()
    plant_links_df = settings.xlxs_settings[settings.plant_links_sheet]
    energy_df = (
        energy_df.reset_index()
        .rename({"Link": "link"}, axis=1)
        .merge(
            plant_links_df[["plant_group", "link", "include_in_dispatch_profile"]],
            on="link",
            how="left",
        )
    )
    energy_df = energy_df.loc[energy_df["include_in_dispatch_profile"] > 0]
    energy_df = energy_df.drop("include_in_dispatch_profile", axis=1)

    # Remove 0's, only possstivie numbers
    energy_df = energy_df.groupby("plant_group").sum()
    # energy_df = energy_df.loc[energy_df > 0].groupby("plant_group").sum()

    energy_df = energy_df.drop("link", axis=1)
    energy_df = energy_df.transpose()

    #
    df_load_8760 = n.loads_t["p"][load_busses].sum(axis=1).to_frame(name="Demand")

    # marginal_price
    try:  # are there a price bus or not, see if it can get the values from buses_t
        df_price_8760 = n.buses_t["marginal_price"][marginal_price_bus].to_frame(
            "Price"
        )
        price_df = year_to_day_ave(pd.DataFrame(df_price_8760, columns=["Price"]))
    except:
        df_price_8760 = pd.DataFrame()  # just set an empty df

    plot_order, plot_colors = get_plot_order_colours(settings)

    global_figsize = (8, 6.3)

    df_load = year_to_day_ave(pd.DataFrame(df_load_8760, columns=["Demand"]))

    # plot setup
    f_size = global_figsize
    title = f"Average daily dispatch profile for '{case_name}' in the year {year}"
    y_title = "MWh/h"

    demand_colour = "black"
    price_color = "#C00000"
    load_width = 2.5  # Example value for load line thickness
    price_width = 2.5  # Example value for price line thickness
    title_settings = {"fontsize": "x-large", "pad": 20}

    # Adjusting the plot with the provided specifications and applying colors array to the bar chart
    fig, ax1 = plt.subplots(figsize=f_size)

    # Line graph for the load dataframe

    df_load["Demand"].plot(
        kind="line", color=demand_colour, ax=ax1, label="Demand", linewidth=load_width
    )

    # Stacked bar graph for the energy dataframe with specified colors
    energy_df[plot_order].plot(
        kind="bar", stacked=True, ax=ax1, width=0.8, color=plot_colors
    )
    ax1.set_ylabel(y_title, fontsize="x-large")

    ax2 = ax1.twinx()
    # Line graph for the price dataframe

    if not df_price_8760.empty:
        price_df["Price"].plot(
            kind="line",
            color=price_color,
            linestyle="dashed",
            ax=ax2,
            label="Price",
            linewidth=price_width,
        )
        ax2.set_ylim(0, max(price_df["Price"] * 1.5))
    else:
        print("Ignoring Price line in dispatch plot.")

    # Labels and legend
    ax2.set_ylabel(y2_label, fontsize="large")

    ax1.set_xlabel("Hour")

    # Legend below the x-axis
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    # move demand line in legend from start position to last
    # pop the first element and add it to the last.
    li = lines.pop(0)
    la = labels.pop(0)
    lines.append(li)
    labels.append(la)

    legend = ax1.legend(
        lines + lines2,
        labels + labels2,
        loc="upper center",
        ncol=4,
        bbox_to_anchor=(0.5, -0.20),
        frameon=False,
        shadow=True,
        fontsize="large",
    )

    plt.title(title, **title_settings)
    plt.xticks(ticks=np.arange(0, 24, 1), labels=np.arange(1, 25, 1))
    plt.xticks(rotation=90, fontsize="x-large")

    plt.yticks(fontsize="x-large")

    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    formatter_commas = tkr.FuncFormatter(format_with_commas)
    formatter_dec = tkr.FuncFormatter(format_with_decimals)

    # Apply the formatter to the y-axis (you could apply it to the x-axis with ax.xaxis.set_major_formatter)
    ax1.yaxis.set_major_formatter(formatter_commas)
    # ax2.yaxis.set_major_formatter(formatter_dec)

    ax1.tick_params(axis="y", labelsize="large")
    ax2.tick_params(axis="y", labelsize="large")
    plt.tight_layout()
    # plt.show()

    return fig, ax1, df_load
