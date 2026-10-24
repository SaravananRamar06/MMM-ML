# Independent Review of Presentation Deck (Slides 3, 6, 7, 8, 10)

**Reviewer:** Gemini (Antigravity)  
**Date:** 2026-10-24  
**Target:** `reports/presentation/slides.md` & `reports/presentation/numbers.md` against saved artifacts (`data/manifest.json`, `runs/selected_Svm/`, `runs/selection_Svm.json`, `runs/score/`, `runs/loco_chosen_settings.json`).

---

### 1. Slide 3: Data-Count Claims
* **Claim:** "108 simulations planned; 73 available: 3 temperatures × 3 strain rates × 3 densities × 3 shear moduli."
  * **Finding — Discrepancy:** $3 \times 3 \times 3 \times 3 = 81$, not 108. The planned matrix actually specifies **4 temperatures** (30, 100, 200, 300 °C) $\times$ 3 rates $\times$ 3 densities $\times$ 3 shear moduli = $4 \times 27 = 108$.
  * **Recommendation:** Correct "3 temperatures" to **"4 temperatures"** (Line 17 already correctly shows all 4 temperatures: 30 °C 27/27, 100 °C 27/27, 200 °C 19/27, 300 °C 0/27).
* **Claim:** Available cases: 30 °C (27), 100 °C (27), 200 °C (19), 300 °C (0) = 73 total. Max strain 0.1; row counts 1,000 / 10,000 / 100,000.
  * **Finding — Verified:** Matches `data/manifest.json` exactly across all 73 parsed files.

---

### 2. Slide 7: Model & Parameter-Count Claims
* **Claim:** Query MLP architecture 5 → 16 → 16 → 1 with 385 parameters per network; 5-network ensemble total = 1,925 parameters.
  * **Finding — Verified:** Reloaded `runs/selected_Svm/query_MLP.joblib`:
    * Layer 0 (Input $\to$ H1): $5 \times 16$ weights + 16 biases = 96
    * Layer 1 (H1 $\to$ H2): $16 \times 16$ weights + 16 biases = 272
    * Layer 2 (H2 $\to$ Out): $16 \times 1$ weights + 1 bias = 17
    * Per-network total = $96 + 272 + 17 = 385$ weights and biases.
    * Ensemble total (5 nets) = $385 \times 5 = 1,925$.
* **Claim:** "with 36 training curves, the larger 32×32 networks did worse in validation."
  * **Finding — Verified:** Confirmed in `runs/selection_Svm.json` history:
    * $16 \times 16$ networks scored CV mean RMSE between **1.158 and 1.201 MPa**.
    * $32 \times 32$ networks scored CV mean RMSE between **1.972 and 2.051 MPa**.

---

### 3. Evaluation Wording on Slides 6, 8, 10

#### Slide 6: "All settings were chosen inside the 36 training cases"
* **Finding:** While hyperparameter tuning (L2 regularisation penalty $\alpha$, hidden layer size selection) was formally conducted on the 3-fold split of the 36 training cases (`runs/selection_Svm.json`), the overall model family, activation function (`tanh`), and initial sizing were established during prior exploratory passes across the dataset before the split was frozen (as disclosed honestly in Slide 12 and `reports/claude-model-recommendation.md`).
* **Recommendation:** To maintain strict academic integrity and align with Slide 12, clarify Slide 6 wording slightly:
  * *Current:* "All settings were chosen inside the 36 training cases."
  * *Suggested:* "Hyperparameters (regularisation, network size) were selected using cross-validation inside the 36 training cases."

#### Slide 8: Table & Unseen-Condition Error
* **Finding — Verified:** All table metrics match `runs/score/select_*_Svm.json` exactly:
  * Query MLP: CV 1.16 MPa, LOCO 6.8 MPa
  * PCA + GP: CV 0.66 MPa, LOCO 11.0 MPa
  * MLP + GP blend: CV 0.87 MPa, LOCO 8.0 MPa
  * MLP with 1/T input: CV 1.54 MPa, LOCO 8.6 MPa
  * PCA-MLP (rank 6): CV 2.00 MPa, LOCO 11.2 MPa
* **Context Note:** The "Unseen-condition error" of **6.8 MPa** for Query MLP here is computed exclusively across condition folds *inside the 36 training cases*.

#### Slide 10: "A condition never seen"
* **Finding — Verified:** The temperature ranges (30 °C: 1.5–4.3 MPa, 100 °C: 1.9–7.6 MPa, 200 °C: 8.0–24.8 MPa) accurately reflect `runs/loco_chosen_settings.json` (target `Svm`, model `mlp`, $\alpha = 0.001$).
* **Recommendation:** Slide 10 uses leave-one-condition-out across **all 73 cases** (an all-dataset diagnostic), whereas Slide 8 reported LOCO inside the training half (**6.8 MPa**). A brief qualifier on Slide 10 (e.g. *(evaluated across all 73 simulation cases as an extrapolation diagnostic)*) will prevent confusion about why the overall LOCO average in Slide 8 is 6.8 MPa while individual conditions in Slide 10 range up to 24.8 MPa.
