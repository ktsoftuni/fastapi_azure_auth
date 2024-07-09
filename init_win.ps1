$AppHome=$PSScriptRoot

python -m venv --clear $AppHome/.venv
.$AppHome/.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip==24.0.0
python -m pip install -e ".[test]"