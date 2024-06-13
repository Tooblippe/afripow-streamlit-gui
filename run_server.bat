call C:\Users\apvse\anaconda3\condabin\activate.bat pypsa_v26_py311
python -m pip install -i https://test.pypi.org/simple/ afripow-pypsa --upgrade
git pull
streamlit run C:\Users\apvse\OneDrive\afripow-streamlit-gui\PypsaGui.py --server.runOnSave=True --theme.primaryColor="0098FF" --logger.level=error

call conda deactivate
