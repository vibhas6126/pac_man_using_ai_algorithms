@echo off
echo ==========================================
echo       STARTING AI PAC-MAN SERVER
echo ==========================================
echo.
echo Please leave this black window open while you play!
echo You can close it when you are finished.
echo.

:: Automatically open the default web browser to the game link
start http://127.0.0.1:5000

:: Run the python flask application
python app.py

pause
