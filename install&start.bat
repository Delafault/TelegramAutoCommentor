@echo off
chcp 65001 > nul

pip show telethon > nul
if errorlevel 1 (
    pip install telethon
)

pip show tgcrypto > nul
if errorlevel 1 (
    pip install tgcrypto
)

echo Запускаю скрипт...
timeout /t 3 >nul
start python commentor.py