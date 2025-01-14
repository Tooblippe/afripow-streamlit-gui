call C:\Users\apvse\anaconda3\condabin\activate.bat pypsa_v26_py311
REM python -m pip install -i https://test.pypi.org/simple/ afripow-pypsa --upgrade
git pull
git checkout dev
streamlit run C:\Users\apvse\OneDrive\afripow-streamlit-gui-dev\PypsaGui.py --server.runOnSave=True --theme.primaryColor="0098FF" --logger.level=error

call conda deactivate
