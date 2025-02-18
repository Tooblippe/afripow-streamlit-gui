import streamlit as st

from pages.eskom_data.eskom_data_viewer import eskom_viewer_new
from pages.helpers.helpers import page_setup


page_setup(page_name="Data Viewer")
options = ["Eskom", "Water"]



option = st.sidebar.selectbox("Select data option", options=options, index=None)
if not option:
    st.write("Select data option from sidebar")

if option == "Eskom":
    eskom_viewer_new()
elif option == "Water":
    st.write("Water")
