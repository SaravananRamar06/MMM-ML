"""Reload the final model and show case 42 plus its residual; no fitting occurs."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data import build, STRAIN_GRID

ids, X, Y, _ = build(target='Svm')
i = int(np.flatnonzero(ids == 42)[0])
prediction = joblib.load(ROOT / 'runs/score/final_Svm/model.joblib').predict(X[i:i+1])[0]
residual = prediction - Y[i]
rmse = float(np.sqrt(np.mean(residual ** 2)))
assert np.isclose(rmse, 0.10614619878284123, rtol=1e-10)
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True,
                         gridspec_kw={'height_ratios': [3, 1]}, layout='constrained')
axes[0].plot(STRAIN_GRID, Y[i], color='#506477', lw=4, alpha=.65, label='Supplied simulation')
axes[0].plot(STRAIN_GRID, prediction, color='#be643c', lw=2, ls='--', label='Saved MLP prediction')
axes[0].set_ylabel('von Mises stress (inferred MPa)')
axes[0].legend(frameon=False)
axes[0].set_title(f'Case 42 · excluded from final fitting · curve RMSE {rmse:.6f}\n'
                  'T=100, rate=1e−4, density=2619, G=23313.95 (units unconfirmed)')
axes[1].plot(STRAIN_GRID, residual, color='#be643c', lw=1.7)
axes[1].axhline(0, color='#506477', lw=.8)
axes[1].set_ylabel('Prediction − truth\n(inferred MPa)')
axes[1].set_xlabel('Axial strain E11')
for ax in axes:
    ax.grid(alpha=.18)
fig.supxlabel('Comparison with one supplied simulation; earlier test exposure disclosed. Not physical or lift validation.', fontsize=9)
destination = ROOT / 'figures/demo_case42.png'
fig.savefig(destination, dpi=160)
print(f'case=42 RMSE={rmse:.12f}; figure={destination.relative_to(ROOT)}')
print('stress at exactly strain .05 (linear interpolation of the common grid):',
      float(np.interp(.05, STRAIN_GRID, Y[i])), float(np.interp(.05, STRAIN_GRID, prediction)))
