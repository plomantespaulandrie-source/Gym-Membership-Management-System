@echo off
title Gym System - Public Mobile Tunnel
echo ====================================================
echo Starting Public Tunnel for Mobile Data Access...
echo ====================================================
echo.
echo Connecting to public tunnel...
echo Keep this window open while accessing from your phone!
echo.
ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:5000 nokey@localhost.run
pause
