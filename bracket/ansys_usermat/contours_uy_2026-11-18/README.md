# Contour pictures of the corrected-load bracket runs, 18 November 2026

MAPDL 2024 R1 post-processing (`../post_contours.mac`, driven by `../make_contours.py`) of the result files of the 5 mm batch runs in `../results_uy_2026-11-18/`. The load is the pin load +P_y, imposed as UY = +2 mm on the upper half of the bore.

- **Views:** front view (x-y plane, looking along -z), true-scale deformation.
- **Times:** `peak` = the saved substep with the largest reaction, and `final` = UY = 2 mm.
- **Runs and plots:**
  - every run: UY, von Mises, maximum and minimum principal stress;
  - EP and USERMAT runs only: equivalent plastic strain (EPPL);
  - USERMAT only: the range flag (SVAR3) and the flow stress (SVAR2).
- **Index:** `contours_index.json` lists each picture with the run's peak and final reaction.
- **Footer label:** the "Elastic--Static Structural (B5)" footer is the system name carried over from the team's Workbench deck; the material is the one in the file name.
- **Support corners:** stress maxima on the mounting-face corners are fixed-support singularities.

Reproduce:

```bat
set "ANS_USER_PATH=%USERPROFILE%\jcpinn_usermat_build"
python bracket\ansys_usermat\make_contours.py OUT_DIR <run>\usermat:usermat <run>\elastic:elastic <run>\ep_miso:ep_miso
```