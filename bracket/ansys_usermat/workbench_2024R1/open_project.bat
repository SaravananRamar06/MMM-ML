@echo off
rem Open a Workbench 2024 R1 project with ANS_USER_PATH set (needed to re-solve the USERMAT model).
rem Usage: open_project.bat [path\to\Bracket_USERMAT_2024R1.wbpj]
setlocal
if "%JCPINN_USERMAT_DIR%"=="" set "JCPINN_USERMAT_DIR=%USERPROFILE%\jcpinn_usermat_build"
set "ANS_USER_PATH=%JCPINN_USERMAT_DIR%"
set "PROJ=%~1"
if "%PROJ%"=="" set "PROJ=%~dp0Bracket_USERMAT_2024R1.wbpj"
start "" "C:\Program Files\ANSYS Inc\v241\Framework\bin\Win64\RunWB2.exe" -F "%PROJ%"
