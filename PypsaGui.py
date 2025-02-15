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
from pathlib import Path

import streamlit as st
from streamlit_local_storage import LocalStorage

from pages.helpers.helpers import (
    package_version,
    get_package_version,
    list_directories_with_paths,
    get_startup_directory,
    get_list_of_users,
    find_files_containing_string,
    open_location,
    select_folder,
    get_index_of_setting,
)
from pages.helpers.study_types import STUDY_TYPES
from pages.helpers.user_settings_db import (
    create_settings_db,
    load_user_settings,
    get_setting,
    set_setting,
)

streamlit_root_logger = logging.getLogger(st.__name__)
streamlit_root_logger.setLevel(logging.ERROR)

st.set_page_config(page_title="PypsaGui", page_icon="📈", layout="wide")
st.session_state["stMetricsConfig"] = ""

localS = LocalStorage()

if "click_tracker" not in st.session_state:
    st.session_state.click_tracker = False

# if not st.session_state.get("logged_in", False):
#     login_dialog()
with st.container(border=True):
    c1, c2 = st.columns([1, 10])
    with c1:
        st.image(Path("static/pypsa-logo.webp").__str__(), width=100)

    with c2:
        st.write(f"## Afripow Pypsa Management System version {get_package_version()}")

# if st.sidebar.button("Clear local storage"):
#     localS.deleteAll()

create_settings_db()
d = load_user_settings()


cola, colb, colc = st.columns(3, border=True)

with cola:
    who_is_working = localS.getItem("who_is_working") or "Marc Goldstein"
    who_is_working = st.radio(
        "Current user",
        get_list_of_users(),
        index=get_list_of_users().index(who_is_working),
    )
    localS.setItem("who_is_working", who_is_working)

gim_file = ""
with colb:
    b_1, b_2 = st.columns(2)
    with b_1:
        st.write(get_startup_directory())

        # st.write(Path(get_setting_for_current_user("gim_file")).name)
    with b_2:
        if st.button("Set PyPSA_csv directory", type="primary"):
            startup_folder = select_folder()
            set_setting(who_is_working, "startup_directory", startup_folder)

        if st.button("Open PyPSA_csv directory", type="primary"):
            open_location(get_startup_directory())
        # if st.button("Select GIM File", key="gim"):
        #     gim_file = select_file()
        #
        #     set_setting(who_is_working, "gim_file", str(gim_file))

        # if st.button("Open GIM file", type="primary"):
        #     open_location(get_setting_for_current_user("gim_file"))


if get_startup_directory():
    available_projects = list_directories_with_paths(get_startup_directory())
    l = list(available_projects.keys())
    s = load_user_settings()
    bp = get_setting(who_is_working, "base_project")

    col1, col2, col3, col4 = st.columns(4, border=True)
    base_project = None
    with col1:
        base_project = st.radio(
            "Select base project",
            available_projects.keys(),
            index=l.index(bp) if bp else 0,
            key="base_project",
        )
        set_setting(who_is_working, "base_project", base_project)
        if st.button("Open project directory", type="primary"):
            open_location(get_startup_directory() / base_project)

    with col2:
        input_dirs = list_directories_with_paths(get_startup_directory() / base_project)
        cases = [k for k in input_dirs.keys() if "reporting" not in k]
        index = get_index_of_setting(
            cases,
            "case",
        )

        case = st.radio("Select case", cases, index=index, key="case")
        set_setting(who_is_working, "case", case)
        if st.button("Open case directory", type="primary"):
            open_location(get_startup_directory() / base_project / case)

    with col3:
        study_types = list(STUDY_TYPES.keys())

        index = get_index_of_setting(study_types, "base_study_type")

        base_study_type = st.radio(
            "Select study type",
            study_types,
            index=index,
            key="study_type",
        )
        set_setting(who_is_working, "base_study_type", base_study_type)

    with col4:
        excel_files = find_files_containing_string(
            get_startup_directory() / base_project, "xls"
        )

        index = get_index_of_setting(
            excel_files,
            "excel_file",
        )
        excel_file = st.radio(
            "Settings file", excel_files, key="excel_file", index=index
        )
        set_setting(who_is_working, "excel_file", excel_file)

        if excel_file:
            path_to_excel = get_startup_directory() / base_project / excel_file

            if st.button("Open settings file", type="primary"):
                open_location(path_to_excel)
else:
    st.write("Please selectg base folder")

package_version()
