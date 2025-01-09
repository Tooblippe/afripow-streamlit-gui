import numpy as np
import pandas as pd


def get_24hour_ricks(df: pd.DataFrame) -> np.array:
    """adds hours 1 to 24 for each of the 8760 values"""
    return (np.arange(len(df)) % 24) + 1


# Function to format number with thousands separator
def format_with_commas(value, tick_number):
    return (
        f"{value:,.0f}"  # Change '.0f' to ',.2f' if you want two decimal places, etc.
    )


def format_with_decimals(value, tick_number):
    return f"{value:,.2f}"


def year_to_day_ave(df):
    # Assuming df has 8760 values representing hours of the year
    # Add a column 'Hour' to represent hours of the day (1 to 24)
    df["__Hour"] = [i % 24 + 1 for i in range(len(df))]
    df.set_index("__Hour", inplace=True)
    df = df.groupby("__Hour").mean()
    df = df.reset_index()
    return df
