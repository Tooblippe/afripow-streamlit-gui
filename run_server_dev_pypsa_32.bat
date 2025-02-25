call C:\Users\apvse\anaconda3\condabin\activate.bat pypsa_v32_py312
REM python -m pip install -i https://test.pypi.org/simple/ afripow-pypsa --upgrade
git pull
git checkout dev
streamlit run C:\Users\apvse\OneDrive\afripow-streamlit-gui-dev\PypsaGui.py --server.runOnSave=True --server.port=8999

call conda deactivate
