@echo off
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
  echo uv is not installed. See README.md for setup instructions.
  pause
  exit /b 1
)
echo Installing project dependencies...
uv sync
if errorlevel 1 (
  echo Setup failed. Check your Python and internet connection.
  pause
  exit /b 1
)
echo Starting Job Hunter AI...
uv run streamlit run streamlit_app.py
pause
