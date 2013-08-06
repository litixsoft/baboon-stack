@echo off

IF EXIST "%CD%\build" (
echo Clean...
del /q "%CD%\build\*.*"
) else (
mkdir "%CD%\build"
)

echo Build...
cxfreeze lxm.py --target-dir "%CD%\build" --icon "%CD%\ressources\baboonstack.ico" --compress
echo Done...