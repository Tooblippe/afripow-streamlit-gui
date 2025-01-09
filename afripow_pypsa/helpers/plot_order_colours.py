import pandas as pd


def get_plot_order_colours(
    settings: dict, available_plant_check_list: list = None
) -> type[list, list]:
    plot_setings_from_excel = pd.DataFrame(settings.xlxs_settings["link_to_plant"])

    # remove unwanted busses
    # column "include_in_profile" myst be 1
    plot_setings_from_excel = plot_setings_from_excel.loc[
        plot_setings_from_excel["include_in_dispatch_profile"] > 0
    ]

    # extract plot order
    plot_order = (
        plot_setings_from_excel.sort_values(by="plot_order")["plant_group"]
        .unique()
        .tolist()
    )

    plot_colors = []
    # iterate through groupings in order
    for plant_group_item in plot_order:
        color = plot_setings_from_excel.loc[
            plot_setings_from_excel["plant_group"] == plant_group_item
        ]["plot_color"].tolist()[0]

        # if a list of plants is specified only add them to the colours
        # this makes itr possible to obly load colours that is needed
        # print(f"checking {plant_group_item}")
        if available_plant_check_list:
            if plant_group_item in available_plant_check_list:
                plot_colors.append(color)
        else:
            plot_colors.append(color)

    return plot_order, plot_colors
