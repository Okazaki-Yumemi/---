@echo off
chcp 65001 >nul
python -m PyInstaller --onefile --windowed --name "代谢之城 Cell City" main.py
pause
