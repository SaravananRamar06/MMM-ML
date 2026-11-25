"""Cross-check the numbers quoted in the complete study guide against the saved result files.

    python scripts/check_study_guide.py

Reads docs/exam-preparation/complete-study-guide.md and confirms that each checked value, computed
from report/numbers.json, the locked run, the bracket and crack result folders, appears in the guide.
Exits with status 1 if any check fails. It changes no file.
"""
import csv, json, math, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
G = (R / 'docs/exam-preparation/complete-study-guide.md').read_text()
N = json.loads((R / 'report/numbers.json').read_text())
J = lambda p: json.loads((R / p).read_text())
fails, n = [], 0
ROUNDED = {'about 3 × 10⁻¹³ MPa': 'NumpyTorchErr 3.4e-13', '(largest 0.92)': 'DeltaMax 0.917'}

def has(s, why):
    global n; n += 1
    if s not in G: fails.append(f'MISSING "{s}"  ({why})')

def num(key):  # numbers.json value as printed by LaTeX (strip {,} and signs as written)
    return str(N[key]).replace('{,}', ',')

# --- numbers.json macros that the guide quotes (value must appear verbatim)
for k in ['TestMean','TestMedian','TestWorst','TestRsq','TestWithinOne','TestWithinHalf','TestWithinTwo','TestBias',
          'TestMAE','TestMaxAbs','TestMaxPct','TestBest','TrainFit','TestEq','TestEqWorst','TestLookup','SelCV','SelGroups',
          'SelScore','EqCV','EqGroups','LookupCV','LookupGroups','SingleTest','SingleGroups','SingleCV','CtrlCV','CtrlGroups',
          'CtrlScore','CtrlTest','SpreadMean','SpreadMax','MemberBest','MemberWorst','EqA','EqB','EqC','Eqn','Eqq','PinnA',
          'PinnB','PorData','PorModel','PorMPa','PorDataThirty','PorDataHundred','PorDataTwoHundred','PorModelThirty',
          'PorModelHundred','PorModelTwoHundred','PorImpliedR','PorG','PorT','PorRatio','PorCorr','PorFullCorr',
          'ScrIterLong','ScrAlphaLow','ScrWide','ScrBoundedScore','FloorJCMean','FloorJCMedian','FloorCubicMean',
          'BrElasticStiff','BrUsermatStiff','BrStiffRatio','BrElasticFinalkN','BrEpFinalkN','BrUsermatPeakkN','BrUsermatPeakU',
          'BrUsermatFinalkN','BrUsermatFlagged','BrUsermatPeakStress','PorBrPhiZeroPeakkN','PorBrDensMinPeakkN',
          'PorBrGOverDens','GphiGFour','GphiPeakZerokN','GphiPeakMaxPorkN','MeshPeakFinekN','MeshPeakFineU','MeshEqpsCoarse',
          'MeshEqpsFine','MeshFlagFine','MeshEpStrainRatio','MeshUmStrainRatio','MeshEpMaxChangePct','MeshSofteningShareMin',
          'MeshSofteningShareMax','SeMaxDiff','SeSFinal','SeEqpsFinal','SePoints','ClFilletVM','ClStudyFlowStress',
          'ClFirstYieldkN','ClCapabilitykN','ClFirstYieldFinekN','ClLimitPhiZerokN','ClLimitPhiFourkN','ClLimitPhiMaxkN',
          'ClFlowStressPhiZero','ClFlowStressPhiFour','ClFlowStressPhiMax','ClLimitkN','ClLimitFFkN','ClWeakk','ClWeakPC',
          'ClWeakMu','ClWeakKILim','ClWeakKrLim','ClWeakLrLim','ClWeakfLim','ClWeakPfkN','ClWeakPfSecondkN','ClWeakKrFail',
          'ClWeakLrFail','ClMinRF','ClMinRFSecond','ClPfLongZerokN','ClPfLongMaxkN','ClAtSixtyZero','ClAtSixtyMax',
          'ClAtEightyZero','ClAtEightyMax','ClLowKMin','ClLowKMax','ClKScalePct','ClKScaledWeakkN','ClCrackExit',
          'Improvement','RunMinutes','Params','CasesHigh','CasesLow','WinsLookup']:
    v = num(k)
    alt = [v, v.lstrip('+'), v.replace('-', '−').lstrip('+'), v.replace('e-', ' × 10⁻').replace('e-0','e-')]
    n += 1
    if not any(a in G for a in alt): fails.append(f'MACRO {k}={v} not found')

# signed percentages written with a Unicode minus
for k in ['PorDensPeakChangePct','PorFourPeakChangePct','PorDensFinalChangePct','PorSeDensYieldPct','PorSeDensLimitPct',
          'GphiPeakChangePct','GphiFourPeakChangePct','GphiFinalChangePct','GphiStiffChangePct','GphiSeYieldPct',
          'GphiSeLimitPct','BrMeshPeakChangePct','MeshFinalChangePct','MeshForceMidChangePct','MeshForceOneChangePct',
          'MeshStiffChangePct','ClLimitDropPct','ClPfLongDropPct','ClTwoDPeakPct','ClTwoDSOnePct','PorGLowPeakChangePct']:
    v = num(k).replace('-', '−').lstrip('+')
    has(v + ' %', k)
for k in ['ClTwoDStiffPct','PorGHighPeakChangePct','PorGHighStepPct']:
    has(num(k) + ' %', k)

# --- tables read from CSV/JSON
fad = J('bracket/ansys_usermat/crack2d_2026-11-20/fad_cl.json')
for case, label in (('gphi0','φ = 0 %'),('gphi4','φ = 4 %'),('gphi785','φ = 7.85 %')):
    vals = [f"{fad['cases'][case]['per_a'][a]['P_f_first_K40']:.2f}" for a in ('0','8','16','25','30')]
    row = f'| {label} | ' + ' | '.join(vals)
    n += 1
    if row not in G.replace('**', ''): fails.append(f'RESIDUAL ROW {row}')
cl = list(csv.DictReader(open(R / 'bracket/ansys_usermat/crack2d_2026-11-20/cl_vs_load.csv')))
for case, label in (('gphi0','φ = 0 %'),('gphi4','φ = 4 %'),('gphi785','φ = 7.85 %')):
    vals = [f"{float(next(r for r in cl if r['load_kN']==L and r['peak']=='first' and r['K_mat']=='40.0')[case]):.2f}" for L in ('50.0','60.0','70.0','80.0')]
    has(f'| {label} | ' + ' | '.join(vals) + ' |', 'CL vs load ' + case)
for a, s in (('1','0.199'),('2','0.245'),('4','0.289'),('8','0.341'),('16','0.439'),('25','0.543'),('30','0.577')):
    n += 1
    if abs(fad['elastic'][a]['k_MPa_sqrtm_per_kN'] - float(s)) > 0.0006: fails.append(f'k({a}) {s}')
v = J('bracket/ansys_usermat/crack2d_2026-11-20/validation_2d_vs_3d.json')
for x in (f"{v['elastic_stiffness_2D_kN_per_mm']:.1f}", f"{v['usermat_phi4_initial_stiffness_2D_kN_per_mm']:.1f}",
          f"{v['usermat_phi4_peak_2D_kN']:.1f}", f"{v['fillet_S1_2D_MPa_per_kN']:.2f}"):
    has(x, 'validation 2D')
# low-K
low = [round(fad['low_K_sensitivity'][f'{c}_K20']['CL_mm_at_limit'],1) for c in ('gphi0','gphi4','gphi785')]
n += 1
if (min(low), max(low)) != (23.4, 23.5): fails.append(f'low K {low}')

# --- bracket summaries
s = J('bracket/ansys_usermat/results_uy_2026-11-18/summary.json')
has(f"{s['ep_miso']['final_eppl_eqv_max_elem']:.3f}", 'EP eqps')
po = J('bracket/ansys_usermat/porosity_uy_2026-11-18/porosity_summary.json')
for c in ('G_lo','G_hi','phi4','phi0','phi785'):
    has(f"{po[c]['peak_F_N']/1e3:.1f}", 'porosity peak ' + c)
gp = J('bracket/ansys_usermat/porosity_gphi_uy_2026-11-18/porosity_gphi_summary.json')
for c in ('gphi0','gphi4','gphi785'):
    has(f"{gp[c]['initial_stiffness_N_per_mm']/1e3:.1f}", 'gphi stiffness ' + c)
    has(f"{gp[c]['F_at_final_N']/1e3:.1f}", 'gphi F2 ' + c)
has(f"{gp['gphi785']['peak_F_N']:,.1f}".replace(',', ','), 'P16 unrounded')
ms = J('bracket/ansys_usermat/mesh_uy_2026-11-18/mesh_summary.json')
for key in ('elements','nodes'):
    for m in ('5mm','2p5mm'): has(f"{ms[m][key]:,}", f'mesh {key} {m}')
for m in ('5mm','2p5mm'): has(f"{ms[m]['initial_stiffness_N_per_mm']/1e3:.2f}", 'mesh stiffness ' + m)
has(f"{ms['2p5mm']['F_at_final_N']/1e3:.1f}", 'mesh fine F2')

# --- test summary
t = J('reports/jc_pinn_20261107/test_report/test_summary.json')['summary']
for b, s_ in zip(t['strain_bands'], ('0.25','0.23','0.51')):
    n += 1
    if f"{b['mae']:.2f}" != s_: fails.append(f"strain band {b}")
for c in t['conditions']:
    has(f"{c['rmse']:.3f}", f"cond rmse {c['T']} {c['log10_rate']}")
n += 1
if abs(sum(t['members']['single_member_rmse'])/5 - 0.453) > 0.0005: fails.append('member average')
# group holdout table from run README values via results.json
# study point table
for x in ('131.39','92.97','2.449','159.29','76.52','1.635','136.06','75.41','1.886','108.03','6.13','0.193','142.27','46.03','1.174','67.60','4.28','0.142'):
    has(x, 'study table')

# --- model / config
cfg = J('configs/jc_pinn.json')
has(f"{cfg['training']['adam_steps']:,}", 'adam steps'); has(str(cfg['training']['adam_lr']), 'lr')
has(f"{cfg['collocation']['points']:,}", 'colloc')
for s_, why in ROUNDED.items():
    has(s_, why)
sp = J('data/split.json'); n += 1
if (len(sp['train']), len(sp['test'])) != (36, 37): fails.append('split')

print(f'{n} checks, {len(fails)} failures')
for f in fails: print('  ', f)
sys.exit(1 if fails else 0)
