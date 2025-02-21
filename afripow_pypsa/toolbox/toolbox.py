# from __future__ import annotations

import os
import shutil
import warnings
import time
from pathlib import Path
from pprint import pprint

import linopy
import pandas as pd
import pypsa
import winsound
from pypsa.descriptors import nominal_attrs
import numpy as np
from questionary import password

from ..Report.Report import Report, __version__

__version__ = __version__

from ..helpers.direcory_cases import remove_non_directory_files, find_int_named_subdirs
from ..pypsa_toolbox.reserves import add_all_reserve_constraints

print(f"Using toolbox version: {__version__}")


def add_multi_index_investment_periods(network: pypsa.Network):
    network.investment_periods = pd.Index([0])


def add_generator_info(network):
    componenet_type = "Generator"
    print(f"Adding {componenet_type} info")
    p_opt = "p_nom_opt"  #
    p_t = "p"

    _component_ref = network.df(componenet_type)  # refernce to e.g. Link
    _component_ref_t = network.pnl(componenet_type)  # reference to Lint_t

    _component_ref["total_cost__"] = (
        _component_ref["capital_cost"] * _component_ref[p_opt]
    )
    _component_ref["total_energy__"] = _component_ref_t[p_t].sum()

    # calcs on results of calcs a bove
    _component_ref["total_variable_cost__"] = (
        _component_ref["marginal_cost"] * _component_ref["total_energy__"]
    )
    _component_ref["ave_lf__"] = _component_ref["total_energy__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%

    _component_ref["ave_cost__"] = (
        _component_ref["total_cost__"] + _component_ref["total_variable_cost__"]
    ) / _component_ref["total_energy__"]
    return


def add_link_info(network):
    componenet_type = "Link"
    print(f"Adding {componenet_type} info")
    p_opt = "p_nom_opt"
    p_t = "p0"

    _component_ref = network.df(componenet_type)  # refernce to e.g. Link
    _component_ref_t = network.pnl(componenet_type)  # reference to Lint_t

    _component_ref["total_capital_cost__"] = (
        _component_ref["capital_cost"] * _component_ref[p_opt]
    )
    _component_ref["total_energy__"] = _component_ref_t[p_t].sum()

    # calcs on results of calcs a bove
    _component_ref["total_variable_cost__"] = (
        _component_ref["marginal_cost"] * _component_ref["total_energy__"]
    )
    _component_ref["ave_lf__"] = _component_ref["total_energy__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%

    _component_ref["ave_cost__"] = (
        _component_ref["total_capital_cost__"] + _component_ref["total_variable_cost__"]
    ) / _component_ref["total_energy__"]


def add_lines_info(network):
    componenet_type = "Line"
    print(f"Adding {componenet_type} info")
    p_opt = "s_nom"
    p_t = "p0"

    _component_ref = network.df(componenet_type)  # refernce to e.g. Link
    _component_ref_t = network.pnl(componenet_type)  # reference to Lint_t

    _component_ref["total_cost__"] = (
        _component_ref["capital_cost"] * _component_ref[p_opt]
    )
    _component_ref["total_energy__"] = _component_ref_t[p_t].sum()

    # calcs on results of calcs a bove
    # line does not have a marginal cost
    # _component_ref['total_variable_cost__'] = _component_ref['marginal_cost'] * _component_ref['total_energy__']
    _component_ref["ave_lf__"] = _component_ref["total_energy__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%

    _component_ref["ave_cost__"] = (_component_ref["total_cost__"]) / _component_ref[
        "total_energy__"
    ]
    return


def add_storage_units_info(network):
    componenet_type = "StorageUnit"
    print(f"Adding {componenet_type} info")
    p_opt = "p_nom_opt"
    p_t_dispatch = "p_dispatch"
    p_t_store = "p_store"

    _component_ref = network.df(componenet_type)  # refernce to e.g. Link
    _component_ref_t = network.pnl(componenet_type)  # reference to Lint_t

    _component_ref["total_cost__"] = (
        _component_ref["capital_cost"] * _component_ref[p_opt]
    )

    _component_ref["total_energy_dispatch__"] = _component_ref_t[p_t_dispatch].sum()
    _component_ref["total_energy_store__"] = _component_ref_t[p_t_store].sum()

    # calcs on results of calcs a bove
    _component_ref["total_variable_cost_dispatch__"] = (
        _component_ref["marginal_cost"] * _component_ref["total_energy_dispatch__"]
    )
    _component_ref["total_variable_cost_store__"] = (
        _component_ref["marginal_cost"] * _component_ref["total_energy_store__"]
    )

    _component_ref["ave_lf_dispatch__"] = _component_ref["total_energy_dispatch__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%
    _component_ref["ave_lf_store__"] = _component_ref["total_energy_store__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%

    _component_ref["ave_cost__"] = (
        _component_ref["total_cost__"]
        + _component_ref["total_variable_cost_dispatch__"]
        + _component_ref["total_variable_cost_store__"]
    ) / (_component_ref["total_energy_dispatch__"])
    return


def add_stores_info(network):
    componenet_type = "Store"
    print(f"Adding {componenet_type} info")
    p_opt = "e_nom_opt"
    p_t = "p"

    _component_ref = network.df(componenet_type)  # refernce to e.g. Link
    _component_ref_t = network.pnl(componenet_type)  # reference to Lint_t

    _component_ref["total_cost__"] = (
        _component_ref["capital_cost"] * _component_ref[p_opt]
    )

    df = _component_ref_t[p_t]
    _component_ref["total_energy_store__"] = df[df < 0].sum()  # all negative values
    _component_ref["total_energy_dispatch__"] = df[df > 0].sum()  # all positive  values

    # calcs on results of calcs a bove
    _component_ref["total_variable_cost__"] = (
        _component_ref["marginal_cost"] * _component_ref["total_energy_dispatch__"]
    )

    _component_ref["ave_lf_store__"] = _component_ref["total_energy_store__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%
    _component_ref["ave_lf_dispatch__"] = _component_ref["total_energy_dispatch__"].div(
        (_component_ref[p_opt] * 8760), np.nan
    )  # %%

    _component_ref["ave_cost__"] = (
        _component_ref["total_cost__"] + _component_ref["total_variable_cost__"]
    ) / _component_ref["total_energy_dispatch__"]
    return


def add_summaries(network):
    """call this function"""
    add_generator_info(network)
    add_link_info(network)
    add_lines_info(network)
    add_storage_units_info(network)
    add_stores_info(network)


def change_element_attrib(network, component, name, attribute, value):
    """
    component : str -> 'links', 'generators' etc....
    name : str -> name of element in component e.g. busname, link name OR 'all' to set all value
    attribute : str -> 'p_nom_opt', "p_nom_extendable"
    value : type of attrib_name -> 0.1 or True/False

    example:
    change_element_attrib( network, "links", "LINK_1_ZIM", "p_nom", 123 )

    """
    df = getattr(network, component)
    if not df.empty:
        if name != "all":
            df.loc[df.index == name, attribute] = value
        else:
            df[name] = value


def get_list_from_dataframe_columns(df, column):
    """return a column from a dataframe as a list and does checking on the values in there"""
    try:
        l = df.loc[
            df[column] == 1
        ].index.to_list()  # find columns named column and get the index values where ==1
    except KeyError:
        print(f"Nminus1 - {column} does not exists in {df}")
        l = []

    return l


def make_all_non_extendable(n: pypsa.Network):
    """this is a copy of n.optimize.fix_optimal_capacities()"""
    # from pypsa.descriptors import nominal_attrs
    print("\n\nRunnning make_all_non_extendable")
    print("=======================")
    for c, attr in nominal_attrs.items():
        print(f"Setting {c}-{attr}")
        ext_i = n.get_extendable_i(c)
        n.df(c).loc[ext_i, attr] = n.df(c).loc[ext_i, attr + "_opt"]
        n.df(c)[attr + "_extendable"] = False
    print("=======================\n")


def make_extendable(network: pypsa.Network):
    # from pypsa.descriptors import nominal_attrs
    print("\nRunning make_extendable")
    print("=======================")
    for c, attr in nominal_attrs.items():
        print(f"Setting extendable True for {c}")
        c_df = network.df(c)
        try:
            c_df.loc[c_df.make_ext == 1, f"{attr}_extendable"] = True
        except AttributeError:
            print(
                f"When setting extendable to true for {c}, the column make_ext was not found"
            )
    print("=======================\n")

    # for item in attr - [links, transformers ..]
    # column = "make_ext"==1
    # list of links, trans, store
    # thos must be extendable = true
    # component = "links"
    # name = "Lk150_(DSM_All-B_RSA)" # Lk178_(CUE_All-B_CUE)
    # attribute = "p_nom_extendable"
    # value = True
    # change_element_attrib(network, component, name, attribute, value)
    # name = "Lk178_(CUE_All-B_CUE)"
    # change_element_attrib(network, component, name, attribute, value)


def increase_load_fixed(n: pypsa.Network, inputs_folder_name):
    print("\nRunning increase_load_fixed")
    print("=======================")
    inc_load_df = pd.read_csv(inputs_folder_name + "\inc_load.csv")
    for i, load in enumerate(inc_load_df.itertuples(index=False)):
        print(f"Adding to load {load.inc_load} + {load.value_mw} MW")
        load_name = load.inc_load
        n.loads_t["p_set"][load_name] = n.loads_t["p_set"][load_name] + load.value_mw
    print("=======================\n")
    #
    # copy inc_load_csv --> down
    # inc_load	value_mw
    # increase_load_fixed(network,  load_name = inc_load, fixed =value_mw)
    # n.loads_t['p_set'][load_name] = n.loads_t['p_set'][load_name] + fixed


def fix_n_minus_capacities(
    path_to_networks: str | Path,  # path to scenarios
    current_network: pypsa.Network,
    current_year: int,
    # attr_zero_dict: dict[str : list[str]] = None,
) -> None:
    # network.links['do_not_fix'] == 1 ---> Links ---set to 0 / "do not fix"
    """
    :argument
    -------
        'path_to_networks': str|Path to the base folder e.g. "Base-31May" etc, inside is 2024, 2025, etc
        'current_network' : pypsa.Network, this is the current solved pypsa Network object
        'current_year'    : int, this is the current report year. Will be used to load year n-1 network (previous_network)
        'attr_zero_dict'  : dict, dictionary containing attrs and list of attrs to set" 'p|e|s_nom_min' to zero
                          e.g   {
                                      "Generator": [], generators
                                      "Line": [],   lines
                                      "Link": [                 #DO_NOT_FIX - set to 0 links
                                          "Lk90_(B1_PV-B2_PV)",
                                          "Lk92_(B2_PV-B_ZimN)",
                                          "Lk93_(B2_PV-B_ZimS",
                                          "Lk225_(B_BES3-B_ZimS)",
                                      ],
                                      "Store": [], stores
                                      "StorageUnit": ["NES_ZimS"], storage_units
                                }

    :methodology
    -----------
        1. This function will load the network for current_year-1 -> previous_network
        2. It will iterate through 'nominal_attrs' = {
                                                    "Generator": "p_nom",
                                                    "Line": "s_nom",
                                                    "Transformer": "s_nom",
                                                    "Link": "p_nom",
                                                    "Store": "e_nom",
                                                    "StorageUnit": "p_nom",
                                                    }

        3. set 'current_network': 'p|e|s_nom_min' to 'previous_network': 'p|e|s_nom_opt'

        4. Set 'current_network': 'p|e|s_nom_min' to 0 as spesified in 'attr_zero_dict'

    :return
        none
    """

    print("\n\nRunning fix_n_minus_capacities")
    print("---------------------------")
    previous_year = int(current_year) - 1
    previous_network = None
    try:
        previous_network = load_network_at_year(
            path_to_networks, current_year, previous_year
        )
        previous_network_loaded = True
    except AssertionError:
        print(
            f"\n\nNOTE:\nThere does not seem to be a network for year={previous_year} at {path_to_networks}\n\n"
        )
        previous_network_loaded = False

    if previous_network_loaded and previous_network:
        # c ="Link","Transformer" etc,
        # attr=['p_nom', 's_nom', 'e_nom']
        for c, attr in nominal_attrs.items():
            # get Index of c  Link -['Lk37_(B3_BG-B_Hwa)', 'Lk80_(B3_Coal-B_Hwa)', ...]
            ext_i_current = current_network.get_extendable_i(c)
            ext_i_previous = previous_network.get_extendable_i(c)

            print("This year before setting to last")
            print(current_network.df(c).loc[ext_i_current, attr + "_min"])
            # set 'current_network': 'p|e|s_nom_min' to 'previous_network': 'p|e|s_nom_opt'

            # old adjustment
            # p_nom_miny = nom_opt_y_1
            current_network.df(c).loc[ext_i_current, attr + "_min"] = (
                previous_network.df(c).loc[ext_i_previous, attr + "_opt"]
            )

            # new adjustment
            # if not p_nom_max  -> use p_nom
            # if not p_nom_min  -> use 0
            # p_nom_miny = Min(p_nom_maxy,Max(p_nom_opty-1, p_nom_miny))

            # nom_max_y = current_network.df(c).loc[ext_i_current, attr + "_max"].iloc[0]
            # nom_min_y = current_network.df(c).loc[ext_i_current, attr + "_min"].iloc[0]

            # nom_opt_y_1 = (
            #     previous_network.df(c).loc[ext_i_previous, attr + "_opt"].iloc[0]
            # )

            #
            # current_network.df(c).loc[ext_i_current, attr + "_min"] = min(
            #     nom_max_y, max(nom_opt_y_1, nom_min_y)
            # )

            print("This year equal to last year")
            print(current_network.df(c).loc[ext_i_current, attr + "_min"])
            print("Last year")
            print(previous_network.df(c).loc[ext_i_previous, attr + "_opt"])

        # Set the list of index names in attr_zero_dict to 0
        # exeptions

        attr_zero_dict = {
            "Generator": get_list_from_dataframe_columns(
                current_network.generators, "do_not_fix"
            ),
            "Link": get_list_from_dataframe_columns(
                current_network.links, "do_not_fix"
            ),
            "Line": get_list_from_dataframe_columns(
                current_network.lines, "do_not_fix"
            ),
            "Store": get_list_from_dataframe_columns(
                current_network.stores, "do_not_fix"
            ),
            "StorageUnit": get_list_from_dataframe_columns(
                current_network.storage_units, "do_not_fix"
            ),
            "Transformer": [],  # add for completeness in iterations-->nominal_attrs
        }

        print("ZERO-DICT")
        print(attr_zero_dict)
        if attr_zero_dict:
            for c, attr in nominal_attrs.items():
                ext_i_current = current_network.get_extendable_i(c)
                list_to_limit = attr_zero_dict[c]
                ext_i_to_set = ext_i_current[ext_i_current.isin(list_to_limit)]
                current_network.df(c).loc[ext_i_to_set, attr + "_min"] = 0
                print(current_network.df(c).loc[ext_i_current, attr + "_min"])

    print("n-minus-1 capacities fixed")
    print("--------------------------\n\n")


def fix_links_capacity(network: pypsa.Network, m: linopy.model):
    # Link1 - for this link
    # Link2_- equate to link in col = 'link_relationship'
    print("\nfix_link_capacity")
    print("---------------------------")
    df: pd.DataFrame = network.links

    if "link_relationship" in df.columns:
        if not df["link_relationship"].isna().all():
            filtered_df: pd.DataFrame = df[
                df["link_relationship"].apply(
                    lambda x: isinstance(x, str) and len(str(x)) > 0
                )  # Ensure it's a string and not empty
                & df["link_relationship"].ne("0")  # Remove "0"
                & df["link_relationship"].notna()  # Remove NaN values
            ]

            # TODO ? we actualy need to test if right link is in fact in the list of left links?

            # get the links variable for p_nom
            link_capacity_var: linopy.Variable = m.variables["Link-p_nom"]

            # iterate through all the links with 'link_relationship' added and set constraint
            for index_link, right_link in filtered_df["link_relationship"].items():
                if index_link and right_link:  # check if the links exist

                    # now check extendable?
                    index_link_extendable: bool = df.loc[df.index == index_link][
                        "p_nom_extendable"
                    ].values[0]
                    right_link_extendable: bool = df.loc[right_link]["p_nom_extendable"]

                    # only add constraint if both is extendable
                    if index_link_extendable and right_link_extendable:
                        lhs: linopy.LinearExpression = (
                            link_capacity_var.loc[index_link]
                            - link_capacity_var.loc[right_link]
                        )
                        m.add_constraints(
                            lhs == 0, name=f"fix_{index_link}_{right_link}_capacity"
                        )
                        print(
                            f" - Added fix link capacity for |{index_link}| and |{right_link}|"
                        )
                    else:
                        # Both not extendable. Let user know.
                        print(
                            "Links Capacity - Links extendability criteria not met for:"
                        )
                        print(f"{index_link} extendable {index_link_extendable}")
                        print(f"{right_link} extendable {right_link_extendable}")
                else:
                    # MMMM .....
                    print("Whe should not reach here!s")
        else:
            print("link_relationship column is only NaN")
    else:
        print("'link_relationship' column not found in the Link definition.")
    print("---------------------------\n")


def fix_link_battery_capacity(network: pypsa.Network, m: linopy.model):
    print("\nfix_link_battery_capacity")
    print("---------------------------")
    link_battery_capacity_definitions = []
    storage_units = network.storage_units

    for i, storage_unit in enumerate(storage_units.itertuples(index=True)):
        if storage_unit.su_link_mw != None and type(storage_unit.su_link_mw) == str:
            link_battery_capacity_definitions.append(
                {
                    "name": f"Link-battery_{storage_unit.Index}",
                    "link_capacity_loc": storage_unit.su_link_mw,  # Left
                    "battery_capacity_loc": storage_unit.Index,  # Right
                }
            )
    print(link_battery_capacity_definitions)
    # link_battery_capacity_definitions = [
    #     {
    #         "name": "Link-battery_Pensulo",
    #         "link_capacity_loc": "Lk196_(B1_BES_Pen-B_Pensulo)",
    #         "battery_capacity_loc": "D-BES_Pen",
    #     },
    #     {
    #         "name": "Link-battery_Chi",
    #         "link_capacity_loc": "Lk197_(B1_BES_Chi-B_Chipata)",
    #         "battery_capacity_loc": "D-BES_Chi",
    #     },
    #     {
    #         "name": "Link-battery_Kit",
    #         "link_capacity_loc": "Lk198_(B1_BES_Kit-B_Kitwe)",
    #         "battery_capacity_loc": "D-BES_Kit",
    #     },
    #     {
    #         "name": "Link-battery_Kas",
    #         "link_capacity_loc": "Lk199_(B1_BES_Kas-B_Kasama)",
    #         "battery_capacity_loc": "D-BES_Kas",
    #     },
    #     {
    #         "name": "Link-battery_Lus",
    #         "link_capacity_loc": "Lk200_(B1_BES_Lus-B_Lusaka-W)",
    #         "battery_capacity_loc": "D-BES_Lus",
    #     },
    # ]

    try:
        link_capacity = m.variables["Link-p_nom"]
        battery_capacity = m.variables["StorageUnit-p_nom"]

        for bcd in link_battery_capacity_definitions:
            lhs = (
                link_capacity.loc[bcd["link_capacity_loc"]]
                - battery_capacity.loc[bcd["battery_capacity_loc"]]
            )
            m.add_constraints(lhs == 0, name=bcd["name"])
    except KeyError:
        print("Current year - does not have any StorageUnit / Battery definition.")
    print("---------------------------")


# def add_reserve_constraint_per_level_and_area(
#     m: linopy.model,
#     network: pypsa.Network,
#     reserve_level: str,
#     area_link_list: dict,
#     reserve_capacity_needed: float,
#     constraint_name: str,
# ):
#     """add a single reserve constraint, this is called by the constaints setup function and not used by user"""
#
#     # Dispatch variable
#     # All links are dispatched
#     Total_Dispatch = m.variables["Link-p"] * network.links[reserve_level]
#
#     Dispatch = Total_Dispatch.sel(Link=area_link_list["all_links"]).sum("Link")
#
#     # Scheduled extendable variable
#     # only extendable links is added
#     # Meet a reserve level in a area (extendable and non extandable ) total needs to meet the given reserve requirement
#     Total_Schedule_Extendable = (
#         m.variables["Link-p_nom"].sel(
#             {"Link-ext": area_link_list["extendable"]}
#         )  # Select all the extendable links
#         * network.links.loc[area_link_list["extendable"]][
#             reserve_level
#         ].to_list()  # Multiply each extendable link with its reserve level
#     )
#     Schedule_Extendable = (
#         Total_Schedule_Extendable.sum()
#     )  # Get the total extendable TODO - what type of var is this
#
#     # Scheduled non-extendable variable (scalar)
#     # scheduled non-extendable totel is the sum of all the p_nom * reserve_level
#     # contribution of each link to reserves
#     non_extantable_total_mw = sum(
#         area_link_list["non_extendable"]["p_nom"]
#         * network.links.loc[area_link_list["non_extendable"]["links"]][reserve_level]
#     )
#
#     # build constraint sentence
#     # check if there are links, but if the non extendable total is 0 don't bother
#     if (
#         len(area_link_list["non_extendable"]["links"]) > 0
#         and non_extantable_total_mw > 0
#     ):
#         # If extendable then build new capacity until you meet reserve requirement
#         print(
#             f"Total adjusted non extendable contrib to reserves {area_link_list['non_extendable']['links']}- {non_extantable_total_mw}"
#         )
#         Reserve_Constraint = (
#             Schedule_Extendable >= reserve_capacity_needed - non_extantable_total_mw
#         )
#     else:
#         Reserve_Constraint = Schedule_Extendable >= reserve_capacity_needed
#
#     # add the constraint to the linopy model
#     constraint = m.add_constraints(Reserve_Constraint, name=constraint_name)
#
#     print(f"{constraint}\n\n")
#
#
# def add_all_reserve_constraints(
#     network: pypsa.Network, m: linopy.model, reserves_file_path: str | Path
# ):
#     """find all constraints from links.csv, and loads reserves.csv witht the RHS from Inputsfolder
#
#     To set up, in the links.csv file:
#     1. add a column called "reserve_area" and add the reserve areas to this column e.g - reserve_area_1, WesternCape, Gauteng. These names will be used in 'reserves.csv'.
#     2. add columns called "reserve_level_1", "reserve_level_2", "reserve_level_n" and add the weightings e.g. 0.2, 0.3. These names will be used in 'reserves.csv'.
#
#     links.csv
#     reserve_area        reserve_level_1         reserve_level_2     .....
#     ============        ===============         ===============     =====
#     reserve_area_1      0.9                     0.1
#     WesternCape         0                       0.7
#     Gauteng             0.4                     0.2
#
#
#     3. Create a 'reserves.csv' file and use the 'reserve_area' and 'reserve_level' names to build the file and column 'level_area'
#     the level_area column should be 'reserve_level_name_reserve_area'. The 'value_mw' is the RHS of the constraint
#
#     reserves.csv
#     level_area                          value_mw
#     ------------------------------      --------
#     reserve_level_1_reserve_area_1      100
#     reserve_level_1_WesternCape         30
#     reserve_level_1_Gauteng             20
#
#     """
#
#     print("\n\nadd_all_reserve_constraints")
#     print("===============================")
#     # get all the network reserve areas defined in links.csv
#     reserve_areas = network.links["reserve_area"].dropna()
#     reserve_areas = reserve_areas[reserve_areas != 0]
#     reserve_areas = reserve_areas[reserve_areas != "0"]
#     reserve_areas = reserve_areas.unique()
#
#     if reserve_areas == [0]:
#         reserve_areas = []
#
#     reserve_areas = [
#         area for area in reserve_areas if "reserve_area" in area
#     ]  # remove areas that does not contain "reserve area"
#     print(f"Found the following areas: {reserve_areas}\n")
#
#     # get the reserve level
#     reserve_levels = [col for col in network.links.columns if "reserve_level_" in col]
#     print(f"Found reserve levels: {reserve_levels}\n")
#
#     # find the links per area
#     # split the dict up into "extendable" and "non-extendable"
#     # {'reserve_area_1':
#     #   {
#     #   'non_extendable':
#     #       {
#     #        'links':
#     #                ['Lk10_(B2-B1)', ...],
#     #        'p_nom':
#     #                [1500.0, ...]
#     #       },
#     #   'all_links':
#     #               ['Lk10_(B2-B1)', 'Lk11_(B2-B1)', 'Lk12_(B2-B1)'],
#     #   'extendable':
#     #               ['Lk11_(B2-B1)', 'Lk12_(B2-B1)']}
#     # }
#     area_to_links_lookup = {}
#     for reserve_area in reserve_areas:
#         area_to_links_lookup[reserve_area] = {}
#         area_to_links_lookup[reserve_area]["non_extendable"] = {}
#         area_to_links_lookup[reserve_area]["all_links"] = []
#         links = network.links
#         area_to_links_lookup[reserve_area]["all_links"] = links[
#             (links["reserve_area"] == reserve_area)
#         ].index.to_list()
#         area_to_links_lookup[reserve_area]["extendable"] = links[
#             (links["reserve_area"] == reserve_area)
#             & (links["p_nom_extendable"] == True)
#         ].index.to_list()
#         area_to_links_lookup[reserve_area]["non_extendable"]["links"] = links[
#             (links["reserve_area"] == reserve_area)
#             & (links["p_nom_extendable"] == False)
#         ].index.to_list()
#         area_to_links_lookup[reserve_area]["non_extendable"]["p_nom"] = links[
#             (links["reserve_area"] == reserve_area)
#             & (links["p_nom_extendable"] == False)
#         ].p_nom.to_list()
#     print("The areas are associated  with the links:")
#     pprint(area_to_links_lookup)
#     print("\n")
#
#     # read reserves RHS
#     reserves = pd.read_csv(reserves_file_path, index_col=0)
#     print(f"Reading RHS file from: {reserves_file_path}\n")
#     print("Found RHS reserve constraints:")
#     print(f"{reserves}\n")
#
#     ignored_constraints = []
#
#     # add constraints found
#     for reserve_level in reserve_levels:
#         for reserve_area in reserve_areas:
#             reserve_level_reserve_area = f"{reserve_level}_{reserve_area}"
#             area_link_list = area_to_links_lookup[reserve_area]
#
#             try:
#                 reserve_capacity_needed = reserves.at[
#                     reserve_level_reserve_area, "value_mw"
#                 ]
#                 constraint_name = f"Reserve_Constraint_{reserve_level_reserve_area}_{reserve_capacity_needed}"
#                 print(
#                     f"Adding: {constraint_name}-{area_link_list} >= {reserve_capacity_needed}\n\n"
#                 )
#                 print("=" * 80)
#                 add_reserve_constraint_per_level_and_area(
#                     m,
#                     network,
#                     reserve_level,
#                     area_link_list,
#                     reserve_capacity_needed,
#                     constraint_name,
#                 )
#             except KeyError:
#                 print(
#                     f"{reserve_level} and {reserve_area} was not found in reserves.csv file. Skipping. Please check.\n"
#                 )
#                 ignored_constraints.append(reserve_level_reserve_area)
#
#     print("Final Linopy Model for optimization:")
#     print("Call: network.optimize.solve_model()")
#     print("============================================================")
#     print("The following constraints have been ADDED to the model:")
#     added_constraints = [c for c in m.constraints if "Reserve_Constraint_" in c]
#     for i, constraint in enumerate(added_constraints):
#         print(f"{i} ✅ -- {constraint}")
#     print("============================================================")
#     print("The following constraints have been SKIPPED:")
#     for i, constraint in enumerate(ignored_constraints):
#         print(f"{i} ❌ -- {constraint}")
#     print("============================================================\n\n")


def add_min_stable_gen(network: pypsa.Network, m):
    """
    Inputs
    -------
        link_stable_gen     link_name check for pressence
        mingen_coefficient  0<=x<=1 check for pressence

    were for var_link_p(at link) >= 0:                # var_p.select( p>0]   [1,1,1,1,0,1,1,1,1,1], [.,.,.,.,.,1,.....] / [1111111.111]
        the if  for var_link_p(at link) >= Constant:
            do_nothing
        else constraint:
            for var_link_p(at link) == 0

            var_link_stable_gen[at==link_stable_gen] >= stable_link_p_nom[at link_stable_gen] * mingen_coefficient[at link_stable_gen]

    """


def check_none_gte_0(val_to_check):
    return (
        abs(val_to_check) > 0 and abs(val_to_check) != None and abs(val_to_check) != 0
    )


def add_hydro_turnine_efficiency(network: pypsa.Network, m):
    hydro_turnine_efficiency_definition = []
    links = network.links
    print("\n\nHydro efficiency - stores")
    print("-------------------------")

    flow_link_present = "flow_link" in links.columns
    store_eff_present = "store_eff" in links.columns

    if flow_link_present and store_eff_present:  # both columns needs to be present
        for i, link in enumerate(links.itertuples(index=True)):
            if (link.flow_link != 0 and link.flow_link != "0") and (
                link.store_eff != 0 and link.store_eff != "0"
            ):
                print(f"!!{i} -- {link.flow_link}")
                print(f"!!{i} -- {link.store_eff}")
                hydro_turnine_efficiency_definition.append(
                    {
                        "name": f"Turbine{i}_eff",
                        "loss_link": link.Index,  # name of Link where we are
                        "flow_link": link.flow_link,
                        "store": link.store_eff,
                    }
                )

        print(hydro_turnine_efficiency_definition)
        print("-------------------------\n\n")

        for i, hte in enumerate(hydro_turnine_efficiency_definition):
            name = hte["name"]
            loss_link = hte["loss_link"]
            flow_link = hte["flow_link"]
            store = hte["store"]

            # variable
            # Select spesific Link, Store and Generators from the network.model.variables
            var_loss_link_p = m.variables["Link-p"].sel(Link=loss_link)
            var_flow_link_p = m.variables["Link-p"].sel(Link=flow_link)
            var_store_e = m.variables["Store-e"].sel(Store=store)  # This is store

            # Variable set in the Link file
            store_coefficient = network.links.at[
                loss_link, "store_coefficient"  # 'store_min_p'
            ]
            flow_coefficient = network.links.at[
                loss_link, "flow_coefficient"
            ]  # 'store_min_p'
            store_constant = network.links.at[
                loss_link, "store_constant"
            ]  # 'store_min_p'

            # Pyps set values in Stores file
            # store_e_min_pu = network.stores.at[store, "e_min_pu"]  # 'store_min_p'
            store_e_nom = network.stores.at[store, "e_nom"]
            flow_link_p_nom = network.links.at[flow_link, "p_nom"]
            loss_link_p_nom = network.links.at[loss_link, "p_nom"]

            #
            term1 = var_store_e / store_e_nom
            term2 = var_flow_link_p / flow_link_p_nom

            rhs = (
                store_coefficient * term1 + (flow_coefficient * term2) + store_constant
            )

            constraint = var_loss_link_p <= rhs

            m.add_constraints(constraint, name=name)

            print("*********************************************")
            print("Reference setup")
            print(f"loss_link:              {loss_link:<20}")
            print(f"flow_link:              {flow_link:<20}")
            print(f"store:                  {store:<20}")
            print("--------------------------------------------")
            print("Constants")
            print(f"store_coefficient:      {store_coefficient:<20}")
            print(f"flow_coefficient:       {flow_coefficient:<20}")
            print(f"store_constant:         {store_constant:<20}")
            print(f"flow_link_p_nom:        {flow_link_p_nom:<20}")
            print(f"loss_link_p_nom:        {loss_link_p_nom:<20}")
            print(f"store_e_nom:            {store_e_nom:<20}")
            print(
                f"Constraint string: var_loss_link_p >= = [store_coefficient * term1 + (flow_coefficient * term2) + store_constant]"
            )
            print("*********************************************")
    else:
        print(
            f"flow_link present: {flow_link_present} or store_eff presnt {store_eff_present} not both true, skipping - add_hydro_turnine_efficiency"
        )


def load_network_at_year(path_to_networks: Path | str, current_year, previous_year):
    """
    Load a network at the path 'path_to_networks' for  'year'
    """
    n = pypsa.Network()
    n.import_from_csv_folder(
        Path(path_to_networks.replace(str(current_year), str(previous_year)))
    )
    return n


def print_study_start_info(child_inputs_folder, child_results_folder):
    print("\n\n\n\n****************************************")
    print("The first run started at : ", time.strftime("%H:%M:%S"))
    print("****************************************")
    print(child_inputs_folder)
    print(child_results_folder)
    print("")
    print(pypsa.__version__)
    print("****************************************\n")


def get_scenarios_paths(
    yr, scenario_folder, child_inputs_folder="Inputs", child_results_folder="Results_uc"
):
    main_folder = ""
    year_folder = yr

    current_folder = os.getcwd()

    print("\n\n\n**************************")
    print("Next run started at : ", time.strftime("%H:%M:%S"))
    print("Scenario Name: ", scenario_folder)
    print("Year : ", year_folder)
    print(f"Inputs: {child_inputs_folder}")
    print(f"Outputs: {child_results_folder}")
    print("**************************\n\n")
    # base_case_folder = os.path.join(current_folder, main_folder, scenario_folder)
    inputs_folder_name = os.path.join(
        current_folder, main_folder, scenario_folder, year_folder, child_inputs_folder
    )

    print(inputs_folder_name)

    results_folder_name = os.path.join(
        current_folder, main_folder, scenario_folder, year_folder, child_results_folder
    )
    if not os.path.exists(results_folder_name):
        os.makedirs(results_folder_name)

    # Start of Morne's Code
    folder_path = results_folder_name

    def open_csv_with_user_retry(file_path, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                with open(file_path, "a") as csv_file:
                    csv_file = csv_file
                return  # Success, exit the function
            except PermissionError:
                retries += 1
                if retries < max_retries:
                    winsound.Beep(2000, 500)
                    winsound.Beep(2000, 500)
                    print(
                        f"Permission error for {file_path}. Please close the file and press Enter to retry."
                    )
                    input()  # Wait for user input before retrying

        print(f"Failed to open {file_path} after {max_retries} retries.")

    # List all files in the folder

    if not (os.path.exists(folder_path)):
        print("Results folder does not exist")
    if os.path.exists(folder_path):
        file_list = os.listdir(folder_path)

        # Iterate through the files and try to open CSV files
        for filename in file_list:
            if filename.endswith(".csv"):
                file_path = os.path.join(folder_path, filename)
                open_csv_with_user_retry(file_path)

    return inputs_folder_name, results_folder_name


def set_cplex_licence_key():
    import os

    print("Setting CPLEX Licence Key")
    os.environ["CPLEX_STUDIO_KEY"] = "api_cos_2afedf42-44b3-4191-8fe2-72cc77d4cfb6"


def load_and_prepare_network(inputs_folder_name, add_multi_index=True):
    network = pypsa.Network()
    network.import_from_csv_folder(inputs_folder_name)
    if add_multi_index:
        add_multi_index_investment_periods(network)
    return network


def network_statistics_output(
    network: pypsa.Network, grouper: str | list[str], output_folder: Path
) -> None:

    p = "z_"
    grouper_list = []
    if isinstance(grouper, str):
        grouper_list = [grouper]
    else:
        grouper_list = grouper

    if len(grouper_list) == 0:
        grouper_list = ["carrier"]

    try:
        z_stats = network.statistics()
        print("In network statistics")
        print("---------------------")
        z_stats["ave_cost"] = (
            z_stats["Capital Expenditure"] + z_stats["Operational Expenditure"]
        ) / z_stats["Transmission"]
        z_stats.to_csv(output_folder / f"{p}statistics.csv")
    except:
        network.statistics().to_csv(output_folder / f"{p}statistics.csv")

    installed_capex: pd.DataFrame = network.statistics.installed_capex(
        groupby=grouper_list
    )
    installed_capex.to_csv(output_folder / f"{p}installed_capex.csv")

    expanded_capex: pd.DataFrame = network.statistics.expanded_capex(
        groupby=grouper_list
    )
    expanded_capex.to_csv(output_folder / f"{p}expanded_capex.csv")

    optimal_capacity: pd.DataFrame = network.statistics.optimal_capacity(
        groupby=grouper_list
    )
    optimal_capacity.to_csv(output_folder / f"{p}optimal_capacity.csv")

    installed_capacity: pd.DataFrame = network.statistics.installed_capacity(
        groupby=grouper_list
    )
    installed_capacity.to_csv(output_folder / f"{p}installed_capacity.csv")

    expanded_capacity: pd.DataFrame = network.statistics.expanded_capacity(
        groupby=grouper_list
    )
    expanded_capacity.to_csv(output_folder / f"{p}expanded_capacity.csv")


def save_outputs(network, scenario_folder, year, results_folder_name):
    if True:
        print("****************************************")
        print("Last run completed: ", scenario_folder)
        print("Last run ended at : ", time.strftime("%H:%M:%S"))
        print("Year completed: ", year)
        print("****************************************")
        print("")
        winsound.Beep(1000, 1000)
        network.export_to_csv_folder(results_folder_name)

        network_statistics_output(network, "carrier", Path(results_folder_name))
        # try:
        #     print("In network statisics")
        #     z_stats = network.statistics()
        #     print("In network statistics")
        #     print("---------------------")
        #     print(z_stats)
        #     print(z_stats.columns)
        #     print(dir(z_stats))
        #     print("---------------------")
        #     z_stats["ave_cost"] = (
        #         z_stats["Capital Expenditure"] + z_stats["Operational Expenditure"]
        #     ) / z_stats["Transmission"]
        #     z_stats.to_csv(results_folder_name + "//z_statistics.csv")
        # except:
        #     network.statistics().to_csv(results_folder_name + "//z_statistics.csv")


def remove_proxy_plant(n: pypsa.Network) -> None:
    """
    This function modifies the 'links' DataFrame in the given pypsa.Network object by setting specific
    columns to predefined values wherever the 'proxy_flag' column is equal to 1.

    Parameters:
    n (pypsa.Network): The network object containing the links DataFrame.

    The function performs the following actions:
    - If the 'proxy_flag' column is not present in the links DataFrame, it prints a message.
    - If the 'proxy_flag' column is present, it sets the 'p_nom_max' and 'p_nom' columns to 0 and
      the 'p_nom_extendable' column to False for all rows where 'proxy_flag' is equal to 1.

    Returns:
    None
    """
    try:
        # Check if the 'proxy_flag' column exists in n.links DataFrame
        if "proxy_flag" not in n.links.columns:
            print(
                "[INFO] - The 'proxy_flag' column is not present in the links dataframe."
            )
        else:
            # Apply the changes where 'proxy_flag' is equal to 1
            # Set 'p_nom_max' and 'p_nom' to 0 and 'p_nom_extendable' to False
            n.links.loc[
                n.links["proxy_flag"] == 1, ["p_nom_max", "p_nom", "p_nom_extendable"]
            ] = [0, 0, False]
            print("[INFO] - Proxy plant has been removed.")

    except:
        print(
            "[ERROR] - There was an error in the 'remove_proxy_plant' function, when running the incremental case.\n"
            "        - This would have no impact on the solver, except that the proxy plant would not have been removed from the case.\n"
        )


def silence_warnings():
    import logging

    # Disable all logging
    logging.basicConfig(level=100)
    warnings.filterwarnings("ignore", module="pypsa")
    warnings.filterwarnings(
        "ignore", message="Could not infer format", category=UserWarning
    )
    warnings.filterwarnings(
        "ignore", message="are not in main components dataframe", category=UserWarning
    )
    warnings.simplefilter(action="ignore", category=FutureWarning)


def copy_file(from_dir, to_dir, filename):
    """
    Copies a file from one directory to another.

    Parameters:
    - from_dir: The directory to copy the file from.
    - to_dir: The directory to copy the file to.
    - filename: The name of the file to copy.
    """
    # Build the full path of the source and destination files
    src_file_path = os.path.join(from_dir, filename)
    dest_file_path = os.path.join(to_dir, filename)

    # Check if the source file exists
    if not os.path.exists(src_file_path):
        print(f"The file {filename} does not exist in {from_dir}")
        return

    # Copy the file
    shutil.copy2(src_file_path, dest_file_path)
    print(f"\n\nFile {filename} copied from {from_dir} to {to_dir}\n\n")


def print_cplex_options():
    """A helper function to print all the cplex option
    Parameter                                           Value
    =========                                           =====
    advance                                             1
    barrier.algorithm                                   0
    barrier.colnonzeros                                 0
    barrier.convergetol                                 1e-08
    barrier.crossover                                   0
    barrier.display                                     1
    barrier.limits.corrections                          -1
    barrier.limits.growth                               1000000000000.0
    barrier.limits.iteration                            9223372036800000000
    barrier.limits.objrange                             1e+20
    barrier.ordering                                    0
    barrier.qcpconvergetol                              1e-07
    barrier.startalg                                    1
    benders.strategy                                    0
    benders.tolerances.feasibilitycut                   1e-06
    benders.tolerances.optimalitycut                    1e-06
    benders.workeralgorithm                             0
    clocktype                                           2
    conflict.algorithm                                  0
    conflict.display                                    1
    cpumask                                             auto
    dettimelimit                                        1e+75
    emphasis.memory                                     0
    emphasis.mip                                        0
    emphasis.numerical                                  0
    feasopt.mode                                        0
    feasopt.tolerance                                   1e-06
    lpmethod                                            0
    mip.cuts.bqp                                        0
    mip.cuts.cliques                                    0
    mip.cuts.covers                                     0
    mip.cuts.disjunctive                                0
    mip.cuts.flowcovers                                 0
    mip.cuts.gomory                                     0
    mip.cuts.gubcovers                                  0
    mip.cuts.implied                                    0
    mip.cuts.liftproj                                   0
    mip.cuts.localimplied                               0
    mip.cuts.mcfcut                                     0
    mip.cuts.mircut                                     0
    mip.cuts.nodecuts                                   0
    mip.cuts.pathcut                                    0
    mip.cuts.rlt                                        0
    mip.cuts.zerohalfcut                                0
    mip.display                                         2
    mip.interval                                        0
    mip.limits.aggforcut                                3
    mip.limits.auxrootthreads                           0
    mip.limits.cutpasses                                0
    mip.limits.cutsfactor                               -1.0
    mip.limits.eachcutlimit                             2100000000
    mip.limits.gomorycand                               200
    mip.limits.gomorypass                               0
    mip.limits.lowerobjstop                             -1e+75
    mip.limits.nodes                                    9223372036800000000
    mip.limits.populate                                 20
    mip.limits.probedettime                             1e+75
    mip.limits.probetime                                1e+75
    mip.limits.repairtries                              0
    mip.limits.solutions                                9223372036800000000
    mip.limits.strongcand                               10
    mip.limits.strongit                                 0
    mip.limits.treememory                               1e+75
    mip.limits.upperobjstop                             1e+75
    mip.ordertype                                       0
    mip.polishafter.absmipgap                           0.0
    mip.polishafter.dettime                             1e+75
    mip.polishafter.mipgap                              0.0
    mip.polishafter.nodes                               9223372036800000000
    mip.polishafter.solutions                           9223372036800000000
    mip.polishafter.time                                1e+75
    mip.pool.absgap                                     1e+75
    mip.pool.capacity                                   2100000000
    mip.pool.intensity                                  0
    mip.pool.relgap                                     1e+75
    mip.pool.replace                                    0
    mip.strategy.backtrack                              0.9999
    mip.strategy.bbinterval                             7
    mip.strategy.branch                                 0
    mip.strategy.dive                                   0
    mip.strategy.file                                   1
    mip.strategy.fpheur                                 0
    mip.strategy.heuristiceffort                        1.0
    mip.strategy.heuristicfreq                          0
    mip.strategy.kappastats                             0
    mip.strategy.lbheur                                 0
    mip.strategy.miqcpstrat                             0
    mip.strategy.nodeselect                             1
    mip.strategy.order                                  1
    mip.strategy.presolvenode                           0
    mip.strategy.probe                                  0
    mip.strategy.rinsheur                               0
    mip.strategy.search                                 0
    mip.strategy.startalgorithm                         0
    mip.strategy.subalgorithm                           0
    mip.strategy.variableselect                         0
    mip.submip.startalg                                 0
    mip.submip.subalg                                   0
    mip.submip.nodelimit                                500
    mip.submip.scale                                    0
    mip.tolerances.absmipgap                            1e-06
    mip.tolerances.linearization                        0.001
    mip.tolerances.integrality                          1e-05
    mip.tolerances.lowercutoff                          -1e+75
    mip.tolerances.mipgap                               0.0001
    mip.tolerances.objdifference                        0.0
    mip.tolerances.relobjdifference                     0.0
    mip.tolerances.uppercutoff                          1e+75
    multiobjective.display                              1
    network.display                                     2
    network.iterations                                  9223372036800000000
    network.netfind                                     2
    network.pricing                                     0
    network.tolerances.feasibility                      1e-06
    network.tolerances.optimality                       1e-06
    optimalitytarget                                    0
    output.clonelog                                     0
    output.intsolfileprefix
    output.mpslong                                      1
    output.writelevel                                   0
    parallel                                            0
    paramdisplay                                        1
    preprocessing.aggregator                            -1
    preprocessing.boundstrength                         -1
    preprocessing.coeffreduce                           -1
    preprocessing.dependency                            -1
    preprocessing.dual                                  0
    preprocessing.fill                                  10
    preprocessing.folding                               -1
    preprocessing.linear                                1
    preprocessing.numpass                               -1
    preprocessing.presolve                              1
    preprocessing.qcpduals                              1
    preprocessing.qpmakepsd                             1
    preprocessing.qtolin                                -1
    preprocessing.reduce                                3
    preprocessing.reformulations                        3
    preprocessing.relax                                 -1
    preprocessing.repeatpresolve                        -1
    preprocessing.sos1reform                            0
    preprocessing.sos2reform                            0
    preprocessing.symmetry                              -1
    qpmethod                                            0
    randomseed                                          202009243
    read.constraints                                    30000
    read.datacheck                                      1
    read.fileencoding                                   ISO-8859-1
    read.nonzeros                                       250000
    read.qpnonzeros                                     5000
    read.scale                                          0
    read.variables                                      60000
    read.warninglimit                                   10
    record                                              0
    sifting.algorithm                                   0
    sifting.simplex                                     1
    sifting.display                                     1
    sifting.iterations                                  9223372036800000000
    simplex.crash                                       1
    simplex.dgradient                                   0
    simplex.display                                     1
    simplex.dynamicrows                                 -1
    simplex.limits.iterations                           9223372036800000000
    simplex.limits.lowerobj                             -1e+75
    simplex.limits.perturbation                         0
    simplex.limits.singularity                          10
    simplex.limits.upperobj                             1e+75
    simplex.perturbation.constant                       1e-06
    simplex.perturbation.indicator                      0
    simplex.pgradient                                   0
    simplex.pricing                                     0
    simplex.refactor                                    0
    simplex.tolerances.feasibility                      1e-06
    simplex.tolerances.markowitz                        0.01
    simplex.tolerances.optimality                       1e-06
    solutiontype                                        0
    threads                                             0
    timelimit                                           1e+75
    tune.dettimelimit                                   1e+75
    tune.display                                        1
    tune.measure                                        1
    tune.repeat                                         1
    tune.timelimit                                      1e+75
    workdir                                             .
    workmem                                             2048.0
    """
    try:
        import cplex

        empty_problem = cplex.Cplex()
        parameters = empty_problem.parameters.get_all()

        print(f"{'Parameter':<50}  Value")
        print(f"{'=========':<50}  =====")
        for p in parameters:
            print(f"{str(p[0]).replace('parameters.',''):<50}  {p[1]}")

    except:
        print("CPLEX solver is not installed.")


def run_unconstrained_expansion(
    scenario_folder,
    years,
    child_inputs_folder="Inputs",
    child_results_folder="Results_uc",
    use_lpmethod_4=True,
):
    print_study_start_info(child_inputs_folder, child_results_folder)

    for year in years:
        inputs_folder_name, results_folder_name = get_scenarios_paths(
            year,
            scenario_folder,
            child_inputs_folder=child_inputs_folder,
            child_results_folder=child_results_folder,
        )

        network = load_and_prepare_network(inputs_folder_name, add_multi_index=True)

        m = network.optimize.create_model(multi_investment_periods=True)
        add_hydro_turnine_efficiency(network, m)
        fix_link_battery_capacity(network, m)
        fix_links_capacity(network, m)
        add_all_reserve_constraints(network, m, inputs_folder_name + r"\reserves.csv")

        if use_lpmethod_4:
            cplex_option = {"lpmethod": 4}  # no crossover
        else:
            cplex_option = {}

        network.optimize.solve_model(solver_name="cplex", solver_options=cplex_option)

        add_summaries(network)

        save_outputs(network, scenario_folder, year, results_folder_name)

        copy_file(inputs_folder_name, results_folder_name, "reserves.csv")
        copy_file(inputs_folder_name, results_folder_name, "inc_load.csv")

    return network


def run_optimum_expansion(
    scenario_folder,
    years,
    child_inputs_folder="Results_uc",
    child_results_folder="Results_opt",
    use_lpmethod_4=True,
):
    print_study_start_info(child_inputs_folder, child_results_folder)

    for year in years:
        inputs_folder_name, results_folder_name = get_scenarios_paths(
            year,
            scenario_folder,
            child_inputs_folder=child_inputs_folder,
            child_results_folder=child_results_folder,
        )

        network = load_and_prepare_network(inputs_folder_name, add_multi_index=True)

        fix_n_minus_capacities(
            path_to_networks=results_folder_name,
            current_network=network,
            current_year=year,
        )

        m = network.optimize.create_model(multi_investment_periods=True)
        add_hydro_turnine_efficiency(network, m)
        fix_link_battery_capacity(network, m)
        fix_links_capacity(network, m)
        add_all_reserve_constraints(network, m, inputs_folder_name + r"\reserves.csv")

        if use_lpmethod_4:
            cplex_option = {"lpmethod": 4}  # no crossover
        else:
            cplex_option = {}

        network.optimize.solve_model(solver_name="cplex", solver_options=cplex_option)

        add_summaries(network)

        save_outputs(network, scenario_folder, year, results_folder_name)

        copy_file(inputs_folder_name, results_folder_name, "reserves.csv")
        copy_file(inputs_folder_name, results_folder_name, "inc_load.csv")

    return network


def run_incremental_demand_expansion(
    scenario_folder,
    years,
    child_inputs_folder="Results_opt",
    child_results_folder="Results_opti",
    use_lpmethod_4=True,
):
    print_study_start_info(child_inputs_folder, child_results_folder)

    for year in years:
        inputs_folder_name, results_folder_name = get_scenarios_paths(
            year,
            scenario_folder,
            child_inputs_folder=child_inputs_folder,
            child_results_folder=child_results_folder,
        )

        network = load_and_prepare_network(inputs_folder_name, add_multi_index=True)

        # make extentable
        make_all_non_extendable(network)

        make_extendable(network)
        increase_load_fixed(network, inputs_folder_name)

        # remove all proxy plants (3/7/2024)
        remove_proxy_plant(network)

        m = network.optimize.create_model(multi_investment_periods=True)
        add_hydro_turnine_efficiency(network, m)
        fix_link_battery_capacity(network, m)
        fix_links_capacity(network, m)

        add_all_reserve_constraints(network, m, inputs_folder_name + r"\reserves.csv")

        if use_lpmethod_4:
            cplex_option = {"lpmethod": 4}  # no crossover
        else:
            cplex_option = {}

        network.optimize.solve_model(solver_name="cplex", solver_options=cplex_option)

        add_summaries(network)

        save_outputs(network, scenario_folder, year, results_folder_name)

        copy_file(inputs_folder_name, results_folder_name, "reserves.csv")
        copy_file(inputs_folder_name, results_folder_name, "inc_load.csv")

    return network


def generate_case_report(
    case_name,
    path_to_excel_settings,
    input_dir,
    results_dir,
    reports_to_run=["ALL"],
    link_plot_color=None,
    currency_str="$/MWh",
    **kwargs,
):
    print(f"[ PACKAGE VERSION ] - {__version__}")
    r = Report(
        case_name=case_name,
        base_directory=input_dir,
        path_to_excel_settings=path_to_excel_settings,
        input_dir=results_dir,  # e.h. path to "Input_uc"
    )
    r._case_name = case_name

    if link_plot_color:
        print(
            f"Changing link plot color from {r.settings.link_profiles.scatter.color} to {link_plot_color}"
        )
        r.settings.link_profiles.scatter.color = link_plot_color
        r.settings.link_profiles.ldc.color = link_plot_color
        r.settings.link_profiles.average.color = link_plot_color

    print(r)

    link_df = r.settings.xlxs_settings.link_profiles

    if "ALL" in reports_to_run or "CAPACITY_ENERGY" in reports_to_run:
        remove_non_directory_files(r.case_output_directory())
        r.show_capacity_plot()
        r.show_energy_plot()
        #
        r.generate_load_factor_plot()
        #
        r.show_capacity_delta_plot()
        r.show_energy_delta_plot()

        #
        # marc
        # average dispatch graphs mark
        try:
            for year in r.study_years:
                print(f"Doing Dispatch {year}")
                # get the network for the study year above
                r.show_average_dispatch_energy_plot(year, currency_str=currency_str)
        except Exception as e:
            print(
                f"An error has occured during the function show_average_dispatch_energy_plot. {e}"
            )

        # LDF curves marc
        try:
            r.show_marginal_price_durtion_curve_plot(
                currency_str=currency_str, **kwargs
            )
        except Exception as e:
            print(
                f"An error has occured during the function show_marginal_price_durtion_curve_plot. {e}"
            )

    if "ALL" in reports_to_run or "LINK_PROFILES" in reports_to_run:
        # clear the directory of years
        years_in_dir = find_int_named_subdirs(r.case_output_directory())
        for year_to_remove in years_in_dir:
            print(f"Removing {r.case_output_directory() / Path(str(year_to_remove))}")
            shutil.rmtree(r.case_output_directory() / Path(str(year_to_remove)))

        # run the study Maree
        for year in r.study_years:
            # get the network for the study year above
            network = r.get_network_at_year(year)

            # Link profiles (Maree x 3)
            for row in link_df.iterrows():
                try:
                    link_profiles_left_bus = row[1]["left_link"]
                    link_profiles_right_bus = row[1]["right_link"]
                    left_name = row[1]["left_link_title"]
                    right_name = row[1]["right_link_title"]

                    r.show_link_profiles_scatter_plot(
                        network,
                        year,
                        link_profiles_left_bus,
                        link_profiles_right_bus,
                        left_name,
                        right_name,
                    )

                    r.show_link_profiles_ldc_plot(
                        network,
                        year,
                        link_profiles_left_bus,
                        link_profiles_right_bus,
                        left_name,
                        right_name,
                    )
                    r.show_link_profiles_average_plot(
                        network,
                        year,
                        link_profiles_left_bus,
                        link_profiles_right_bus,
                        left_name,
                        right_name,
                    )
                except Exception as e:
                    print(
                        f"Profile plot error for {year}, {link_profiles_left_bus}, {link_profiles_right_bus}, {e}"
                    )
