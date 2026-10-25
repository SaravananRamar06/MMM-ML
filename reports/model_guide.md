# Technical Reference & Architecture Guide: AlSi10Mg Flow-Stress Neural Surrogate Model

**Material Lab Project Team**  
*User, Gemini (Antigravity), Codex, OpenCode, Claude*  
*Date: October 25, 2026*

---

## Abstract & Plain-Language Motivation
This guide provides a comprehensive, technically rigorous, and accessible personal reference for the AlSi10Mg flow-stress surrogate model. It documents the problem physics, data representations, the ensemble neural network architecture (five 5–16–16–1 $\tanh$ MLPs, 385 parameters each, 1,925 total), training procedure (L-BFGS, $\alpha=0.001$), 3-tier reproducibility audits, verified test performance (mean curve RMSE **0.059085** in inferred stress units), optimized NumPy runtime benchmarks (**0.221 ms** single-curve inference), operational boundaries, and a defense-oriented viva preparation guide.

### What the Model Does
Given temperature, nominal strain rate, material density, shear modulus, and an operational axial strain point ($E_{11}$), the model predicts the corresponding flow stress. Within represented conditions, it reproduces non-linear plastic yield curves with sub-millisecond latency.

---

## 1. Dataset, Feature Pipeline & Partitioning

### Dataset Provenance & Row Counts
The simulation matrix comprises **73 available histories**. The raw source data contains 2,197,000 observation rows:
- **Training Partition (36 cases):** 1,224,000 raw source rows.
- **Holdout Partition (37 cases):** 973,000 raw source rows.

> **Important Provenance Note:** The raw row counts represent the size of underlying finite element output files, not independent training examples. For surrogate modeling, each simulation curve is interpolated onto a standardized **120-point operational strain grid**.
> - **Fitting operates on 4,320 query samples** ($36 \text{ cases} \times 120 \text{ points}$).
> - **Evaluation operates on 4,440 query samples** ($37 \text{ cases} \times 120 \text{ points}$).

### Input Features & Numerical Ranges
Inside the network, each sample is mapped as a 5-dimensional vector:
$$\mathbf{x} = \begin{bmatrix} T \\ \log_{10}(\dot{\varepsilon}) \\ \rho \\ G \\ E_{11} \end{bmatrix} \longrightarrow y = \hat{\sigma}$$

1. **$T$ (Temperature):** Numerical range $30.0$ to $200.0$ ($^\circ\text{C}$).
2. **$\dot{\varepsilon}$ (Strain Rate):** Nominal values $10^{-5}$ to $10^{-3}\,\text{s}^{-1}$, always encoded logarithmically: $\log_{10}(\dot{\varepsilon}) \in [-5.0, -3.0]$. Raw strain rate is not passed without logarithmic transformation.
3. **$\rho$ (Density):** Numerical range $2488.05$ to $2700.0$ (presumably $\text{kg/m}^3$; units unconfirmed).
4. **$G$ (Shear Modulus):** Numerical range $23313.95$ to $25300.0$ (presumably $\text{MPa}$; units unconfirmed).
5. **$E_{11}$ (Operational Axial Strain):** Standardized 120-point grid spanning the monotonic loading trajectory.

#### Physical Caveats on Inputs:
- **Unconfirmed Units:** Units for $G$ and $\rho$ are not explicitly defined in the simulation headers.
- **No Porosity Mapping:** Neither $G$ nor $\rho$ has a validated physical porosity relationship in this dataset. Density varies stress by only $\sim 0.19$ units. Do not claim a direct porosity-to-lift mapping.

### Dataset Partitioning & Evaluation Disclosure
The split was established using a reproducible pseudo-random seed on simulation IDs ($36$ train, $37$ test).
- **Standardization Scope:** The input standardizer ($\boldsymbol{\mu}, \boldsymbol{\sigma}$) and target standardizer ($\mu_y, \sigma_y$) were fitted strictly on the 4,320 training grid queries.
- **Prior Exploration Disclosure:** While the final model fitting partition was strictly disjoint, earlier exploratory model selection was conducted on the full dataset before the final split was frozen. Therefore, the test set should be described as a *disjoint holdout split*, not an untouched or completely blind benchmark.

---

## 2. Model Architecture & Training

### The 5-Network Query MLP Ensemble
The surrogate model is an ensemble of **five independently initialized multi-layer perceptrons** ($k \in \{0, 1, 2, 3, 4\}$). Each network shares an identical 5–16–16–1 architecture:
- **Input Layer ($D=5$):** Standardized vector $\tilde{\mathbf{x}} = (\mathbf{x} - \boldsymbol{\mu}) / \boldsymbol{\sigma}$.
- **Hidden Layer 1:** 16 neurons with hyperbolic tangent ($\tanh$) activation.
  - Weights: $16 \times 5 = 80$, Biases: $16$. Subtotal: 96 parameters.
- **Hidden Layer 2:** 16 neurons with hyperbolic tangent ($\tanh$) activation.
  - Weights: $16 \times 16 = 256$, Biases: $16$. Subtotal: 272 parameters.
- **Output Layer:** 1 linear neuron (identity activation).
  - Weights: $1 \times 16 = 16$, Bias: $1$. Subtotal: 17 parameters.
- **Parameter Total:** Exactly **385 trainable parameters per network**, totaling **1,925 parameters** across the 5-network ensemble.

### Mathematical Formulation
For network $k$, the standardized predicted stress $\hat{z}_k$ is:
$$\hat{z}_k = \mathbf{W}_3^{(k)} \cdot \tanh\left( \mathbf{W}_2^{(k)} \cdot \tanh\left( \mathbf{W}_1^{(k)} \cdot \tilde{\mathbf{x}} + \mathbf{b}_1^{(k)} \right) + \mathbf{b}_2^{(k)} \right) + b_3^{(k)}$$

The ensemble average across all 5 networks is unscaled using the training target mean $\mu_y$ and standard deviation $\sigma_y$:
$$\hat{\sigma} = \left( \frac{1}{5} \sum_{k=0}^4 \hat{z}_k \right) \cdot \sigma_y + \mu_y$$

### Training Procedure
- **Optimizer:** L-BFGS (quasi-Newton method, highly efficient for smooth non-linear parameter fitting on moderately sized tabular grids).
- **Regularization:** $L_2$ penalty $\alpha = 0.001$.
- **Loss Function:** Mean Squared Error (MSE) on standardized training queries.
- **Seeds:** Five deterministic seeds ($0, 1, 2, 3, 4$).

---

## 3. Verification, Reproducibility & Metrics

### Three-Tier Verification Hierarchy
1. **Tier 1: Cache Verification (Zero Discrepancy)**
   The 120-point interpolated stress grid for all 73 curves was audited directly against raw `STR_STR.OUT` files and SHA256 hashes. The maximum absolute difference was verified at **0.0**.
2. **Tier 2: Holdout Artifact Reload**
   Evaluating the frozen saved ensemble weights on the 37 holdout cases reproduced the exact saved metrics:
   - **Mean Test Curve RMSE:** **0.05908515** in inferred stress units.
   - **Worst Test Case RMSE:** **0.11330618** (Case 45).
3. **Tier 3: Same-Environment Training Reproduction**
   A completely independent refit of all five seeds on the 36 training cases took **25.0 seconds**, produced zero convergence warnings, and reproduced all weights and 73 predictions with **0.0 maximum absolute difference**.

### Summary of Performance Metrics
| Evaluation Split | Metric | Value (Inferred Stress Units) | Explanation |
| :--- | :--- | :--- | :--- |
| **Holdout Test Set (37 cases)** | Mean Curve RMSE | **0.059085** | Within-condition interpolation fidelity |
| **Holdout Test Set** | Worst Case RMSE | **0.113306** | Case 45 (high temperature) |
| **Training Case CV (36 cases)** | Mean Curve RMSE | **1.158263** | Cross-case variability across folds |
| **Training Case CV** | Median Curve RMSE | **0.201877** | Half of cases have RMSE $\le 0.20$ |
| **Leave-Condition-Out (LOCO)** | Mean of Conditions | **6.793603** | Average generalization to unseen $(T, \dot{\varepsilon})$ |
| **Leave-Condition-Out ($200^\circ\text{C}, 10^{-5}\,\text{s}^{-1}$)** | Condition Mean RMSE | **23.525129** | Hot/slow extreme operating corner |

#### Explaining the Metrics:
- **What is RMSE?** Root Mean Squared Error measures the average magnitude of prediction error across strain points along a curve: $\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (\hat{\sigma}_i - \sigma_i)^2}$.
- **Why is Test RMSE (0.059) so low?** All 8 temperature and strain-rate combinations present in the test set also exist in the training set. The test score measures interpolation within represented operating conditions.
- **Why is LOCO RMSE (6.79) higher?** When an entire operating condition is held out, the model must extrapolate across temperature/rate space without anchor curves. In the hot/slow condition ($200^\circ\text{C}, 10^{-5}\,\text{s}^{-1}$), error rises to 23.53.

### The Case 60 Anomaly
In training cross-validation, Case 60 exhibits high error ($\text{RMSE} = 25.99$). Inspection reveals that its recorded von Mises strain reverses while axial strain $E_{11}$ increases. The generating cause of this behavior is unknown. It is retained and flagged as genuine evidence of limited generalization under irregular yield behavior.

---

## 4. Runtime Performance & Benchmarks

An optimized NumPy-only runtime was developed (`src/query_runtime.py`) to eliminate the heavy scikit-learn dependency:
- **Weight Storage:** Stored in an 18,462-byte pickle-free `.npz` file (vs. 62,940 bytes Joblib).
- **Single-Curve Latency:** **0.221 ms** (NumPy) vs. **0.511 ms** (scikit-learn) in local repeated single-thread benchmarks.
- **Fresh Interpreter / Import / Load / Inference:** **163 ms** (NumPy) vs. **976 ms** (scikit-learn).
- **Full Batch (73 Cases):** NumPy was slower (**21.8 ms** vs. **17.3 ms**), as scikit-learn utilizes optimized multi-threaded BLAS routines for large matrix multiplications.
- **Accuracy Parity:** Exactly **0.0 difference** against reference model outputs.

---

## 5. Verified Executable Code Example

The following script loads the lightweight NumPy runtime, runs inference on a test condition, and queries a specific strain value:

```python
import sys
import numpy as np
from src.query_runtime import QueryRuntime

# 1. Load lightweight runtime (18 KB pickle-free NPZ)
runtime = QueryRuntime.load("runs/score/final_Svm/model_numpy.npz")

# 2. Define input case: [T, log10(strain_rate), density, shear_modulus]
# Example: T = 100 deg C, rate = 1e-4 s^-1, density = 2619.0, G = 24541.0
X_case = np.array([[100.0, -4.0, 2619.0, 24541.0]])

# 3. Predict full 120-point flow-stress curve
curve = runtime.predict(X_case)[0]
print(f"Predicted curve output shape: {curve.shape}")  # (120,)

# 4. Query stress at a specific strain point (e.g., E11 = 0.05)
# runtime.strain provides the standardized 120-point strain grid
stress_at_point = np.interp(0.05, runtime.strain, curve)
print(f"Predicted Flow Stress at E11 = 0.05: {stress_at_point:.4f} (inferred units)")
```

---

## 6. Operational Boundaries & Defense Q&A Guide

When presenting this model to academic reviewers, use this reference guide to answer challenging questions accurately:

**Q1: What are the units of your predicted stress?**  
*Answer:* "The raw simulation files report stress without explicit unit headers. The model predictions are evaluated in inferred stress units ($\text{RMSE} = 0.059$). While numerically consistent across all profiles, we explicitly treat them as inferred stress units rather than confirmed MPa until the simulator's exact constitutive definitions are verified."

**Q2: Does your model predict true plastic strain?**  
*Answer:* "No. The input variable is $E_{11}$, which is the operational axial strain coordinate reported by the simulation output, not verified true plastic strain."

**Q3: Can your model predict flow stress at $300^\circ\text{C}$?**  
*Answer:* "No. The training data strictly spans $30^\circ\text{C}$ to $200^\circ\text{C}$. Unconstrained MLPs predict unphysical negative stress when extrapolated to $300^\circ\text{C}$. Operational use must strictly remain within $[30^\circ\text{C}, 200^\circ\text{C}]$."

**Q4: Can this model predict wing-rib bracket aerodynamic lift ($C_L$)?**  
*Answer:* "No. This is a material-level flow-stress surrogate. The simulation matrix models constitutive stress-strain histories, not aerodynamic coefficients. It serves as an accelerated constitutive input for finite element structural analysis."

**Q5: Can you claim zero data leakage?**  
*Answer:* "We claim a strictly disjoint case partition for final fitting and evaluation. However, earlier exploratory feature selection was performed across the dataset before the final split was frozen. We maintain scientific honesty by reporting this exploration rather than claiming an untouched blind holdout."
