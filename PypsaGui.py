"""

To revert changes:
Open PyCharm
Use Shift + Shift (Search Everywhere)
In the popup type: Registry and press Enter
Find "Registry" in the list of results and click on it.
In the new popup find python.debug.asyncio.repl line and uncheck the respective checkbox
Press Close.
Restart the IDE.
The asyncio support will be disabled in the debugger.

"""

import logging
import os
import sys
from pathlib import Path

# sys.path.insert(
#     0,
#     "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src",
# )
import streamlit as st

# import hack
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.helpers.helpers import package_version, get_package_version, get_current_git_branch

streamlit_root_logger = logging.getLogger(st.__name__)
streamlit_root_logger.setLevel(logging.ERROR)

st.set_page_config(page_title="PypsaGui", page_icon="📈", layout="wide")

with st.container(border=True):
    c1, c2 = st.columns([1, 10])
    with c1:
        st.image(
            Path("static/pypsa-logo.webp").__str__(), width=100
        )

    with c2:
        st.write(f"## Afripow Pypsa Management System version {get_package_version()}")

tab1, tab2 = st.tabs(["Changes log", "Documents"])
with tab1:
    st.markdown(
        f"""
    
    14/01/2025
    * Faster loading of image
    * Split into production and development version
    
    11/01/2025
    * Combined toolbox and GUI code into one package
    
    05/03/2024
    * Energy plot/data - Only add p0 for possitive energy values: SumP0 if P0>0
    * Added Energy Delta Plot.
    * Added Capacity Delta Plot.
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

package_version()
