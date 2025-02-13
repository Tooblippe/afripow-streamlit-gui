# import binascii  # Not used, so it's commented out
import pickle
import uuid
import sqlite3
import time
from pathlib import Path
from typing import List

from fastapi import FastAPI
from huey import SqliteHuey
from starlette.responses import HTMLResponse

import xlwings as xw

# Initialize Huey with SQLite as the backend
huey = SqliteHuey("tasks.db")
app = FastAPI()


# Database setup
def init_db():
    """Initialize the tasks database and create the tasks table if it doesn't exist."""
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            status TEXT
        )"""
        )
        conn.commit()


# Call the database initialization function
init_db()


def decode_task(hex_string):
    """Decode a pickled task from the SQLite database."""
    return pickle.loads(hex_string)


# Add task to the database
def add_task_to_db(task_id: str, status: str):
    """Insert a new task into the database."""
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_id, status) VALUES (?, ?)", (task_id, status)
        )
        conn.commit()


# Update task status
def update_task_status(task_id: str, status: str):
    """Update the status of a task in the database."""
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id)
        )
        conn.commit()


# Remove completed tasks from the database
def remove_completed_tasks():
    """Delete tasks that have been marked as 'completed'."""
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE status = 'completed'")
        conn.commit()


# Define a Huey background task
@huey.task(context=True)
def background_task(message, task=None):
    """Run a background task and update its status."""
    task_id = task.id
    add_task_to_db(task_id, "running")

    # Define paths
    base_path = Path(
        r"C:\Users\tobie\PycharmProjects\afripow-streamlit-gui\experiments\huey_task_scheduler"
    )
    base_path = Path(
        r"C:\Users\apvse\OneDrive\afripow-streamlit-gui-dev\experiments\huey_task_scheduler"
    )
    original_file = base_path / "macro_test.xlsb"
    copy_file = base_path / f"{task_id}.xlsx"

    # Open the workbook without making it visible
    app = xw.App(visible=False)  # Ensure Excel is hidden
    wb = app.books.open(original_file)  # Open the file in the hidden Excel instance

    # Select sheet and run macro
    sheet = wb.sheets["Sheet1"]
    wb.macro("run_python")()
    sheet["A1"].value = task_id  # Set value in A1

    # Save a copy
    wb.save(copy_file)

    # Close workbook and quit Excel completely
    wb.close()
    app.quit()  # Ensure Excel process is terminated

    update_task_status(task_id, "completed")


# API endpoint to start a background task
@app.get("/start_task/")
def start_task():
    """Start a new background task and return the task ID."""
    task = background_task("I am a task")
    return {"message": "Task started", "task_id": task.id}


# API endpoint to get all running tasks
@app.get("/tasks/running", response_model=List[dict])
def get_running_tasks():
    """Retrieve all tasks with their status from the database."""
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT task_id, status FROM tasks")
        tasks = cursor.fetchall()
    return [{"task_id": t[0], "status": t[1]} for t in tasks]


# API endpoint to clear all completed tasks
@app.delete("/tasks/clear_completed")
def clear_completed_tasks():
    """Remove all completed tasks from the database."""
    remove_completed_tasks()
    return {"message": "Completed tasks removed"}


# API endpoint to check the current status of Huey tasks
@app.get("/huey", response_class=HTMLResponse)
def current_huey_tasks():
    """Fetch and display the current running and queued tasks."""
    with sqlite3.connect("huey.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM task")
        tasks = cursor.fetchall()

    html = ""

    # Check for running tasks
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT task_id FROM tasks WHERE status = ?", ("running",))
        id_r = cursor.fetchone()
        if id_r:
            html += f"<p> 1 - TASK ID : {id_r[0]} -- Running</p>"

    # Check for queued tasks
    for ix, task in enumerate(tasks):
        task_id = decode_task(task[0])[0]
        html += f"<p> {ix + 2} - TASK ID : {task_id} -- Queued</p>"

    # Return formatted HTML response
    if html:
        return f"""
        <html>
            <head>
                <title>Task Status</title>
            </head>
            <body>
               {html}
            </body>
        </html>
        """
    else:
        return """
        <html>
            <head>
                <title>Task Status</title>
            </head>
            <body>
               Queue is empty
            </body>
        </html>
        """
