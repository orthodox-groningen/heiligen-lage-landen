@echo off
setlocal
cd /d "%~dp0.."
python -m pip install -r requirements.txt
python scripts\validate.py || exit /b 1
python scripts\generate.py --clean || exit /b 1
python scripts\inject_git_dates.py
python scripts\write_build_stamp.py
hugo --source site --destination generated\site --minify --baseURL /
echo Built generated\site
