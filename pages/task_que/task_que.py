from pathlib import Path
import xlwings as xw
from huey import SqliteHuey
import streamlit as st

PATH_TO_GIM = Path(
    r"C:\Users\apvse\OneDrive\S(Pypsa)-APVserver2\2502_Link-Relationship_Example\250211_GIM_Link_Example_v12.6.xlsb"
)
PATH_TO_TASK_DB = r"C:\Users\apvse\OneDrive\afripow-streamlit-gui-dev\pages\tasks.db"
PATH_TO_HUEY_DB = r"C:\Users\apvse\OneDrive\afripow-streamlit-gui-dev\pages\huey.db"


huey = SqliteHuey(PATH_TO_HUEY_DB)


@huey.task(context=True)
def create_excel_file(message, task=None):
    """Run a background task and update its status."""
    task_id = task.id
    original_file = PATH_TO_GIM

    # Open the workbook without making it visible
    app = xw.App(visible=False)  # Ensure Excel is hidden
    wb = app.books.open(original_file)  # Open the file in the hidden Excel instance

    # Select sheet and run macro
    wb.macro("Export")()
    # Close workbook and quit Excel completely
    wb.close()
    app.quit()  # Ensure Excel process is terminated
