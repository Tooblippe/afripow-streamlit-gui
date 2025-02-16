import json
from pathlib import Path

import pandas as pd
import streamlit as st
from huey import SqliteHuey
import time
from pages.task_que.task_que import create_excel_file, huey, PATH_TO_GIM

with st.container(border=True):
    st.write("# Task que (experimental)")


if st.button("Refresh"):
    st.rerun()

if st.button("Start Task"):
    st.write("# Latest task")
    task_messge = f"Running output Excel Macro on {Path(PATH_TO_GIM).name}"
    task = create_excel_file(task_messge)
    st.dataframe(
        pd.DataFrame(
            {"message": "Enqued " + task_messge, "task_id": task.id}, index=[task.id]
        ),
        use_container_width=True,
    )
#
# try:
#     with open("current_task.json", "r", encoding="utf-8") as f:
#         data = json.load(f)
#         st.write(data)
# except FileNotFoundError:
#     st.write({"message": "No current task found"})


st.write("# Task que")
st.dataframe(pd.DataFrame(huey.pending()), use_container_width=True)
