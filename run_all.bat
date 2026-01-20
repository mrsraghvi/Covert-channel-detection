@echo off
echo ============================================
echo   🚨 Covert Channel Detection System
echo ============================================

REM Activate Conda environment
call conda activate covert

REM Start Live Packet Logger
echo [1/3] Starting Live Packet Logger...
start "Live Logger" cmd /k python live\live_logger.py

REM Small delay to ensure logger is ready
timeout /t 3 > nul

REM Start Real-Time Detector
echo [2/3] Starting Real-Time Detector...
start "Realtime Detector" cmd /k python -m live.realtime_detector

REM Small delay before dashboard
timeout /t 3 > nul

REM Start Dashboard
echo [3/3] Starting Dashboard...
start "Dashboard" cmd /k streamlit run dashboard\app.py

echo ============================================
echo   ✅ System Launched Successfully
echo ============================================

pause
