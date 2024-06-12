call C:\Users\User\anaconda3\condabin\activate.bat pypsa_v28_py311
python -m pip install -i https://test.pypi.org/simple/ afripow-pypsa --upgrade
git pull
streamlit run C:\Users\User\OneDrive\S(Pypsa)\afripow_gui\PypsaGui.py --server.runOnSave=True --theme.primaryColor="0098FF" --logger.level=error
call conda deactivate
