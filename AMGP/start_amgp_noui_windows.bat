@echo off
set %PYTHON_EXE%="%CD%\amgp_env\env\python.exe"
if %1.==. (
	call %PYTHON_EXE% "%CD%\AMGP\AMGP.py" --no-ui
)
else (
	call %PYTHON_EXE% "%CD%\AMGP\AMGP.py" %1
)