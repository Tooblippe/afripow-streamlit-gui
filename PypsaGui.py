__guiversion__ = "0.0.3"

import logging
import os
import pdb
import sys

sys.path.insert(
    0,
    "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src",
)
import streamlit as st

# import hack
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.helpers.helpers import package_version, get_package_version

streamlit_root_logger = logging.getLogger(st.__name__)
streamlit_root_logger.setLevel(logging.ERROR)

st.set_page_config(page_title="PypsaGui", page_icon="📈", layout="wide")

with st.container(border=True):
    c1, c2 = st.columns([1, 10])
    with c1:
        st.image(
            "https://pypsa.readthedocs.io/en/latest/_static/pypsa-logo.png", width=100
        )

    with c2:
        st.write(f"## Afripow Pypsa Management System version {get_package_version()}")

tab1, tab2 = st.tabs(["Changes log", "Documents"])
with tab1:
    st.markdown(
        f"""
    
    05/03/2024
    * Added Energy Delta Plot
    * Added Capacity Delta Plot
    * Added Copy to Clipboard function
    * Link plot colour can be spesified before report generation
    * Forced Link plots y-origin to zero if all values are possitive
    
    27/02/2024
    * Rounding to zero digits in Capacity and Energy Plot
    * Show % and rounding to 1 in Loadfactor table (png), csv - write out full values
    

    22/02/2024
    * added solver options to - use_lpmethod_4=True,
    * added load factor graph and csv in reports
    
    21/02/2024    
    * Update Energy and Capacity Plot Colors
    * CSV file transpose
    * Will choose reporting xlsm files based on "_setup" in the filename
    * Fix reporting when no solved case in Results folder
    * Plot naming conventions linkName_plotType_year
    * Implement first version of Gui
    """
    )
with tab2:
    st.markdown("""Docs - Reporting""")

st.sidebar.write(f":green[GUI version: {__guiversion__}]")
