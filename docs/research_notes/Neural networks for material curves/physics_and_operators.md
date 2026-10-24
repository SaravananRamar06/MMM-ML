# Physics constraints and curve representations

Research date: 24 October 2026. Scope: architecture selection before implementation for the supplied 73 AlSi10Mg material histories, approximately 36 training cases, four scalar conditions, and a strain query. No training was performed. CL is coefficient of lift; no aerodynamic target is constructed here.

## Are physics informed networks justified now?

### Takeaway

Not as the first implementation. Physics-informed training can use a feed-forward backbone, but valid equations, state definitions, and compatible observations must come first. A thermodynamics-aware constitutive architecture has substantially stronger prerequisites than simply adding Johnson–Cook to a loss.

### Cited Findings

- Masi, Stefanou, Vannucci and Maffi-Berthier, *Thermodynamics-based Artificial Neural Networks for constitutive modeling* (2020 preprint; JMPS 2021), build constitutive networks around free energy, dissipation, internal state, and incremental updates. Their original treatment is strain-rate independent; they discuss extension to viscosity/rate dependence. The training construction needs free-energy and dissipation outputs in addition to ordinary response quantities. Their 1D demonstration generated 2,000 random state/increment pairs per material case, used 1,000 for training, and compared to conventional ANNs. This is not a study with 36 AlSi10Mg curves. The authors discuss non-vanishing higher derivatives of activation functions when derivatives of learned energy enter the loss. — [Full primary manuscript](https://arxiv.org/html/2005.12183), especially sections 3–5.
- Krishnapriyan et al., *Characterizing possible failure modes in physics-informed neural networks* (NeurIPS 2021), show in convection, reaction, and diffusion examples that PDE residual constraints can cause optimisation difficulty and ill conditioning. The observed failures are not simply insufficient network expressivity. Their remedies include curriculum regularisation and sequential solution strategies. These are PDE examples, not evidence of failure or success on the present material dataset. — [Full primary manuscript](https://arxiv.org/html/2109.01050).

### Inferences

- The user wants a material surrogate first. Neither unknown units nor an unknown generating law should be filled in from the old deck. A scalar stress–strain curve also does not by itself provide a full thermodynamic state representation.
- A physics-constrained MLP could become a useful second experiment **if** a compatible, independently justified constitutive law/state definition is recovered. Compare it to the same data-only backbone so that the effect of the constraints can be isolated.
- Do not impose universal hardening, zero initial stress, or monotonic temperature/rate trends before auditing the actual response. Those would be assumptions, not established fundamentals for this data.
- Do not describe positivity or smoothness penalties alone as proof of thermodynamic consistency, and do not promise improved extrapolation merely because a model is called physics informed.

### Gaps

- Actual governing law, internal variables, energy/dissipation outputs, initial state, and rate dependence are unverified. Consequently this research does not specify a defensible physics residual for these files.

## Does DeepONet or another operator network fit this problem?

### Takeaway

A branch–trunk network is possible, but there is no evidence yet that its added structure is needed for four scalar conditions and a scalar strain query. It is worth revisiting if the task becomes learning across diverse loading **functions**, not simply fixed parameter combinations.

### Cited Findings

- Lu, Jin and Karniadakis' original DeepONet preprint (2019, revised 2020; journal development published in 2021) represents input functions by sensor values in a branch network and output coordinates in a trunk network. It tests nonlinear dynamic systems and a diffusion–reaction PDE, reporting improved generalisation over fully connected comparators in those experiments. One PDE example uses 100 input functions with 1,000 output observations per function. The paper explicitly distinguishes approximation guarantees from optimisation/generalisation errors. These examples establish capability, not a sample-size rule or a guaranteed advantage for this AlSi10Mg dataset. — [Full original manuscript](https://arxiv.org/html/1910.03193).

### Inferences

- A parameter-to-curve variant could take `[temperature, log(rate), density, modulus]` in the branch and strain in the trunk. This is an adaptation, not direct replication of the original input-function setting.
- Both it and a pointwise MLP could produce continuous strain-query predictions; producing a curve does not itself force operator learning.
- With only approximately 36 training conditions, the relevant question is whether branch–trunk factorisation supplies a useful inductive bias. More output points do not create more independent input functions/parameter cases.
- Do not reject DeepONet with a blanket assertion that it always requires huge data; its own examples include modest numbers of functions. Reject it as the **default here** because its extra machinery is not yet motivated or benchmarked.

### Gaps

- No located primary source tests these exact 73 cases or proves which network wins with 36 training cases. No inference is made about general loading histories outside the available protocol.

## Is PCA or POD plus an MLP a useful second model?

### Takeaway

Yes, conditionally: it is a more concrete second candidate than an unjustified PINN. First determine, using training cases only, whether the curves have a compact low-error linear representation. If not, do not spend the second-model budget on it.

### Cited Findings

- Yang, Kim, Ryu and Gu, *Prediction of composite microstructure stress–strain curves using convolutional neural networks*, Materials & Design 189 (2020), 108509, represent 61-point stress curves with 15 principal components, capturing over 99.5% of the variance in their dataset. They explicitly fit PCA on training data only. A CNN predicts the compressed coefficients because their inputs are binary microstructure images. Their dataset contains 100,000 composite configurations, with a 95:5 split. The result supports curve compression as a method; its CNN, data scale, and material differ sharply from this project. — [Author-hosted full paper](https://gu.berkeley.edu/wp-content/uploads/2020/03/materials_and_design_gu.pdf), sections 2.1–2.3 and 3.1; [DOI](https://doi.org/10.1016/j.matdes.2020.108509).
- Bhattacharya, Hosseini, Kovachki and Stuart, *Model Reduction and Neural Networks for Parametric PDEs* (2020 preprint, revised June 2021), combine PCA encoding/decoding with a neural network between reduced coordinates. Their analysis separates dimensional-reduction and learned-map errors. They note that linear-subspace approximation of a nonlinear solution manifold can converge slowly; increasing reduced dimension can demand more training data. Their demonstrated PDE settings are not a validation on this material. — [Full primary manuscript](https://arxiv.org/html/2005.03180), sections 2–4.

### Inferences

- Concrete competitor: four scalar conditions → a small MLP → `k` predicted PCA coefficients → reconstructed stress curve on a documented common strain grid. This retains one independent training example per material case and explicitly models whole-curve correlation.
- Fit the mean, basis, coefficient scalers, and `k` **inside each training-validation fold**. A basis fitted once on all 73 curves leaks test-target shape information. After selecting `k` using training-side validation, fit the final basis on the complete training partition, never the test partition.
- Select `k` by original-unit reconstruction errors and errors near important curve features, not a variance percentage alone. Compare held-out *curve* errors against the pointwise MLP under the identical case split.
- Candidate limitations: different strain endpoints need careful interpolation/common support; a moving sharp knee, stress drop, or localised feature may require many fixed basis modes or produce local errors even when global variance retention looks high. This is an inference from fixed-subspace compression, not a claim that those defects are established in these files.
- Report separately: (1) basis truncation/reconstruction error and (2) coefficient-prediction error. A poor basis imposes an error floor no larger MLP can remove. Do not label the PCA model a physical law.
- Recommendation: retain the compact pointwise MLP as model 1; reserve model 2 for a PCA/POD–MLP **only if** a training-only compression diagnostic supports it. Prioritise a physics-constrained comparison instead only if sound governing information becomes available.

### Gaps

- The curve singular-value spectrum, common strain support, and actual reconstruction error have not been measured in this research. No defensible value of `k`, accuracy claim, or winner can yet be named.
