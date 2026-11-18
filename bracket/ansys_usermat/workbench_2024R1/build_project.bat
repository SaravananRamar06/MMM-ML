@echo off
rem Build and solve the Workbench 2024 R1 bracket project with the JC-PINN USERMAT.
rem Defaults: USERMAT DLL in %USERPROFILE%\jcpinn_usermat_build, project in %USERPROFILE%\jcpinn_workbench.
rem ANS_USER_PATH is set for this process only.
setlocal
set "JCPINN_WB_SCRIPTS=%~dp0"
if "%JCPINN_USERMAT_DIR%"=="" set "JCPINN_USERMAT_DIR=%USERPROFILE%\jcpinn_usermat_build"
if "%JCPINN_WB_DIR%"=="" set "JCPINN_WB_DIR=%USERPROFILE%\jcpinn_workbench"
if not exist "%JCPINN_USERMAT_DIR%\usermatLib.dll" (echo usermatLib.dll not found in %JCPINN_USERMAT_DIR% & exit /b 1)
set "ANS_USER_PATH=%JCPINN_USERMAT_DIR%"
if not exist "%JCPINN_WB_DIR%" mkdir "%JCPINN_WB_DIR%"
"C:\Program Files\ANSYS Inc\v241\Framework\bin\Win64\RunWB2.exe" -B -R "%JCPINN_WB_SCRIPTS%build_project.wbjn"
