# import sys

from streamlit.web.bootstrap import run

# disable in actions - registry  python.debug.asyncio.repl
from streamlit import config as _config

# sys.path.insert(
#     0,
#     "C:\\Users\\tobie\\PycharmProjects\\afripow-pypsa-reporting\\afripow_toolbox_reporting\\src",
# )

_config.set_option("server.runOnSave", True)
_config.set_option("theme.primaryColor", "0098FF")
_config.set_option("logger.level", "ERROR")
# --server.runOndSave=True --theme.primaryColor="0098FF" --logger.level=error

if __name__ == '__main__':
    run("PypsaGui.py", False, [], {})
