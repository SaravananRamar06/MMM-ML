# Technical Reference & Intuitive Architecture Guide: AlSi10Mg Flow-Stress Neural Surrogate Model

**Material Lab Project Team**  
*User, Gemini (Antigravity), Codex, OpenCode, Claude*  
*Date: October 25, 2026*

---

## Guide Purpose & Plain-Language Overview
This document serves as an accessible, end-to-end technical reference for understanding, defending, and querying the neural surrogate model developed for AlSi10Mg additive manufacturing simulations. It breaks down how neural networks, weights, and $\tanh$ activations function intuitively, traces a worked step-by-step mathematical prediction, documents the verified 5-network ensemble architecture (1,925 total parameters, 0.059085 holdout RMSE), explains the generalization spectrum, and provides plain-language answers for academic viva defense.

### What the Model Does
Additive manufacturing of metallic parts (such as aerospace brackets) produces material whose stiffness and flow stress vary across different thermal and strain-rate conditions. Running a full numerical finite-element simulation for every new loading condition can take minutes or hours.

**The Surrogate Solution:** Given four environmental conditions (temperature, strain rate, density, shear modulus) and an axial strain point ($E_{11}$), the surrogate model calculates the corresponding flow stress curve in 0.22 milliseconds—reproducing the simulated response with high numerical fidelity within represented conditions.

### How Neural Networks, Weights, and Tanh Work
The surrogate model is an empirical function approximator equipped with 385 adjustable parameters per network:
- **Inputs:** Features like temperature and strain act as input signals. Because raw numerical magnitudes differ widely (e.g., $G \sim 24,000$ while strain $\sim 0.05$), we standardize them first so inputs have zero mean and unit variance.
- **Weights:** Each connection between layers has a numerical weight multiplier. Input influences combine nonlinearly across all layers rather than a single weight directly equaling physical sensitivity.
- **Biases:** Each neuron has an added constant offset (bias) that sets its baseline pre-activation value.
- **Tanh Activation:** Each neuron passes its pre-activation sum through a hyperbolic tangent ($\tanh$) activation function, which maps values smoothly to $(-1, 1)$. This introduces the nonlinearity required to fit smooth continuous response surfaces.
- **Ensemble Averaging:** Rather than relying on a single network, we train five identical networks initialized with different random seeds. Taking their average smooths out individual fitting variations and produces a stable consensus prediction.

---

## 1. Tracing a Step-by-Step Prediction (Worked Numerical Example)
To demystify the internal math, let us trace an exact prediction using the calibrated parameters from the production runtime.

We evaluate a material specimen under the following query inputs:
- **Temperature ($T$):** $100.0$ (inferred $^\circ\text{C}$ units)
- **Strain Rate ($\dot{\varepsilon}$):** $10^{-4}$ (inferred $\text{s}^{-1}$ units) $\longrightarrow \log_{10}(\text{rate}) = -4.0$
- **Density ($\rho$):** $2619.0$ (inferred units)
- **Shear Modulus ($G$):** $24541.0$ (inferred units)
- **Axial Strain ($E_{11}$):** $0.049631$ (grid point closest to $0.05$)

### Step A: Standardization (Z-Score)
Using the training set mean and standard deviation (fitted on 4,320 training samples):
$$z = \frac{\text{raw\_input} - \mu}{\sigma}$$
- $T$: $(100.0 - 107.22) / 68.09 = \mathbf{-0.1061}$
- $\log_{10}(\text{rate})$: $(-4.0 - (-3.92)) / 0.829 = \mathbf{-0.1005}$
- Density: $(2619.0 - 2598.71) / 89.26 = \mathbf{+0.2273}$
- Shear Modulus $G$: $(24541.0 - 24371.98) / 850.39 = \mathbf{+0.1988}$
- Strain $E_{11}$: $(0.049631 - 0.05005) / 0.02902 = \mathbf{-0.0144}$

### Step B: Five-Network Ensemble Forward Evaluation
The standardized vector $[-0.1061, -0.1005, 0.2273, 0.1988, -0.0144]$ passes through the two hidden $\tanh$ layers of each network. The standardized outputs produced by the five committee networks are:
- Network 0 (Seed 0): $z_0 = \mathbf{+0.068864}$
- Network 1 (Seed 1): $z_1 = \mathbf{+0.071352}$
- Network 2 (Seed 2): $z_2 = \mathbf{+0.066148}$
- Network 3 (Seed 3): $z_3 = \mathbf{+0.066717}$
- Network 4 (Seed 4): $z_4 = \mathbf{+0.067810}$

### Step C: Ensemble Averaging & Unscaling
1. **Average Standardized Output:**
   $$z_{\text{avg}} = \frac{0.068864 + 0.071352 + 0.066148 + 0.066717 + 0.067810}{5} = \mathbf{+0.068178}$$
2. **Inverse Scaling to Inferred Stress Units** (training target mean $\mu_y = 97.7665$, target standard deviation $\sigma_y = 27.3756$):
   $$\hat{\sigma} = z_{\text{avg}} \cdot \sigma_y + \mu_y = 0.068178 \cdot 27.3756 + 97.7665 = \mathbf{99.6329}\text{ (inferred stress units)}$$
3. **Exact Interpolation to $E_{11} = 0.05000$:**
   $$\hat{\sigma}(0.05) = \mathbf{99.4186}\text{ (inferred stress units)}$$

---

## 2. Training vs. Inference, L-BFGS & Regularization
It is essential to distinguish between the two distinct lifecycle phases of the model:
- **Training Phase:** The fitting phase where the algorithm determines the 385 numerical weights per network. Using the L-BFGS optimizer on the 4,320 training grid points, training completes in **25.0 seconds** for all 5 networks.
- **Inference Phase:** The operational deployment phase. The weights are frozen into an 18 KB NPZ file. Calculating a full 120-point curve requires only matrix multiplications and $\tanh$ evaluations, taking **0.221 milliseconds**.

### L-BFGS and L2 Regularization ($\alpha = 0.001$)
- **L-BFGS Optimizer:** For moderately sized tabular datasets (4,320 samples), L-BFGS (a quasi-Newton 2nd-order method) uses gradient history to approximate the Hessian curvature, efficiently converging to a local minimum on the empirical loss surface without convergence warnings.
- **L2 Regularization ($\alpha = 0.001$):** L2 weight regularization penalizes large weight magnitudes, discouraging rapid oscillation between query coordinates.

---

## 3. Dataset Provenance & Case-Level Splitting
The simulation dataset contains **73 complete flow-stress histories**. The underlying finite element files contain **2,197,000 raw rows** (1,224,000 in the training cases, 973,000 in the holdout cases). These raw rows represent output time-steps, not independent data samples. Each simulation curve is interpolated onto a standardized **120-point axial strain grid**.
- **Training Queries:** Fitting operates on **4,320 query samples** ($36\text{ cases} \times 120\text{ strain points}$).
- **Holdout Queries:** Evaluation operates on **4,440 query samples** ($37\text{ cases} \times 120\text{ strain points}$).

### Why We Split by Case, Not by Row
If data were partitioned randomly by row, neighboring strain coordinates from the same simulation curve would appear in both partitions, yielding heavily overoptimistic evaluation scores. By partitioning strictly by simulation ID, the holdout set evaluates how well the model predicts entirely separate simulation histories.

**Prior Exploration Disclosure:** The split was established using a reproducible pseudo-random seed on simulation IDs (36 train, 37 test). Standardizers were fitted strictly on the 4,320 training grid queries. Earlier all-data exploration and feature selection were conducted on the dataset. The final split is a disjoint case partition rather than an untouched blind benchmark.

### Compact Operational Input Range Table
Summary of valid operational ranges inside the training domain. Note: Units are inferred and generalization on unseen condition combinations is not guaranteed:

| Feature | Physical Range | Internal Encoding | Inferred Unit | Operational Guidance |
| :--- | :--- | :--- | :--- | :--- |
| **Temperature ($T$)** | 30.0 .. 200.0 | 30.0 .. 200.0 | °C (inferred) | Strictly [30, 200]; 300 °C extrapolation invalid |
| **Strain Rate** | 1e-5 .. 1e-3 | -5.0 .. -3.0 | s^-1 (inferred) | Always log10-transformed before network input |
| **Density ($\rho$)** | 2488.05 .. 2700.0 | 2488.05 .. 2700.0 | kg/m³ (inferred) | Minor sensitivity (~0.19 units); no porosity link |
| **Shear Modulus ($G$)** | 23313.95 .. 25300.0 | 23313.95 .. 25300.0 | MPa (inferred) | Numeric stiffness input; no porosity proxy |
| **Axial Strain ($E_{11}$)** | 0.0002 .. 0.0999 | 0.0002 .. 0.0999 | Strain | Standardized 120-point monotonic loading grid |

---

## 4. Three-Tier Verification & Generalization Metrics
1. **Tier 1 (Cache Verification):** The 120-point interpolated grid for all 73 curves was audited against raw `STR_STR.OUT` files and SHA256 hashes. Maximum absolute difference = **0.0**.
2. **Tier 2 (Holdout Artifact Reload):** Evaluating the frozen ensemble on the 37 holdout cases reproduced the exact saved metrics: Mean Test RMSE = **0.05908515** (worst case: **0.11330618**, Case 45).
3. **Tier 3 (Same-Environment Reproduction):** A completely independent refit of all five seeds on the 36 training cases took **25.0 seconds**, producing zero warnings and reproducing all weights and predictions with **0.0 maximum absolute difference**.

| Evaluation Regime | Metric | Value (Inferred Stress Units) | Context / Interpretation |
| :--- | :--- | :--- | :--- |
| **Holdout Test Set (37 cases)** | Mean RMSE | **0.059085** | Within-condition interpolation fidelity |
| **Holdout Test Set** | Worst RMSE | **0.113306** | Case 45 ($T=100$, rate=$10^{-4}$) |
| **Training Case CV (36 cases)** | Mean RMSE | **1.158263** | Cross-case variability across folds |
| **Training Case CV** | Median RMSE | **0.201877** | Half of training cases have RMSE $\le 0.201877$ |
| **Leave-Condition-Out (LOCO)** | Mean of Conds | **6.793603** | Average generalization to unseen conditions |
| **Leave-Condition-Out (Hot/Slow)** | Condition Mean | **23.525129** | $200^\circ\text{C}, 10^{-5}\,\text{s}^{-1}$ extreme corner |

### Understanding the Generalization Spectrum
Root Mean Squared Error measures average prediction error along curve points. Why is Test RMSE 0.059 while Leave-Condition-Out RMSE is 6.79?
- **Within-Condition Interpolation (0.059 RMSE):** All 8 temperature and strain-rate combinations in the test set exist in the training set. The model is interpolating along smooth curves for known conditions, yielding near-zero error (0.059).
- **Unseen Condition Generalization (6.79 - 23.53 RMSE):** When an entire operating condition is held out, the model must predict without anchor curves. Held-out interior levels (e.g., $100^\circ\text{C}, 10^{-4}\,\text{s}^{-1}$) represent interpolation to unseen conditions (RMSE ~5.2). Boundary corners (e.g., $200^\circ\text{C}, 10^{-5}\,\text{s}^{-1}$) represent extrapolation across extreme edges, where condition mean error reaches 23.53.

**The Case 60 Anomaly:** In training cross-validation, Case 60 exhibits high error ($\text{RMSE} = 25.99$). Its recorded von Mises strain reverses while axial strain $E_{11}$ increases. The generating cause of this behavior is unknown. It is retained and flagged as genuine evidence of limited generalization under irregular yield behavior.

---

## 5. Runtime Performance & Benchmarks
An optimized NumPy-only runtime was developed (`src/query_runtime.py`) to eliminate the heavy scikit-learn dependency:
- **Weight Storage:** Stored in an 18,462-byte pickle-free `.npz` file (vs 62,940 bytes Joblib bundle).
- **Full-Curve Latency:** **0.221 ms** (NumPy) vs **0.511 ms** (scikit-learn) for full 120-point curve prediction in local repeated single-thread benchmarks.
- **Cold Startup Time:** **163 ms** (NumPy) vs **976 ms** (scikit-learn).
- **Full-Batch Caveat:** On full-batch evaluation (73 cases), scikit-learn took **17.3 ms** vs NumPy **21.8 ms** under identical single-thread BLAS settings.
- **Accuracy Parity:** Exactly **0.0 max absolute difference** against reference model outputs across all 73 curves.

---

## 6. Verified Executable Code Example
The following code loads the lightweight NumPy runtime, runs inference on a test case, and queries a point:

```python
import numpy as np
from src.query_runtime import QueryRuntime

# 1. Load lightweight runtime (18 KB pickle-free NPZ)
runtime = QueryRuntime.load("runs/score/final_Svm/model_numpy.npz")

# 2. Define input case: [T, log10(strain_rate), density, shear_modulus]
X_case = np.array([[100.0, -4.0, 2619.0, 24541.0]])

# 3. Predict full 120-point flow-stress curve
curve = runtime.predict(X_case)[0]
print(f"Curve shape: {curve.shape}")  # (120,)

# 4. Query stress at a specific strain point (e.g., E11 = 0.05)
stress_at_point = np.interp(0.05, runtime.strain, curve)
print(f"Flow Stress at E11=0.05: {stress_at_point:.4f} (inferred units)")
```

---

## 7. Exact Reproducible Commands & Evidence Paths
All findings and metrics in this report can be independently audited using the following commands:

```bash
# 1. Audit raw simulation rows, cache integrity, and saved model reload:
.venv/bin/python reports/verify_final_model.py

# 2. Reproduce fresh training across all 5 seeds from scratch (25.0s):
.venv/bin/python reports/reproduce_final_training.py

# 3. Run test suite (13 model, parser, and runtime tests):
.venv/bin/python -m unittest discover -s tests -p "test_*.py" -v

# 4. Run single-curve and batch runtime benchmarks:
.venv/bin/python reports/benchmark_query_runtime.py
```

**Artifact Provenance:**
- `reports/model_verification_20261025.json` (Audit results and metrics)
- `reports/final_training_reproduction_20261025.json` (Refit timing and weight parity)
- `reports/query_runtime_benchmark_20261025.json` (Latency and file size measurements)

---

## 8. Operational Boundaries & Viva Defense Q&A Guide
- **Q1: What are the units of your predicted stress?**  
  *Answer:* The raw simulation files report stress without explicit unit headers. The model predictions are evaluated in inferred stress units ($\text{RMSE} = 0.059$). While numerically consistent across all profiles, we explicitly treat them as inferred stress units rather than confirmed MPa until the simulator's exact constitutive definitions are verified.
- **Q2: Does your model predict true plastic strain?**  
  *Answer:* No. The input variable is $E_{11}$, which is the operational axial strain coordinate reported by the simulation output, not verified true plastic strain.
- **Q3: Can your model predict flow stress at 300 °C?**  
  *Answer:* No. The training data strictly spans $30^\circ\text{C}$ to $200^\circ\text{C}$. Unconstrained MLPs predict unphysical negative stress when extrapolated to $300^\circ\text{C}$. Operational use must strictly remain within $[30^\circ\text{C}, 200^\circ\text{C}]$.
- **Q4: Can this model predict wing-rib bracket aerodynamic lift ($C_L$)?**  
  *Answer:* No. This is a material-level flow-stress surrogate along the supplied uniaxial loading family. The simulation matrix models constitutive stress-strain histories, not aerodynamic coefficients. No bracket structural FEA integration has been validated.
- **Q5: Can you claim zero data leakage?**  
  *Answer:* We claim a strictly disjoint case partition for final fitting and evaluation. However, earlier all-data exploration and feature selection were conducted on the dataset. We maintain scientific honesty by reporting this exploration rather than claiming an untouched blind holdout.
