from __future__ import annotations

from pathlib import Path

import pandas as pd
import dataframe_image as dfi


def df_to_image(
    df: pd.DataFrame, filename: Path | str, first_cell: str = None, decimals=1
) -> None:
    if first_cell:
        df.index.name = first_cell

    # Define the styles
    df = df.round(decimals)
    styles = [
        {"selector": "thead th", "props": [("background-color", "#A3D3CA")]},
        {
            "selector": "th:first-child, td:first-child",
            "props": [("background-color", "#A3D3CA")],
        },
    ]

    # Apply the styles
    styled_df = df.style.set_table_styles(styles)

    # Format the numbers to 2 decimal places

    if decimals == 1:
        styled_df = styled_df.format("{:,.1f}")

    if decimals == 0:
        styled_df = styled_df.format("{:,.0f}")

    # save the File
    dfi.export(styled_df, filename, table_conversion="matplotlib")
