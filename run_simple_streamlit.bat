@echo off
echo Starting Suraksha Analytics Streamlit App...
echo.
echo Navigate to http://localhost:8503 in your browser
echo Press Ctrl+C to stop the server
echo.
streamlit run simple_streamlit.py --server.port 8503
pause