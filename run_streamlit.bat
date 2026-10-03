@echo off
echo 🚀 Starting Suraksha Analytics Streamlit App...
echo.
echo 📊 Loading Crime Data Analysis Platform...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo ✅ Starting web application...
echo 🌐 Open your browser to: http://localhost:8501
echo.
echo 💡 Press Ctrl+C to stop the application
echo.

streamlit run streamlit_main.py --server.port 8501 --server.headless false

pause