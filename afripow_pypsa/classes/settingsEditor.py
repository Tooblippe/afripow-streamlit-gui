# settings editor

import uuid
import tkinter as tk
from tkinter import ttk


def j_tree(tree, parent, dic):
    for key in sorted(dic.keys()):
        uid = uuid.uuid4()
        if isinstance(dic[key], dict):
            item = tree.insert(parent, "end", uid, text=key)
            tree.bind(
                "<Button-1>",
                lambda event, item=item, key=key: on_item_click(event, item, key),
            )
            j_tree(tree, uid, dic[key])
        elif isinstance(dic[key], tuple):
            item = tree.insert(parent, "end", uid, text=str(key) + "()")
            tree.bind(
                "<Button-1>",
                lambda event, item=item, key=key: on_item_click(event, item, key),
            )
            j_tree(tree, uid, dict([(i, x) for i, x in enumerate(dic[key])]))
        elif isinstance(dic[key], list):
            item = tree.insert(parent, "end", uid, text=str(key) + "[]")
            tree.bind(
                "<Button-1>",
                lambda event, item=item, key=key: on_item_click(event, item, key),
            )
            j_tree(tree, uid, dict([(i, x) for i, x in enumerate(dic[key])]))
        else:
            value = dic[key]
            if isinstance(value, str):
                value = value.replace(" ", "_")
            item = tree.insert(parent, "end", uid, text=key, value=value)
            tree.bind(
                "<Button-1>",
                lambda event, item=item, key=key: on_item_click(event, item, key),
            )


def on_item_click(event, item, key):
    # Add your click handler code here
    print(f"Item {item} with key '{key}' was clicked.")


def tk_tree_view(data):
    # Setup the root UI
    root = tk.Tk()
    root.title("Settings and Info viewer")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Setup the Frames
    tree_frame = ttk.Frame(root, padding="3")
    tree_frame.grid(row=0, column=0, sticky=tk.NSEW)

    # Setup the Tree
    tree = ttk.Treeview(tree_frame, columns=("Values"))
    tree.column("Values", width=100, anchor="w")
    tree.heading("Values", text="Values")
    j_tree(tree, "", data)
    tree.pack(fill=tk.BOTH, expand=1)

    # Limit windows minimum dimensions
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()
