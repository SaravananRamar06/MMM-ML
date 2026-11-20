"""2D plane-strain bracket with a through-thickness edge crack at the R10 crotch fillet (MAPDL 2024 R1).

The bracket is a straight extrusion (40 mm along z) of the profile in bracket/cad/Rib Bracket.STEP, so its x-y
section is modelled with PLANE183 in plane strain (per mm of thickness). The crack starts on the R10 fillet at
the point of highest tension found in the 3D elastic run, (31.146, 14.340) mm (angle -120 deg about the fillet
axis (36.1464, 23)), and runs perpendicular to that tension (radially, direction -120 deg) into the boss.

Load and supports as in the 3D decks: both mounting faces (x = 210) fixed, UY imposed on the upper half of the
bore (y >= 0). Two deck kinds:
  elastic  - linear elastic, UY = 0.1 mm; writes the reaction and the interaction-integral K_I (CINT SIFS)
  usermat  - the JC-PINN USERMAT (TB,USER) at a porosity case, UY ramped to 2 mm; writes the reaction history
Usage: python make_crack_decks.py OUT_DIR
Writes OUT_DIR/<kind>_<case>_a<len>/crack.dat for the crack lengths in A_MM and the cases in CASES.
"""
import math
import sys
from pathlib import Path

A_MM = [0, 1, 2, 4, 6, 8, 12, 16, 20, 25, 30]
# porosity cases, density and G coupled by decision D5 (same as make_decks.GPHI_CASES)
CASES = {'gphi0': (2700.0, 25300.0), 'gphi4': (2592.0, 24288.0), 'gphi785': (2488.05, 23313.95)}
E_EL = 76600.0          # elastic run: Workbench "AlSi10Mg - E" (K per kN does not depend on E)
FC = (36.1464, 23.0)    # R10 fillet centre
ANG = math.radians(-120.0)
MOUTH = (FC[0] + 10 * math.cos(ANG), FC[1] + 10 * math.sin(ANG))
DIR = (math.cos(ANG), math.sin(ANG))   # crack extension direction (radial, into the boss)


def r30_centre():
    (x1, y1), (x2, y2), r = (-17.4989, 25.8740), (-6.5211, 46.3444), 30.0
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    h = math.sqrt(r * r - (d / 2) ** 2)
    c1 = (mx - dy / d * h, my + dx / d * h)
    c2 = (mx + dy / d * h, my - dx / d * h)
    return c1 if c1[0] > c2[0] else c2   # the centre lies inside the boss (right of the arc)


def exit_point():
    """Where the crack line meets the bottom edge from (-1.6232, -18.4854) to (210, -37)."""
    (x2, y2), (x3, y3) = (-1.6232, -18.4854), (210.0, -37.0)
    ex, ey = x3 - x2, y3 - y2
    det = DIR[0] * (-ey) + ex * DIR[1]
    s = ((x2 - MOUTH[0]) * (-ey) + ex * (y2 - MOUTH[1])) / det
    return MOUTH[0] + s * DIR[0], MOUTH[1] + s * DIR[1]


def deck(kind, a, case=None):
    rc = r30_centre()
    tip = (MOUTH[0] + a * DIR[0], MOUTH[1] + a * DIR[1])
    L = ['/BATCH', f'/TITLE,2D bracket, {kind}, crack a = {a} mm' + (f', {case}' if case else ''), '/PREP7',
         'ET,1,PLANE183,,,2          ! plane strain, per mm of thickness']
    if kind == 'elastic':
        L += [f'MP,EX,1,{E_EL}', 'MP,PRXY,1,0.33']
    else:
        rho, g = CASES[case]
        L += [f'MP,EX,1,{2 * g * 1.33:.1f}', 'MP,PRXY,1,0.33      ! label only; the USERMAT sets the stiffness',
              'TB,USER,1,1,7', 'TBTEMP,0', f'TBDATA,1,100,1.0E-4,{rho:.12g},{g:.12g},0.33,0', 'TBDATA,7,0',
              'TB,STATE,1,,4']
    kp = {1: (-21.5335, -16.5938), 2: (-1.6232, -18.4854), 3: (210.0, -37.0), 4: (210.0, 13.0),
          5: (36.1464, 13.0), 6: MOUTH, 8: (26.1464, 23.0), 9: (29.8505, 30.7693), 10: (163.3036, 138.9146),
          11: (210.0, 143.0), 12: (210.0, 193.0), 13: (170.1522, 189.5138), 14: (-6.5211, 46.3444),
          15: (-17.4989, 25.8740), 20: FC, 21: rc}
    if a > 0:
        # the crack line, continued to the bottom edge (kp 2-3), splits the section into the lower arm (area 1)
        # and the rest (area 2); the two crack faces are separate lines with coincident mouth keypoints 6 and 7,
        # and the ligament line from the tip (30) to the exit point (31) is shared, so the areas join only there.
        kp[7] = MOUTH
        kp[30] = tip
        kp[31] = exit_point()
    for k, (x, y) in kp.items():
        L.append(f'K,{k},{x:.6f},{y:.6f}')
    if a > 0:
        L += ['LARC,7,5,20,10', 'L,5,4', 'L,4,3', 'L,3,31', 'L,31,30', 'L,30,7',
              'L,31,2', 'L,2,1', 'L,1,15', 'LARC,15,14,21,30', 'L,14,13', 'L,13,12', 'L,12,11', 'L,11,10',
              'L,10,9', 'LARC,9,8,20,10', 'LARC,8,6,20,10', 'L,6,30',
              'AL,1,2,3,4,5,6', 'LSEL,S,LINE,,7,18', 'LSEL,A,LINE,,5', 'AL,ALL', 'LSEL,ALL',
              'CYL4,0,0,5', 'ASBA,2,3',
              'ESIZE,2', 'MSHAPE,1,2D']
        nl = max(4, int(round(a / 0.5)))
        L += [f'KSCON,30,{min(a / 4.0, 0.25):.4f},1,16,0.75     ! singular quarter-point elements at the crack tip',
              f'LESIZE,6,,,{nl}', f'LESIZE,18,,,{nl}']
    else:
        L += ['L,1,2', 'L,2,3', 'L,3,4', 'L,4,5', 'LARC,5,6,20,10', 'LARC,6,8,20,10', 'LARC,8,9,20,10',
              'L,9,10', 'L,10,11', 'L,11,12', 'L,12,13', 'L,13,14', 'LARC,14,15,21,30', 'L,15,1',
              'LSEL,ALL', 'AL,ALL', 'CYL4,0,0,5', 'ASBA,1,2', 'ESIZE,2', 'MSHAPE,1,2D']
    L += ['AMESH,ALL', 'ALLSEL,ALL']
    if a > 0:
        L += ['KSEL,S,KP,,30', 'NSLK,S', 'CM,CRACKTIP,NODE', 'ALLSEL,ALL',
              f'LOCAL,11,0,{tip[0]:.6f},{tip[1]:.6f},0,{math.degrees(ANG):.3f}', 'CSYS,0']
    u = 0.1 if kind == 'elastic' else 2.0
    L += ['NSEL,S,LOC,X,209.999,210.001', 'CM,SUPPORT,NODE', 'D,ALL,ALL', 'ALLSEL,ALL',
          'CSYS,1', 'NSEL,S,LOC,X,4.999,5.001', 'NSEL,R,LOC,Y,-0.001,180.001', 'CM,BORETOP,NODE', 'CSYS,0',
          f'D,ALL,UY,{u}', 'ALLSEL,ALL', 'FINISH', '/SOLU', 'ANTYPE,0']
    if kind == 'elastic':
        if a > 0:
            L += ['CINT,NEW,1', 'CINT,CTNC,CRACKTIP', 'CINT,NORM,11,2', 'CINT,TYPE,SIFS', 'CINT,NCON,6']
        L += ['OUTRES,ALL,ALL', 'SOLVE', 'FINISH', '/POST1', 'SET,LAST', 'CMSEL,S,SUPPORT', 'FSUM',
              '*GET,_FY,FSUM,0,ITEM,FY', 'ALLSEL,ALL', '_K=0', '*DIM,_KC,ARRAY,6']
        if a > 0:
            L += ['CMSEL,S,CRACKTIP', '*GET,_NT,NODE,0,NUM,MIN', 'ALLSEL,ALL',
                  '*DO,_C,1,6', '*GET,_KC(_C),CINT,1,CTIP,_NT,CONT,_C,DTYPE,K1', '*ENDDO']
        L += ['*CFOPEN,crack_result,csv', "*VWRITE", "('a_mm,FY_N_per_mm,K1_c1,K1_c2,K1_c3,K1_c4,K1_c5,K1_c6')",
              f'*VWRITE,{a},_FY,_KC(1),_KC(2),_KC(3),_KC(4),_KC(5),_KC(6)',
              "(F8.3,',',E15.7,',',E15.7,',',E15.7,',',E15.7,',',E15.7,',',E15.7,',',E15.7)", '*CFCLOS', 'FINISH']
    else:
        L += ['NLGEOM,OFF', 'AUTOTS,ON', 'NSUBST,40,10000,20', 'LNSRCH,ON', 'NEQIT,50', 'OUTRES,ERASE', 'OUTRES,ALL,ALL', 'OUTRES,SVAR,ALL',
              'SOLVE', 'FINISH', '/POST1', '*GET,_NS,ACTIVE,0,SET,NSET', '*CFOPEN,crack_history,csv',
              "*VWRITE", "('set,time,uy_mm,FY_N_per_mm')", '*DO,_I,1,_NS', 'SET,,,,,,,_I',
              '*GET,_T,ACTIVE,0,SET,TIME', 'CMSEL,S,SUPPORT', 'FSUM', '*GET,_FY,FSUM,0,ITEM,FY', 'ALLSEL,ALL',
              '_U=2*_T', '*VWRITE,_I,_T,_U,_FY', "(F6.0,',',E15.7,',',E15.7,',',E15.7)", '*ENDDO', '*CFCLOS',
              'FINISH']
    return '\n'.join(L) + '\n'


def main():
    out = Path(sys.argv[1])
    n = 0
    for a in A_MM:
        jobs = [('elastic', None)] + [('usermat', c) for c in CASES]
        for kind, case in jobs:
            d = out / (f'{kind}_a{a:g}' if kind == 'elastic' else f'{kind}_{case}_a{a:g}')
            d.mkdir(parents=True, exist_ok=True)
            (d / 'crack.dat').write_text(deck(kind, a, case), newline='\n')
            n += 1
    print(n, 'decks; mouth', tuple(round(v, 3) for v in MOUTH), 'R30 centre', tuple(round(v, 3) for v in r30_centre()))


if __name__ == '__main__':
    main()
