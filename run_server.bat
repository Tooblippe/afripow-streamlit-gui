call C:\Users\apvse\anaconda3\condabin\activate.bat pypsa_v32_py312
git pull
git checkout master
streamlit run C:\Users\apvse\OneDrive\afripow-streamlit-gui\PypsaGui.py --server.port=8088
call conda deactivate
