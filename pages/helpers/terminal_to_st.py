import sys
from contextlib import contextmanager
from io import StringIO

import streamlit as st


@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)
    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if not b.endswith("\n"):  # Check if the incoming text ends with a newline
                b += "\n"  # If not, append a newline character
            buffer.write(b)
            v = buffer.getvalue()
            output_func(v)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def terminal_stdout_to_st_element(dst):
    with st_redirect(sys.stdout, dst):
        yield
