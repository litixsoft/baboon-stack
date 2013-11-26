@echo off
if "%1"=="build" goto build
if "%1"=="install" goto install

echo Use "make build" and "make install"

goto exit

:build
IF EXIST "%CD%\build" (
echo Clean...
del /q "%CD%\build\*.*"
) else (
mkdir "%CD%\build"
)

echo Build...
cxfreeze lxm.py --target-dir "%CD%\build" --icon "%CD%\ressources\baboonstack.ico" --compress
echo Done...
goto exit

:install
copy "%CD%\build\*.*" "%LXPATH%\lxm\*"
del /q "D:\BaboonStack\common\lxm\*"
copy "%CD%\build\*.*" "D:\BaboonStack\common\lxm\*"
goto exit


:exit
echo.