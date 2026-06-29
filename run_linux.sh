#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app/main.py --server.port 8520 --server.address 127.0.0.1 --server.maxUploadSize 20480 --server.fileWatcherType none
