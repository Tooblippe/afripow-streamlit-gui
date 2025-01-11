from __future__ import annotations

__version__ = '25.1.2'


import os
import pickle
from itertools import chain
from pathlib import Path
from typing import List

import easygui

import pandas as pd
import pypsa
from addict import Dict
from matplotlib import pyplot as plt
from matplotlib.pyplot import close

from ..classes.settingsEditor import tk_tree_view

from ..helpers.direcory_cases import find_input_directories
from ..helpers.is_solved_case import is_solved_case

from ..helpers.own_types import FigAxDF
from ..helpers.plot_order_colours import get_plot_order_colours
from ..lib.average_dispatch_energy_plot import (
    average_dispatch_energy_plot,
)
from ..lib.capacity_plan_plot import (
    capacity_plan_plot,
)
from ..lib.df_to_image import df_to_image
from ..lib.energy_plan_plot import (
    energy_plan_plot,
)

from ..lib.energy_capacity_delta_plot import energy_capacity_delta_plot

from ..lib.link_profiles_scatter_ldc_ave import (
    link_profiles_scatter_plot,
    link_profiles_ldc_plot,
    link_profiles_average_plot,
    get_link_total_string,
)
from ..lib.marginal_price_duration_curve import (
    marginal_price_durtion_curve_plot,
)
from ..lib.settings import load_settings


class Report:
    def __init__(
        self,
        case_name: str = "",
        base_directory: str | Path = None,
        study_saved_file: Path | str = "",
        input_dir: str | Path = "Results",
        save_dir: str = "Report_Output",
        path_to_excel_settings: str | Path = None,
    ):
        print("[ Info ] - Reporting being initialized")
        self._case_name = case_name
        self.base_directory = base_directory
        self.input_dir = input_dir  # eg Results
        print(f"[ Info ] - Input directory set to {self.input_dir}")

        self._network_pickle_file = study_saved_file
        self._network_pickle_file = study_saved_file
        self.save_dir = save_dir
        self.path_to_excel_settings = path_to_excel_settings
        self.paths = []

        self.networks = []

        if self.base_directory != None:
            if self.base_directory == "":
                self.base_directory = os.getcwd()

            self.paths = find_input_directories(self.base_directory, self.input_dir)
            self.settings = self.load_settings()
            self.load_study_networks()

        if self._network_pickle_file:
            self.load_saved_study_from_parameter()

        self.settings: Dict = self.load_settings()  # special dict, dot notation dict

        plt.style.use(self.settings.mpl_style)

        # create output directory and clear
        if not self.case_output_directory().exists():
            self.case_output_directory().mkdir()
        # else:
        #     shutil.rmtree(self.case_output_directory(), ignore_errors=True)
        #     self.case_output_directory().mkdir()

        print(f"{self}")

    def load_case_directory(self):
        print("A directory dialog box opened up. Plase select the Case directory")
        case_dir = easygui.diropenbox("Open Case directory")
        if case_dir:
            self.base_directory = case_dir
            self._case_name = Path(self.base_directory).parts[-1]
            self.paths = find_input_directories(self.base_directory, self.input_dir)
            self.load_study_networks()

    def load_study_networks(self) -> None:
        for year in self.all_study_years:
            print(f"[ INFO ] - Importing Pypsa Network from {year}")
            # TODO - error - if network not available here, add blank Pypsa Network
            try:
                loaded_network = pypsa.Network(self.paths[str(year)][year])
                self.networks.append(loaded_network)
            except KeyError:
                self.networks.append(pypsa.Network())

    def save_current_case_to_pickle(self, filename=None) -> None:
        if not filename:
            print(
                "No filename was given. A file dialod opened. Please select a directory, Enter a filename and save "
                "this study."
            )
            filename = easygui.filesavebox("Select file to save", filetypes=["pkl"])
        if filename:
            with open(filename, "wb") as f:
                state = self.gen_app_state()
                pickle.dump(state, f)

    def load_saved_case_from_pickle(self, filename: str = None):
        if not filename:
            print(
                "No filename was given. A file dialod opened. Please select a directory, Select a filename and save "
                "this study."
            )
            filename = easygui.fileopenbox("Open file", filetypes=["*.pkl"])

        if filename:
            print(f"[ INFO ] - Saved file loading : {self._network_pickle_file}")
            self._network_pickle_file = filename
            self.load_saved_study_from_parameter()

    def load_saved_study_from_parameter(self) -> None:
        print(f"[ INFO ] - Saved file loading : {self._network_pickle_file}")
        with open(self._network_pickle_file, "rb") as f:
            self.set_app_state(pickle.load(f))

    def mini_settings_ui(self):
        tk_tree_view(self.gen_app_state())

    def open_xls_settings_file(self):
        import xlwings as xw

        xw.Book(self.path_to_excel_settings, editable=True, read_only=False)

    def __repr__(self):
        return (
            f"[ INFO ] - PyPSA Reporting Case (software version V{__version__})\n"
            f"           - Case name : {self.case_name} \n"
            f"           - Networks count : {len(self.study_networks)}\n"
            f"           - Study years available: {self.all_study_years} \n"
            f"           - Study years reporting: {self.study_years} \n"
            f"           - Working dir : {os.getcwd()}\n"
            f"           - Settings file : {self.base_directory / self.path_to_excel_settings} \n"
            f"           - Output dir: {self.base_directory / self.settings.paths.output_directory}"
        )

    def __str__(self):
        return self.__repr__()

    def get_network_at_year(self, year: int):
        index = self.study_years.index(year)
        return self.study_networks[index]

    @property
    def link_dict(self):
        return {ix: bus for ix, bus in enumerate(self.networks[0].links.index)}

    @property
    def bus_dict(self):
        return {ix: bus for ix, bus in enumerate(self.networks[0].buses.index)}

    @property
    def case_name(self) -> str:
        return self._case_name

    @property
    def all_networks(self) -> List[pypsa.Network]:
        """returns all the loaded networks. This is not contrained by the Excl spreadsheet."""
        return self.networks

    @property
    def study_networks(self) -> List[pypsa.Network]:
        """should only return the networks that is accoaciated with the excel"""

        # this code snippet extract the positions of the years so that the networks can be adjusted
        years_to_use_ix = []
        # this will be a list of the indexes of the years that is used in the main array
        for (
            findme
        ) in (
            self.study_years
        ):  # [2024, 2027, 2028] - this is loaded from the excel file
            for ix, year in enumerate(
                self.all_study_years  # this looks at all the path keys so this is 2023 to 2045
            ):  # e.g [2023, 2024, 2025, ..., 2045]
                if findme == year:
                    years_to_use_ix.append(ix)

        constrained_number_of_networks = []
        for ix in years_to_use_ix:
            constrained_number_of_networks.append(self.networks[ix])

        # return self.networks
        return constrained_number_of_networks

    @property
    def active_carriers(self, discard: List[str] = ["--"]) -> List[str]:
        all_carriers = [n.links.carrier.tolist() for n in self.study_networks]
        carrier_set = set(list(chain(*all_carriers)))
        for item in discard:
            carrier_set.discard(item)
        return list(carrier_set)

    @property
    def all_study_years(self) -> List[int]:
        """all the loaded years"""
        return [int(year) for year in self.paths.keys()]

    @property
    def study_years(self) -> List[int]:
        """returns only the years that is applicable to the study and specced in the settings xlsx file"""
        if self.paths:
            study_iterator = list(  # use the excel limiting on the total cases
                set(
                    self.settings.xlxs_settings.study_years.loc[
                        self.settings.xlxs_settings.study_years.select == 1
                    ]["years"].values.tolist()
                ).intersection(set(self.all_study_years))
            )
            study_iterator.sort()

            # return [int(year) for year in self.paths.keys()]
            return study_iterator
        else:
            return []

    @property
    def full_save_path(self) -> Path:
        return Path(self.base_directory + "//" + self.save_dir)

    def case_output_directory(self, filename: str | Path = None) -> Path:
        output_directory = self.base_directory / Path(
            str(self.settings.paths.output_directory) + "_" + str(self.input_dir)
        )

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        if filename:
            return output_directory / str(filename)

        else:
            return output_directory

    # plots
    # --------------------------------------------------------------------------
    def generate_capacity_plot(
        self,
    ) -> FigAxDF:
        plot_order, plot_colors = get_plot_order_colours(self.settings)

        fig, ax, df = capacity_plan_plot(
            case_name=self.case_name,
            study_years=self.study_years,
            study_networks=self.study_networks,
            plant_links_df=self.settings.xlxs_settings[self.settings.plant_links_sheet],
            colors_list=plot_colors,
            divider=self.settings.graphs.capacityplot.divider,
            groupby_to_be_removed=self.settings.carriers.exclude,
            plot_order=plot_order,
        )
        return fig, ax, df

    def show_capacity_plot(self, show_fig=False):
        fig_name = self.case_output_directory("capacity_plot.png")
        table_name = self.case_output_directory("capacity_plot_table.png")
        csv_name = self.case_output_directory("capacity_plot_table.csv")

        # generate plot
        fig, ax, df = self.generate_capacity_plot()
        fig.savefig(fig_name)
        if show_fig:
            fig.show()
        close()

        df.fillna(0, inplace=True)

        # csv
        df.transpose().to_csv(csv_name)

        # Convert totals to a DataFrame and set its name as 'Total'
        T_df = df.transpose()
        totals = T_df.sum()
        totals = totals.to_frame().T
        totals.index = ["Total"]

        T_df = pd.concat([T_df, totals])
        T_df.index.name = "Supply(MW)"
        # table
        df_to_image(T_df, table_name, decimals=0)

        print(f"Created : {fig_name}")
        print(f"Created : {table_name}")
        print(f"Created : {csv_name}")
        return "Capacity Plot, Table and CSV file generation success."

    # --------------------------------------------------------------------------

    def generate_capacity_delta_plot(self):
        input_file = self.case_output_directory("capacity_plot_table.csv")

        df = pd.read_csv(input_file, index_col=0)
        df.fillna(0, inplace=True)
        df = df.transpose().diff().transpose()
        # print(f"Capacity - Found buses: {df.index.tolist()}")
        plot_order, plot_colors = get_plot_order_colours(
            self.settings, available_plant_check_list=df.index.tolist()
        )
        return energy_capacity_delta_plot("Capacity", self.case_name, df, plot_colors)

    def show_capacity_delta_plot(self):
        try:
            fig, ax, df = self.generate_capacity_delta_plot()
            fig_name = self.case_output_directory("capacity_delta_plot.png")
            fig.savefig(fig_name, bbox_inches="tight")
            print(f"Created : {fig_name}")
        except Exception as e:
            print(f"Error while generating capacity delta plots.")
            print(e)

    # --------------------------------------------------------------------------
    def generate_energy_delta_plot(self):
        input_file = self.case_output_directory("energy_plot_table.csv")

        df = pd.read_csv(input_file, index_col=0)
        df.fillna(0, inplace=True)
        df = df.transpose().diff().transpose()
        # print(f"energy - Found buses: {df.index.tolist()}")

        plot_order, plot_colors = get_plot_order_colours(
            self.settings, available_plant_check_list=df.index.tolist()
        )
        return energy_capacity_delta_plot("Energy", self.case_name, df, plot_colors)

    def show_energy_delta_plot(self):
        try:
            fig, ax, df = self.generate_energy_delta_plot()
            fig_name = self.case_output_directory("energy_delta_plot.png")
            fig.savefig(fig_name, bbox_inches="tight")
            print(f"Created : {fig_name}")
        except:
            print(f"Error while generating energy delta plots.")

    # --------------------------------------------------------------------------

    def generate_energy_plot(
        self,
    ) -> FigAxDF:
        plot_order, plot_colors = get_plot_order_colours(self.settings)

        fig, ax, df = energy_plan_plot(
            case_name=self.case_name,
            study_years=self.study_years,
            study_networks=self.study_networks,
            plant_links_df=self.settings.xlxs_settings[self.settings.plant_links_sheet],
            colors_list=plot_colors,
            divider=self.settings.graphs.energyplot.divider,
            groupby_to_be_removed=self.settings.carriers.exclude,
            plot_order=plot_order,
        )
        return fig, ax, df

    def show_energy_plot(self, show_fig=False):
        fig_name = self.case_output_directory("energy_plot.png")
        table_name = self.case_output_directory("energy_plot_table.png")
        csv_name = self.case_output_directory("energy_plot_table.csv")

        # generate plot
        fig, ax, df = self.generate_energy_plot()
        fig.savefig(fig_name)
        if show_fig:
            fig.show()
        close()

        df.fillna(0, inplace=True)

        # csv
        df.transpose().to_csv(csv_name)

        # table
        # Convert totals to a DataFrame and set its name as 'Total'
        T_df = df.transpose()
        totals = T_df.sum()
        totals = totals.to_frame().T
        totals.index = ["Total"]

        T_df = pd.concat([T_df, totals])
        T_df.index.name = "Supply(GWh)"
        # table
        df_to_image(T_df, table_name, decimals=0)

        print(f"Created : {fig_name}")
        print(f"Created : {table_name}")
        print(f"Created : {csv_name}")
        return "Energy Plot, Table and CSV file generation success."

    # --------------------------------------------------------------------------
    def generate_load_factor_plot(self):
        """
        Reads the energy and capacity data
        return a df :   ENERGY_GWH / ( CAPACITY_MW *8.76 )
        :return:
        """
        energy_output = self.case_output_directory("energy_plot_table.csv")
        capacity_output = self.case_output_directory("capacity_plot_table.csv")
        energy_df = pd.read_csv(energy_output, index_col=0)
        capacity_df = pd.read_csv(capacity_output, index_col=0)
        lf_df = energy_df / (capacity_df * 8.76)
        # lf_df.fillna("-", inplace=True)
        lf_df.to_csv(self.case_output_directory("load_factor_plot_table.csv"))
        lf_df = lf_df * 100
        df_to_image(
            lf_df.fillna(0),
            self.case_output_directory("load_factor_plot_table.png"),
            decimals=1,
        )

    def show_load_factor_plot(self, show_fig=False):
        ...

    # --------------------------------------------------------------------------
    def show_average_dispatch_energy_plot(self, year: int, currency_str):
        fig, ax, df = self.generate_average_dispatch_energy_plot(year, currency_str)

        fig_dir = self.case_output_directory("average_dispatch")
        # print(fig_dir)
        if not os.path.exists(fig_dir):
            # Create the directory
            os.makedirs(fig_dir)

        fig_name = self.case_output_directory(
            Path(f"average_dispatch/average_dispatch_{year}.png")
        )
        fig.savefig(fig_name)
        close()

    def generate_average_dispatch_energy_plot(self, year: int, currency_str) -> FigAxDF:
        n: pypsa.Network = self.get_network_at_year(year)
        fig, ax, df = average_dispatch_energy_plot(
            n,
            self.case_name,
            year=year,
            settings=self.settings,
            currency_str=currency_str,
        )
        return fig, ax, df

    # --------------------------------------------------------------------------

    def generate_marginal_price_durtion_curve_plot(
        self,
        marginal_price_bus,
        settings,
        network_component_type="Link",
        currency_str="$/MWh",
        **kwargs,
    ):
        fig, ax, df = marginal_price_durtion_curve_plot(
            self.networks,
            self.study_years,
            case_name=self.case_name,
            marginal_price_bus=marginal_price_bus,
            settings=settings,
            network_component_type=network_component_type,  # Link or Bus,
            currency_str=currency_str,
            **kwargs,
        )
        return fig, ax, df

    def show_marginal_price_durtion_curve_plot(self, currency_str, **kwargs):
        # get the list of busses from the settings file in sheet "marginal_price_dc"
        # header = bus, list bus values
        settings = self.settings

        for marginal_price_bus in settings.xlxs_settings["marginal_price_dc"][
            "bus"
        ].tolist():
            try:
                fig, ax, df = self.generate_marginal_price_durtion_curve_plot(
                    marginal_price_bus=marginal_price_bus,
                    settings=self.settings,
                    network_component_type="Bus",
                    currency_str=currency_str,
                    **kwargs,
                )
                santise_name = marginal_price_bus.replace("(", "_")
                dir_name = self.case_output_directory("marginal_price")
                if not os.path.exists(dir_name):
                    # Create the directory
                    os.makedirs(dir_name)

                fig_name = self.case_output_directory(
                    f"marginal_price/{santise_name}_marginal_price_durtion_curve.png"
                )
                fig.savefig(fig_name, bbox_inches="tight")
                print(f"Created : {fig_name}")
            except Exception as e:
                print(e)

        for marginal_price_bus in settings.xlxs_settings["marginal_price_dc"][
            "link"
        ].tolist():
            try:
                fig, ax, df = self.generate_marginal_price_durtion_curve_plot(
                    marginal_price_bus=marginal_price_bus,
                    settings=self.settings,
                    network_component_type="Link",
                    currency_str=currency_str,
                    **kwargs,
                )
                santise_name = marginal_price_bus.replace("(", "_")
                fig_name = self.case_output_directory(
                    f"{santise_name}_marginal_price_durtion_curve.png"
                )
                fig.savefig(fig_name, bbox_inches="tight")
                print(f"Created : {fig_name}")
            except Exception as e:
                print(e)

    # -------------------------------------------------------------------------

    # Links Scatter
    def generate_link_profiles_scatter_plot(
        self,
        network,
        study_year: int,
        left_link: str,
        right_link: str,
        left_link_name: str,
        right_link_name: str,
        settings: Dict,
    ):
        fig, ax, df = link_profiles_scatter_plot(
            network,
            study_year,
            left_link,
            right_link,
            left_link_name,
            right_link_name,
            settings,
        )

        return fig, ax, df

    def show_link_profiles_scatter_plot(
        self,
        network: pypsa.Network,
        study_year: int,
        left_link: str,
        right_link: str,
        left_link_name: str,
        right_link_name: str,
        show_fig=False,
    ):
        if is_solved_case(network):
            fig, ax, df = self.generate_link_profiles_scatter_plot(
                network,
                study_year,
                left_link,
                right_link,
                left_link_name,
                right_link_name,
                self.settings,
            )

            if show_fig:
                fig.show()

            if not self.case_output_directory(study_year).exists():
                self.case_output_directory(study_year).mkdir()

            link_total_string_file_str = get_link_total_string(
                left_link, right_link, left_link_name, right_link_name, for_file=True
            )

            fig_name = (
                self.case_output_directory(study_year)
                / f"{link_total_string_file_str}_scatter_{study_year}.png"
            )
            print(f"Created : {fig_name}")
            fig.savefig(fig_name)
            close()
        else:
            print(f"Not a solved case in scatter - attempting {study_year}")

    # Links LDC
    def generate_link_profiles_ldc_plot(
        self,
        network,
        study_year: int,
        left_link: str,
        right_link: str,
        left_link_name: str,
        right_link_name: str,
        settings: Dict,
    ):
        fig, ax, df = link_profiles_ldc_plot(
            network,
            study_year,
            left_link,
            right_link,
            left_link_name,
            right_link_name,
            settings,
        )

        return fig, ax, df

    def show_link_profiles_ldc_plot(
        self,
        network,
        study_year: int,
        left_link: str,
        right_link: str,
        left_link_name: str,
        right_link_name: str,
        show_fig=False,
    ):
        if is_solved_case(network):
            fig, ax, df = self.generate_link_profiles_ldc_plot(
                network,
                study_year,
                left_link,
                right_link,
                left_link_name,
                right_link_name,
                self.settings,
            )
            if show_fig:
                fig.show()

            link_total_string_file_str = get_link_total_string(
                left_link, right_link, left_link_name, right_link_name, for_file=True
            )

            figname = (
                self.case_output_directory(study_year)
                / f"{link_total_string_file_str}_ldc_{study_year}.png"
            )
            fig.savefig(figname)
            close()
            print(f"Created : {figname}")
        else:
            print(f"Not a solved case in LDC - attempting {study_year}")

    # Links Average
    def generate_link_profiles_average_plot(
        self,
        network,
        study_year: int,
        left_link: str,
        right_link: str,
        left_link_name: str,
        right_link_name: str,
        settings: Dict,
    ):
        fig, ax, df = link_profiles_average_plot(
            network,
            study_year,
            left_link,
            right_link,
            left_link_name,
            right_link_name,
            settings,
        )

        return fig, ax, df

    def show_link_profiles_average_plot(
        self,
        network,
        study_year: int,
        left_link: str,
        right_link: str,
        left_link_name: str,
        right_link_name: str,
        show_fig=False,
    ):
        if is_solved_case(network):
            fig, ax, df = self.generate_link_profiles_average_plot(
                network,
                study_year,
                left_link,
                right_link,
                left_link_name,
                right_link_name,
                self.settings,
            )

            if show_fig:
                fig.show()

            link_total_string_file_str = get_link_total_string(
                left_link, right_link, left_link_name, right_link_name, for_file=True
            )

            fig_name = (
                self.case_output_directory(study_year)
                / f"{link_total_string_file_str}_average_{study_year}.png"
            )

            fig.savefig(fig_name)
            close()
            print(f"Created : {fig_name}")
        else:
            print(f"Not a solved case in Average - {study_year}")

    # Settings
    def load_settings(self) -> Dict:
        settings: Dict = load_settings(
            path_to_excel_settings=self.path_to_excel_settings
        )
        settings.graphs.capacityplot.title += self.case_name
        settings.graphs.energyplot.title += self.case_name
        return settings

    def reload_settings(self) -> None:
        self.settings = self.load_settings()

    def set_excel_settings_file(self, path_to_excel_settings: str | Path = None):
        if not path_to_excel_settings:
            self.path_to_excel_settings = easygui.fileopenbox(
                "Choose Settings Excel file"
            )
        else:
            self.path_to_excel_settings = path_to_excel_settings

        self.reload_settings()
        print(self)

    def gen_app_state(self) -> Dict:
        return Dict(
            {
                "Case": self.case_name,
                "Base Dir": self.base_directory,
                "Save Dir": self.save_dir,
                "Current Save": self._network_pickle_file,
                "Years": self.study_years,
                "Paths": self.paths,
                "Networks": self.networks,
                "Settings": self.settings,
                "zCommands": [i for i in dir(self) if i[0] != "_"],
            }
        )

    def set_app_state(self, state: Dict):
        self._case_name = state["Case"]
        self.base_directory = state["Base Dir"]
        self.save_dir = state["Save Dir"]
        self._network_pickle_file = state["Current Save"]
        self.paths = state["Paths"]
        self.networks = state["Networks"]
        self.settings = state["Settings"]


def case_directory_to_save_file(
    case_name: str,
    base_directory: Path | str,
    output_file: Path | str,
    path_to_excel_settings: Path | str,
    input_dir: str | Path = "Results",
):
    r = Report(
        case_name=case_name,
        base_directory=Path(base_directory),
        path_to_excel_settings=Path(path_to_excel_settings),
        input_dir=input_dir,
    )
    print(f"[ INFO ] - Savings save file: {output_file.resolve()}")
    r.save_current_case_to_pickle(output_file.resolve())
