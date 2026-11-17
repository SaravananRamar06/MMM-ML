# Hosted notebook check (closes Q8)

Run this once in your own Colab account and once on Kaggle. Nobody else can sign in for you. It takes about five minutes on each.

**Notebook:** `notebooks/jc_pinn_colab.ipynb`

- It embeds the model code and the locked weights, so `PREDICT` mode needs no data upload and no git clone.
- It installs `torch`, `scipy`, `scikit-learn` and `matplotlib` only if they are missing. Both platforms already include them.

## Colab

1. Open https://colab.research.google.com/github/SaravananRamar06/MMM-ML/blob/main/notebooks/jc_pinn_colab.ipynb (or **File → Open notebook → GitHub**, then paste the repository URL and pick the notebook).
2. In the first code cell, check `MODE = 'PREDICT'`. Leave `DATA_PATH = ''`.
3. **Runtime → Run all**. A CPU runtime is enough.
4. `PREDICT` should not ask to mount Google Drive, because the data search runs only in `FAST`/`FULL`. If it does ask, note it as a finding.
5. Write down:
   - the "Platform:" line (it should say Colab);
   - any error or traceback, with the cell number;
   - whether the prediction cell (the first code cell after "Predict curves from the saved equation") draws its three panels of predicted curves;
   - the runtime's Python and torch versions (`!python --version`, `import torch; torch.__version__`).

## Kaggle

1. Go to https://www.kaggle.com/code, then **New Notebook → File → Import Notebook**. Choose the GitHub tab, or upload `notebooks/jc_pinn_colab.ipynb` from the repository.
2. In the first code cell, check `MODE = 'PREDICT'`.
3. **Run All**. A CPU session is enough, and no dataset needs to be attached.
4. Write down the same items as for Colab. The "Platform:" line should say Kaggle.

## What counts as a pass

- Every cell runs without an error.
- The platform is detected correctly.
- The prediction cell draws its three panels of predicted curves.

## Then

Tell Claude the results, or paste any traceback. Q8 in `docs/open-questions.md` is then closed with the date, platform and versions. If a cell fails, the fix goes into the notebook builder (`scripts/build_jc_pinn_notebook.py`), not into the saved run.

Optional: `MODE = 'FAST'` retrains the final model and needs the data folder. It is not required to close Q8.
