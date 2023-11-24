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

pip show openai > nul
if errorlevel 1 (
    pip install openai
)

echo Запускаю скрипт...
timeout /t 3 >nul
start python main.py
