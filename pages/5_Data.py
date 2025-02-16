import streamlit as st

from pages.helpers.helpers import page_setup


page_setup(page_name="Data Viewer")

with st.container(border=True):
    st.markdown("# Data viewer", unsafe_allow_html=True)

options = ["Eskom", "Water"]

option = st.selectbox("Select data option", options=options)


if option == "Eskom":
    st.write("Eskom")
elif option == "Water":
    st.write("Water")
