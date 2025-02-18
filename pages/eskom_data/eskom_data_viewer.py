import datetime
import glob
import csv
import os
from pathlib import Path

import matplotlib
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.pyplot import xlabel, ylabel, title

from pages.helpers.helpers import download_df


ESKOM_DATA_DIR = "pages/eskom_data/"

eskom_columns = [
    "Original Res Forecast before Lockdown",
    "Residual Forecast",
    "RSA Contracted Forecast",
    "Dispatchable Generation",
    "Residual Demand",
    "RSA Contracted Demand",
    "International Exports",
    "International Imports",
    "Thermal Generation",
    "Nuclear Generation",
    "Eskom Gas Generation",
    "Eskom OCGT Generation",
    "Hydro Water Generation",
    "Pumped Water Generation",
    "ILS Usage",
    "Manual Load_Reduction(MLR)",
    "IOS Excl ILS and MLR",
    "Dispatchable IPP OCGT",
    "Eskom Gas SCO",
    "Eskom OCGT SCO",
    "Hydro Water SCO",
    "Pumped Water SCO Pumping",
    "Wind",
    "PV",
    "CSP",
    "Other RE",
    "Total RE",
    "Wind Installed Capacity",
    "PV Installed Capacity",
    "CSP Installed Capacity",
    "Other RE Installed Capacity",
    "Total RE Installed Capacity",
    "Installed Eskom Capacity",
    "Total PCLF",
    "Total UCLF",
    "Total OCLF",
    "Total UCLF+OCLF",
    "Non Comm Sentout",
    "Drakensberg Gen Unit Hours",
    "Palmiet Gen Unit Hours",
    "Ingula Gen Unit Hours",
]


def latest_file():

    list_of_files = glob.glob(os.path.join(ESKOM_DATA_DIR, "*.csv"))
    # * means all if need specific format then *.csv
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    else:
        return None


# @st.cache
def read_df():
    return pd.read_csv(Path(latest_file()), parse_dates=True)


def upload_and_fix():

    st.write("Upload latest Eskom file")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv"],
        accept_multiple_files=False,
        label_visibility="hidden",
    )

    if uploaded_file:
        uploaded_filenae = uploaded_file.name
        new_eskom_file = Path(ESKOM_DATA_DIR) / uploaded_filenae
        print(f"file uploaded {new_eskom_file}")
        if uploaded_file is not None:
            file_type = new_eskom_file.suffix[1:]
            name = new_eskom_file.name[:-4]
            if uploaded_file is not None and file_type == "csv":
                # To read file as bytes:
                bytes_data = uploaded_file.getvalue()

                with open(new_eskom_file, "wb") as f:
                    f.write(bytes_data)
            else:
                st.write("Must be a csv file")

        # fix the file
        with open(new_eskom_file, "r") as f:
            csv_file = csv.DictReader(f)
            df = pd.DataFrame(csv_file)

        df = df.iloc[:, :-1]
        df["Original Res Forecast before Lockdown"] = df[
            "Original Res Forecast before Lockdown"
        ].apply(lambda x: 0 if x == "" else float(x))
        df.to_csv(
            Path(f"{ESKOM_DATA_DIR}/latest_{datetime.date.today()}.csv"),
            index=False,
        )
        st.rerun()
    else:
        st.write("Drop raw eskom download file here.")


def eskom_viewer_new():

    st.write("# Eskom Data Viewer")

    select, c1, c2 = st.columns([2, 6, 2], border=True)

    with select:
        report_start_date = st.date_input(
            "Select reporting start date",
            datetime.date(2024, 1, 1),
            max_value=datetime.datetime.today(),
            min_value=datetime.date(2018, 1, 1),
            key="date_start",
        )
        report_end_date = st.date_input(
            "Select reporting end date",
            datetime.datetime.today(),
            max_value=datetime.datetime.today(),
            min_value=report_start_date,
            key="date_end",
        )

        default_col = []
        if st.checkbox("Select all Data Columns"):
            default_col += eskom_columns
        else:
            if st.checkbox("International"):
                default_col += ["International Exports", "International Imports"]

            if st.checkbox("Renewable Generation"):
                default_col += [
                    "Wind",
                    "PV",
                    "CSP",
                    "Other RE",
                    "Total RE",
                ]

            if st.checkbox("Renewable Installed Capacity"):
                default_col += [
                    "Wind Installed Capacity",
                    "PV Installed Capacity",
                    "CSP Installed Capacity",
                    "Other RE Installed Capacity",
                    "Total RE Installed Capacity",
                ]

            if st.checkbox("Pumped Storage Generating Hours"):
                default_col += [
                    "Drakensberg Gen Unit Hours",
                    "Palmiet Gen Unit Hours",
                    "Ingula Gen Unit Hours",
                ]

        if not default_col:
            default_col = ["RSA Contracted Forecast"]

        col = st.multiselect(
            "Click to Add Data Column", eskom_columns, default=default_col
        )

    master_df = read_df()

    df = master_df.copy()
    df.index = pd.to_datetime(df["Date Time Hour Beginning"])
    df = df[col]

    mask = (df.index.date >= report_start_date) & (df.index.date <= report_end_date)
    df = df.loc[mask]

    if not df.empty:

        with c1:
            download_df(
                df,
                f"eskom_data",
                f"{report_start_date}_{report_end_date}",
                show_df_button=False,
            )
            fig, ax = plt.subplots()
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.StrMethodFormatter("{x:,.0f}")
            )
            fig.set_size_inches(9.5, 5.5)
            xlabel("Date/Time[h]")
            ylabel("MW")
            df.plot(kind="line", ax=ax)
            ax.legend(bbox_to_anchor=(1.4, 0.9), labels=col, loc="right")
            ax.title.set_size(15)
            fig = matplotlib.pyplot.gcf()
            st.pyplot(fig, use_container_width=False)
    else:
        st.write("### Please select a data column(s)")

    with c2:
        st.write("[Eskom Data Source](https://www.eskom.co.za/dataportal/)")
        st.write(
            "[Data Request Form](https://www.eskom.co.za/dataportal/data-request-form/)"
        )
        st.write(f"Data file: {Path(latest_file()).name}")
        upload_and_fix()
