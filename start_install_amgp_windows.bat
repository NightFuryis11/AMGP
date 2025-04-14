@echo off
title AMGP Install-Update Script

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

set TMP=%CD%\amgp_env
set TEMP=%CD%\amgp_env


set DIR=%CD%\amgp_env
set CONDA_DIR=%CD%\amgp_env\conda
set ENV_DIR=%CD%\amgp_env\env
set MINICONDA_DOWNLOAD=https://repo.anaconda.com/miniconda/Miniconda3-py311_25.1.1-2-Windows-x86_64.exe
set MINICONDA_CHECKSUM=08bae491cef4f3b060774f661337ac4c8be51ccefac0e26e1fe78b14588301e6
set conda_exists=F

call "%CONDA_DIR%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" set conda_exists=T

if %conda_exists% == F (
	mkdir "%DIR%"

	call curl -Lk "%MINICONDA_DOWNLOAD%" > "%DIR%\miniconda_installer.exe"
	
	for /f %%a in ('CertUtil -hashfile "%DIR%\miniconda_installer.exe" SHA256 ^| find /i /v " " ^| find /i "%MINICONDA_CHECKSUM%"') do (
		set "output=%%a"
	)

	start /wait "" "%DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_DIR%
)

if not exist "%ENV_DIR%" (
	call %CONDA_DIR%\_conda.exe create --no-shortcuts -y -k --prefix "%ENV_DIR%" python=3.12
	@rem call %ENV_DIR%\python.exe install_dependencies.py
)

@rem set PYTHONNOUSERSITE=1
@rem set PYTHONPATH=
@rem set PYTHONHOME=
@rem set "CUDA_PATH=%INSTALL_ENV_DIR%"
@rem set "CUDA_HOME=%CUDA_PATH%"

"%ENV_DIR%\python.exe" -m pip install -r "%~dp0\requirements.txt"

call "%CONDA_DIR%\condabin\conda.bat" activate "%ENV_DIR%"

call "%~dp0\AMGP\start_amgp_windows.bat"

pause