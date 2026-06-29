@echo off
setlocal
cd /d "%~dp0"
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app\main.py --server.port 8520 --server.address 127.0.0.1 --server.maxUploadSize 20480 --server.fileWatcherType none
pause
