#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

mkdir -p new_images output

PYTHON_BIN="venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "Brak interpretera w venv. Sprawdz instalacje Python 3."
  exit 1
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" -m streamlit run app.py
