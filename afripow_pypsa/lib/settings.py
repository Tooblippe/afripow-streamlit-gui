from __future__ import annotations

from pathlib import Path
import os

import pandas as pd
from addict import Dict

import logging

# Defining 20 distinct colors in HEX
COLOR_1 = "#2E5655"  # APV Slide background blue
COLOR_2 = "#7F7F7F"  # Nuclear
COLOR_3 = "#7F7F7F"  # E-Wind
COLOR_4 = "#F1C40F"  # A shade of yellow
COLOR_5 = "#9B59B6"  # A shade of purple
COLOR_6 = "#E74C3C"  # A shade of red-orange
COLOR_7 = "#16A085"  # A shade of green-blue
COLOR_8 = "#2980B9"  # A shade of ocean blue
COLOR_9 = "#F39C12"  # A shade of orange
COLOR_10 = "#8E44AD"  # A shade of violet
COLOR_11 = "#2ECC71"  # A shade of soft green
COLOR_12 = "#D35400"  # A shade of dark orange
COLOR_13 = "#27AE60"  # A shade of jungle green
COLOR_14 = "#7F8C8D"  # A shade of gray
COLOR_15 = "#C0392B"  # A shade of ruby red
COLOR_16 = "#BDC3C7"  # A shade of silver
COLOR_17 = "#7F8C8D"  # A shade of gray-blue
COLOR_18 = "#2C3E50"  # A shade of midnight blue
COLOR_19 = "#F39C12"  # A shade of dark yellow
COLOR_20 = "#E67E22"  # A shade of carrot orange


colors = [
    COLOR_1,
    COLOR_2,
    COLOR_3,
    COLOR_4,
    COLOR_5,
    COLOR_6,
    COLOR_7,
    COLOR_8,
    COLOR_9,
    COLOR_10,
    COLOR_11,
    COLOR_12,
    COLOR_13,
    COLOR_14,
    COLOR_15,
    COLOR_16,
    COLOR_17,
    COLOR_18,
    COLOR_19,
    COLOR_20,
]

global_figsize = (8, 6.3)


def load_settings(
    settings_file: str | Path = None, path_to_excel_settings: str | Path = None
) -> Dict:
    if not settings_file:
        settings = Dict()

        settings.mpl_style = "ggplot"

        settings.paths.settings_directory = "afripow-pypsa-reporting/settings"

        if not path_to_excel_settings:
            settings.paths.path_to_excel_settings = (
                "pypsa_reporting/settings/reporting_setup_and_settings.xlsm"
            )
        else:
            settings.paths.path_to_excel_settings = path_to_excel_settings

        settings.paths.output_directory = Path("reporting_outputs")

        # if not os.path.isdir(Path(settings.paths.output_directory)):
        #     os.mkdir(Path(settings.paths.output_directory))

        settings.plant_links_sheet = "link_to_plant"
        settings.plant_plot_settings_sheet = "plant_group"
        settings.report_study_years_setup_sheet = "study_years"
        settings.report_link_profiles = "link_profiles"

        settings.colors.table.table_headers = "#A3D3CA"
        settings.colors.plotting.colorslist = colors
        settings.colors.plotting.figsize = global_figsize

        settings.carriers.exclude = ["--"]  # plant carriers is degined in the xls setup

        settings.graphs.capacityplot.divider = 1
        settings.graphs.capacityplot.ylabel = "MW"
        settings.graphs.capacityplot.title = "Capacity Plan for Scenario: "
        settings.graphs.capacityplot.order = []

        settings.graphs.energyplot.divider = 1_000
        settings.graphs.energyplot.ylabel = "GWh"
        settings.graphs.energyplot.title = "Energy Plan for Scenario: "

        # averaege dispatch profile plot settigns
        settings.average_dispatch_energy_plot.title_fontsize = 11
        settings.average_dispatch_energy_plot.y_label = "MWh/h"
        settings.average_dispatch_energy_plot.y_label_fontsize = 11
        settings.average_dispatch_energy_plot.y_ticks_fontsize = 8
        settings.average_dispatch_energy_plot.secondary_y_label = "USD/MWh"
        settings.average_dispatch_energy_plot.secondary_y_label_fontsize = 11
        settings.average_dispatch_energy_plot.secondary_y_ticks_fontsize = 8
        settings.average_dispatch_energy_plot.x_label = "Hour"
        settings.average_dispatch_energy_plot.x_ticks_font_size = 8
        settings.average_dispatch_energy_plot.show_x_label = False

        settings.average_dispatch_energy_plot.demand_line.color = "black"
        settings.average_dispatch_energy_plot.demand_line.linewidth = 2

        settings.average_dispatch_energy_plot.bus_price.color = "red"
        settings.average_dispatch_energy_plot.bus_price.linestyle = "--"
        settings.average_dispatch_energy_plot.bus_price.linewidth = 2

        # link profiles
        # scatter
        settings.link_profiles.scatter.color = "blue"
        settings.link_profiles.scatter.scatter_size = 3

        # LDC
        settings.link_profiles.ldc.color = "blue"

        # Average
        settings.link_profiles.average.color = "blue"

        # now load excel
        path_to_excel_settings = settings.paths.path_to_excel_settings
        try:
            settings.xlxs_settings[settings.plant_links_sheet] = pd.read_excel(
                path_to_excel_settings, sheet_name=settings.plant_links_sheet
            )

            settings.xlxs_settings[settings.plant_plot_settings_sheet] = pd.read_excel(
                path_to_excel_settings, sheet_name=settings.plant_plot_settings_sheet
            )

            settings.xlxs_settings[settings.report_study_years_setup_sheet] = (
                pd.read_excel(
                    path_to_excel_settings,
                    sheet_name=settings.report_study_years_setup_sheet,
                )
            )

            settings.xlxs_settings[settings.report_link_profiles] = pd.read_excel(
                path_to_excel_settings, sheet_name=settings.report_link_profiles
            )

            settings.xlxs_settings["marginal_price_dc"] = pd.read_excel(
                path_to_excel_settings, sheet_name="marginal_price_dc"
            )

            settings.xlxs_settings["dispatch_setup"] = pd.read_excel(
                path_to_excel_settings, sheet_name="dispatch_setup"
            )

            print(f"[ INFO ] - Setttings file loaded : {path_to_excel_settings}")
        except FileNotFoundError:
            print(
                f"[ ERROR ] - Excel settings file not found at '{path_to_excel_settings}'"
            )

        return settings
    else:
        empty_dict = Dict()
        return empty_dict
