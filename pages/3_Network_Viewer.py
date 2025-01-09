import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pypsa
import streamlit as st

# sys.path.insert(
#     0,
#     "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src",
# )


from afripow_pypsa.helpers.direcory_cases import find_int_named_subdirs

from pages.helpers.helpers import select_folder, list_directories_with_paths

st_container = st.sidebar.container(border=True)
from mitosheet.streamlit.v1 import spreadsheet

# manage state
if "folder_path" not in st.session_state:
    st.session_state.folder_path = os.getcwd()
# handle study directory selection
selected_folder_path = st.session_state.get("folder_path", None)
folder_select_button = st_container.button(
    "Select folder containing cases", use_container_width=True, type="primary"
)
if folder_select_button:
    base_dir = select_folder()
    st.session_state.folder_path = base_dir
base_dir = st.session_state.folder_path
st_container.text(base_dir)

# handle the case directory
input_dirs = list_directories_with_paths(Path(base_dir))
start_dir = st_container.selectbox(
    "Select case",
    input_dirs.keys(),
)
year = str(
    st.selectbox("Select year", find_int_named_subdirs(Path(base_dir) / start_dir))
)

network_path = Path(base_dir) / start_dir / year / "Results_uc"
n = pypsa.Network()
n.import_from_csv_folder(network_path)

sheets = ["Link", "Bus", "Generator", "StorageUnit"]
element = st.selectbox("Element", sheets)
df = n.df(element)
df = n.links_t.p0
columns = df.columns
column = st.selectbox("Select columns", columns)


a, b, c = st.columns(3)

with a:
    x = [i + 1 for i, _ in enumerate(n.snapshots)]
    df["x"] = x
    st.pyplot(df.plot(kind="scatter", x="x", y=column, s=2).figure)

plt.clf()

with b:
    st.pyplot(df[column].sort_values(ascending=False).plot().figure)


with c:
    df["Hour"] = np.arange(1, 8761) % 24
    df.loc[df["Hour"] == 0, "Hour"] = (
        24  # Adjusting so that we count hours as 1-24 instead of 0-23
    )
    df["Day"] = np.arange(1, 8761) // 24 + 1

    # Now, let's group by the 'Hour' column and get the average of each hour across all days
    average_by_hour = df[[column, "Hour"]].groupby("Hour").mean()

    # Assuming you've already plotted something
    plt.clf()
    fig = average_by_hour[column].plot().figure

    st.pyplot(fig)

# final_dfs, code = spreadsheet(*dfs, n.links_t.p0.reset_index(), df_names= [*sheets,"Links-p0"], height="100%")
