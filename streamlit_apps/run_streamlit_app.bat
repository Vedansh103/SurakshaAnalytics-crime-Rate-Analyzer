@echo off
echo Starting Crime Analyser Streamlit App...
echo.
echo Make sure you have installed the requirements:
echo pip install -r requirements_streamlit.txt
echo.
echo Opening app in browser...
cd /d "%~dp0"
cd ..
streamlit run streamlit_apps/simple_streamlit.py
pause