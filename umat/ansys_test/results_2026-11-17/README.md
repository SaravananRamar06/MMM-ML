# ANSYS single-element test of the JC-PINN USERMAT, 17 November 2026

**Result: PASS.** On all 240 substeps, MAPDL's S11 matches `expected_single_element.csv` to within **1.2×10⁻⁵ MPa**. The tolerance is 0.1 MPa. The difference is the rounding of the 8-digit `E16.8` CSV output.

| Final values (ε₁₁ = 0.12) | ANSYS | Expected |
|---|---|---|
| S11 | 75.4065 MPa | 75.4065 MPa |
| EQPS (SVAR1) | 0.118845 | 0.118845 |
| FLAG (SVAR3) | 1 | 1 |

I also compared the other columns row by row. The largest EQPS difference is 4×10⁻⁹, the largest SIGY difference is 1.2×10⁻⁵ MPa, and FLAG is equal on every row. The peak is 135.82 MPa at ε₁₁ = 0.0025, as expected.

This checks the routine and the build inside ANSYS. It does not validate the model experimentally, and the general limits in `umat/README.md` still apply. The bracket model was not run.

## Files

| File | What it is |
|---|---|
| `jcpinn_single_element.csv` | MAPDL output: eps11, S11, EQPS, SIGY, FLAG at 240 substeps |
| `compare.txt` | Output of `umat/ansys_test/compare.py` |
| `jcpinn_out_tail.txt` | Key lines and the last 120 lines of `jcpinn.out` |
| `build_log_tail.txt` | The build's console, compile and link logs |
| `build_ifx.bat` | The build script that was used (see "Compiler" below) |

The DLL, `.rst`, `.db`, `.esav`, `.full` and the other ANSYS scratch files are not committed.

## Machine

| Item | Version |
|---|---|
| ANSYS | Mechanical APDL 2024 R1 (v241), build 24.1, UP20231106; licence "Ansys Mechanical Enterprise" |
| Fortran | Intel Fortran Compiler (ifx) 2026.2.0, build 20261001 (standalone offline installer from intel.com, SHA384 checked) |
| Linker / C runtime | Visual Studio 2019 Build Tools 16.11.63 (MSVC 14.29.30133, link 14.29.30159.0) |
| Windows | Windows 11 Pro, 10.0.26200 |
| CPU | Intel Core i9-14900HX; the run used 1 core |

### Compiler: a deviation from the UPF guide

For 2024 R1, `ANSUSERSHARED.bat` calls `%IFORT_COMPILER23%\bin\compilervars.bat` and `ifort`. MAPDL itself was built with ifort 2021.9 (oneAPI 2023.1), and it ships that runtime in `v241\tp\IntelCompiler\2023.1.0`. Intel's public download page no longer offers ifort 2023. Only Fortran 2026.2 is available, and it contains ifx and no ifort. The user chose ifx.

`build_ifx.bat` runs the same steps as `ANSUSERSHARED.bat`:
- the same compile macros and switches (`/DNOSTDCALL /DARGTRAIL /DCADOE_ANSYS /DPCWINNT_SYS /D_EFL /DFORTRAN /O2 /MD /c /fpp /4Yportlib /auto /watch:source /DPCWIN64_SYS /DPCWINX64_SYS`);
- the same `usermatLibex.def`, made with ANSYS's `UpCase.bat`;
- the same `usermatLib.lrf`, with `ANSYS.lib`, `ansMemManager.lib` and `ansOpenMP.lib`;
- the same `INCLUDE` and `LIB` order, with ANSYS's `customize\Include` and `custom\lib\winx64` first.

Only two things differ: `ifx` replaces `ifort`, and oneAPI's `setvars.bat intel64 vs2019` replaces `compilervars.bat`. The routine name is set in the script, not typed at the interactive prompt.

The DLL links to ANSYS's own Intel runtime import libraries, so at run time it uses the 2023.1 runtime that MAPDL loads. The compile had no warnings, and the run had no runtime errors.

## ANSYS 2024 R1 file layout (differs from the earlier `umat/README.md` text)

- In v241, `usermat3d` is not a separate file. `ansys\customize\user\usermat.F` contains `usermat`, `usermat1d`, `usermat3d`, `usermatbm`, `usermatps` and `usermat_harm`. The sources are in `ansys\customize\user\`, not in a `winx64` subfolder.
- The build folder therefore holds:
  - `usermat.F`: ANSYS's file with the stock `usermat3d` removed. That is lines 535–934, from `*deck,usermat3d` to the matching `end`. It is not committed because it is ANSYS source.
  - `usermat3d.F`: the repository's `umat/jc_pinn_usermat3d.F`, unchanged.
  - `usermatth.F`: ANSYS's file, unchanged.
- `ANSUSERSHARED.bat` is in `ansys\custom\user\winx64\`.

## Commands

Build. Run in `%USERPROFILE%\jcpinn_usermat_build`, which holds the three `.F` files and `build_ifx.bat`:

```bat
cmd /c "%USERPROFILE%\jcpinn_usermat_build\build_ifx.bat > build_console.log 2>&1"
```

This writes `usermatLib.dll`, 106,496 bytes, which exports `USERMAT`.

Run. `ANS_USER_PATH` was set for this one process only. The working folder was `%USERPROFILE%\jcpinn_usermat_run`:

```bat
cd /d "%USERPROFILE%\jcpinn_usermat_run"
set "ANS_USER_PATH=%USERPROFILE%\jcpinn_usermat_build" && "C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe" -b -np 1 -dir "%USERPROFILE%\jcpinn_usermat_run" -j jcpinn -i single_element.mac -o jcpinn.out
```

Compare:

```bat
python <repo>\umat\ansys_test\compare.py jcpinn_single_element.csv
```

These show that the user library was loaded:
- `jcpinn.out` reports `User Link path (ANS_USER_PATH): C:\Users\amitn\jcpinn_usermat_build` and "This MAPDL version was linked by Licensee".
- `TB,USER` and `TB,STATE` were accepted ("USER MATERIALS OPTION", 4 state variables).
- There is no default-usermat message. Without the library, the stock routine would have produced a different curve, with no softening and no SVAR1–3.
- The run reported 0 errors and 1 warning: "Ansys, Inc.-supplied version of coding for USERCK has been used". USERCK is the optional routine that checks the TB,USER constants. No USERCK is supplied here, so the warning is expected.

## Problems found and fixed

1. **`single_element.mac` lost the state variables.** `OUTRES,ALL,ALL` does not write SVAR, so POST26 stored nothing for SVAR1–3. Fix: add `OUTRES,SVAR,ALL`.
2. **`single_element.mac` wrote one CSV row.** `*GET,NROW,VARI,2,NSETS` ran before POST26 had stored data, so MAPDL ignored it ("No data points are stored") and NROW stayed 1. Fix: add `STORE,MERGE` before the `*GET`.
3. **The build steps in `umat/README.md` did not match the v241 file layout.** There is no `usermat3d.F` to replace, and the folder names were wrong (see above). The README has been updated.
4. Environment issues, which needed no repository change:
   - `setvars.bat` failed (`'vars.bat' is not recognized`) because `NoDefaultCurrentDirectoryInExePath` was set in the calling shell. `build_ifx.bat` clears it for its own process.
   - `-o jcpinn.out` is relative to the shell's working folder, not to `-dir`. Start MAPDL from inside the run folder.

The Fortran was not changed. `compare.py`, `expected_single_element.csv` and the 0.1 MPa tolerance were not changed.

## Time taken

| Step | Time |
|---|---|
| Clone the repo and check out `claude/lucid-faraday-9rkcqe` | 18 s |
| Find ANSYS and check for compilers | about 1 min |
| Install VS 2019 Build Tools, C++ workload (winget) | 837 s (about 14 min) |
| Download the Intel Fortran 2026.2 offline installer (754 MB) | 158 s |
| Install Intel Fortran 2026.2 (silent) | 96 s |
| Build `usermatLib.dll` (final run) | 2.4 s |
| MAPDL batch run (final run, 240 substeps) | 4.0 s wall; MAPDL reports 2.5 s solve |
| `compare.py` | 1.1 s |
