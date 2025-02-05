import matplotlib.figure
from matplotlib import pyplot as plt
import matplotlib.ticker as tkr


# -------------------------------------------------------------------------------------
# Function to format number with thousands separator
def format_with_commas(value, tick_number):
    return (f"{value:,.0f}"  # Change '.0f' to ',.2f' if you want two decimal places, etc.
    )


def format_zero_to_one(value, tick_number):
    return (f"{value:,.02f}"  # Change '.0f' to ',.2f' if you want two decimal places, etc.
            )


def study_stacked_bar_graph(fig: matplotlib.figure.Figure, ax, title: str, xlabel: str, custom_formatter=None) -> None:
    """Just do operations on the current graph"""

    plt.title(title, fontsize="x-large", pad=20)
    plt.ylabel(xlabel, fontsize="x-large")
    plt.xticks(rotation=90, fontsize="x-large")
    plt.yticks(fontsize="x-large")

    # Put a legend below current axis
    plt.subplots_adjust(bottom=0.30)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), frameon=False, shadow=True, ncol=4, fontsize="large", )

    # add comma
    # Create a formatter object using the custom function
    formatter = tkr.FuncFormatter(format_with_commas)

    # Apply the formatter to the y-axis (you could apply it to the x-axis with ax.xaxis.set_major_formatter)
    if custom_formatter:
        ax.yaxis.set_major_formatter(custom_formatter)
    else:
        ax.yaxis.set_major_formatter(formatter)

    fig.tight_layout()
