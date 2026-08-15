@echo off
setlocal
cd /d "%~dp0.."
python scripts\validate.py || exit /b 1
python scripts\generate.py --clean || exit /b 1
python scripts\write_build_stamp.py
hugo --source site --destination generated\site --minify --baseURL http://127.0.0.1:1313/
hugo serve --source site --destination generated\site --bind 127.0.0.1 --baseURL http://127.0.0.1:1313/ --disableFastRender
