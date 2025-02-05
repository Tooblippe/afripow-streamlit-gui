from pathlib import Path

import streamlit as st

from pages.helpers.helpers import load_file


def fetch_excess_energy_parameters(settings_file: Path) -> dict:
    df = load_file(settings_file, "excess_energy")
    excess_generator = df["generator"].dropna().to_list()
    excess_energy_link_name = df["link"].dropna().to_list()
    excess_energy_prices = df["price"].dropna().to_list()
    excess_energy_link_pnom_max = df["link_pnom_max"].dropna().to_list()
    return {
        "excess_generator": excess_generator,
        "excess_energy_link_name": excess_energy_link_name,
        "excess_energy_link_pnom_max": excess_energy_link_pnom_max,
        "excess_energy_prices": excess_energy_prices,
    }


def excess_energy_optimisation(
    scenario_folder,
    years,
    child_inputs_folder="Results_uc",
    child_results_folder="Results_opt",
    use_lpmethod_4=True,
    setttings_file=None,
):

    st.write(fetch_excess_energy_parameters(Path(setttings_file)))
