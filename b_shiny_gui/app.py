from shiny import App, render, ui
from palmerpenguins import load_penguins
import pandas as pd
import shinyswatch

from palmerpenguins import load_penguins

penguins = load_penguins()
selectors = penguins.columns.to_list()


def AppSideBar():
    btn_reset = (ui.input_action_button("reset", "Solver"),)
    btn_report = (ui.input_action_button("reset", "Reporting"),)
    return ui.sidebar(btn_reset, btn_report)


app_ui = ui.page_fluid(
    # AppSideBar(),
    ui.input_selectize("select", label="what", choices=selectors),
    ui.output_data_frame("penguins_df"),
    ui.output_plot("plot_penguins_df"),
)


def server(input, output, session):
    @render.data_frame
    def penguins_df():
        return render.DataTable(penguins[[input.select()]], height="300px")

    @render.plot
    def plot_penguins_df():
        return penguins[[input.select()]].plot()


app = App(app_ui, server)
