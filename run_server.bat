call C:\ProgramData\Anaconda3\condabin\activate.bat pypsa_v0_026_3_1
python -m pip install -i https://test.pypi.org/simple/ afripow-pypsa --upgrade
git pull
streamlit run C:\Users\User\OneDrive\S(Pypsa)\afripow_gui\PypsaGui.py --server.runOnSave=True --theme.primaryColor="0098FF" --logger.level=error
call conda deactivate