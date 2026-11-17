@echo off
rem Non-interactive equivalent of ANSYS 2024 R1 ANSUSERSHARED.bat for USERMAT,
rem using Intel ifx (oneAPI 2026.2) instead of ifort 2023 (IFORT_COMPILER23),
rem which is not installed. Compile switches, macros, .def/.lrf contents and
rem link libraries are copied from
rem   C:\Program Files\ANSYS Inc\v241\ansys\custom\user\winx64\ANSUSERSHARED.bat
setlocal
cd /d "%~dp0"

rem setvars.bat does "pushd <comp>\env" + "call vars.bat"; that needs cmd to
rem search the current directory, which NoDefaultCurrentDirectoryInExePath blocks.
set "NoDefaultCurrentDirectoryInExePath="
set "VS2019INSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools"
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" intel64 vs2019 || exit /B 1
setlocal EnableDelayedExpansion

set "ROOT_DIR=C:\Program Files\ANSYS Inc\v241"
set "PLATFORM_DIR=winx64"
set "MACHINE_TARGET=X64"
set "AIDIR=%ROOT_DIR%\ansys\customize\Include"
set "ALDIR=%ROOT_DIR%\ansys\Custom\Lib\%PLATFORM_DIR%"
set "INCLUDE=%AIDIR%;%INCLUDE%"
set "LIB=%ALDIR%;%LIB%"

set "COMMACS=/DNOSTDCALL /DARGTRAIL /DCADOE_ANSYS /DPCWINNT_SYS"
set "FMACS=/D_EFL /DFORTRAN"
set "MACS64=/DPCWIN64_SYS /DPCWINX64_SYS"
set "COMSWITCH=/O2 /MD /c"
set "FSWITCH=/fpp /4Yportlib /auto /Fo.\ /watch:source"

del /q *.obj compile.log link.log usermatLib.* >NUL 2>&1

echo ==== ifx version >> compile.log
ifx /QV >> compile.log 2>&1
echo ==== link version >> compile.log
link 2>&1 | findstr /C:"Version" >> compile.log

echo ==== compile >> compile.log
echo ifx %COMMACS% %FMACS% %COMSWITCH% %FSWITCH% %MACS64% *.F >> compile.log
ifx %COMMACS% %FMACS% %COMSWITCH% %FSWITCH% %MACS64% *.F >> compile.log 2>&1
set COMPILE_RC=%ERRORLEVEL%
echo compile exit code: %COMPILE_RC% >> compile.log
findstr /I /C:": error" compile.log >NUL && (echo UPF COMPILER ERROR & exit /B 1)
if not exist usermat.obj (echo usermat.obj missing & exit /B 1)

echo EXPORTS> usermatLibex.def
echo.  >>     usermatLibex.def
call "%ROOT_DIR%\ansys\Custom\user\%PLATFORM_DIR%\upcase.bat" usermat >> usermatLibex.def

echo -out:usermatLib.dll>              usermatLib.lrf
echo -def:usermatLibex.def>>           usermatLib.lrf
echo -dll>>                            usermatLib.lrf
echo -machine:%MACHINE_TARGET%>>       usermatLib.lrf
echo -map>>                            usermatLib.lrf
echo -manifest:embed>>                 usermatLib.lrf
echo -defaultlib:ANSYS.lib>>           usermatLib.lrf
echo -defaultlib:ansMemManager.lib>>   usermatLib.lrf
echo -defaultlib:ansOpenMP.lib>>       usermatLib.lrf
echo. >>                               usermatLib.lrf
echo *.obj>>                           usermatLib.lrf

echo ======================================== >> link.log
echo  Linking usermat ... >> link.log
link @usermatLib.lrf >> link.log 2>&1
set LINK_RC=%ERRORLEVEL%
echo link exit code: %LINK_RC% >> link.log
if not "%LINK_RC%"=="0" (echo usermatLib.dll FAILED to link & exit /B 1)
if not exist usermatLib.dll (echo usermatLib.dll missing & exit /B 1)
echo usermatLib.dll has been successfully built.
exit /B 0
