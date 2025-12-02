@echo off
echo Building Bluetooth Messenger for Windows...
echo.

REM Install dependencies
echo Installing dependencies...
pip install pyinstaller kivy pybluez

echo.
echo Building executable...
pyinstaller build_windows.spec

echo.
if exist "dist\BluetoothMessenger.exe" (
    echo Build successful!
    echo Executable location: dist\BluetoothMessenger.exe
    echo.
    echo You can now distribute this .exe file!
) else (
    echo Build failed. Check the output above for errors.
)

pause
