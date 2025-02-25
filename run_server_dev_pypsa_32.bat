call C:\Users\apvse\anaconda3\condabin\activate.bat pypsa_v32_py312
git pull
git checkout dev
streamlit run C:\Users\apvse\OneDrive\afripow-streamlit-gui-dev\PypsaGui.py --server.runOnSave=True --server.port=8999

call conda deactivate
