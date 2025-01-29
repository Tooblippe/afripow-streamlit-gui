from pathlib import Path

import streamlit as st
import toml

from pages.helpers.helpers import select_folder, list_directories_with_paths

CONFIG_FILE = "pages/settings/settings.toml"
SHELVE = "pages/settings/SHELVE_DB"


def write_config(config_in):
    with open(CONFIG_FILE, "w") as f:
        toml.dump(config_in, f)


def read_config():
    with open(CONFIG_FILE, "r") as f:
        return toml.load(f)



config = read_config()


case_folder_last_selected = config['directories']['last_selected']
case_last_selected = config['case']['last_selected']
study_years_last_selected = list(config['study_years']['last_selected'])

select_case_folder = st.button("Select case folder")
if select_case_folder:
    last_selected = select_folder()
    config['directories']['last_selected'] = last_selected
    case_folder_last_selected = str(last_selected)
    write_config(config)

st.write(case_folder_last_selected)

input_dirs = list_directories_with_paths(Path(case_folder_last_selected))

case = st.selectbox("Select case", input_dirs.keys())

if case:
    config['case']['last_selected'] = case
    write_config(config)

# config['study_years']['last_selected'] = str([1,2,3])
#
st.write(case_last_selected)
# st.write(study_years_last_selected)
