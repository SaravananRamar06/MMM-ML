# Constitutive surrogate architectures

Research date: 24 October 2026. Scope: material stress–strain response only. The user's CL is **coefficient of lift**; this note does not redefine it or infer aerodynamic labels. Project-specific counts come from the existing local [dataset notes](../../dataset.md), not the papers below. No model was trained in this research.

## When is an MLP sufficient and when is recurrence justified?

### Takeaway

For a fixed, monotonically increasing loading protocol, a small feed-forward multilayer perceptron (MLP) is a defensible first surrogate for stress as a function of strain and prescribed material conditions. This is not a general constitutive law for arbitrary loading histories; unloading/reloading or changing multiaxial paths can require explicit internal-state inputs, recurrence, or embedded constitutive structure.

### Cited Findings

- **Sun et al., 2010:** developed a three-layer feed-forward, backpropagation-trained network for Ti600 hot-compression flow stress. Inputs were temperature, strain, and strain rate; output was flow stress. The material and deformation regime differ from this project, so it establishes precedent for the prediction formulation rather than AlSi10Mg-specific performance. The publisher's accessible abstract/introduction and section previews were inspected; complete architecture tuning and split details were not accessible. [Original paper, DOI 10.1016/j.commatsci.2010.03.007](https://www.sciencedirect.com/science/article/pii/S0927025610001151).
- **Vijayaraghavan et al., published 7 August 2023:** explicitly distinguish feed-forward use under known or approximately monotonic paths from recurrent treatment of general elastoplastic history. Their own study predicts full RVE displacement-field coefficients with an RNN/POD model, so its architecture is not directly comparable to a scalar-stress surrogate. Its introduction nevertheless directly supports per-step feed-forward prediction for nearly monotonic loading. [Scientific Reports paper](https://www.nature.com/articles/s41598-023-38104-x).
- **Maia et al., preprint 15 September 2022; journal publication 2023:** explain why current strain alone cannot uniquely determine stress during unloading. Their physically recurrent network (PRNN) embeds constituent material laws whose internal variables carry history. Thus a plain current-strain MLP is inadequate for general cyclic plasticity, but feed-forward or other networks can be augmented with state information; architecture labels alone do not determine capability. [Author preprint](https://arxiv.org/abs/2209.07320), [journal DOI](https://doi.org/10.1016/j.cma.2023.115934).

### Inferences

- **Recommendation for this project:** first confirm that the measured loading path is a single increasing strain ramp at fixed conditions. If so, use `stress = f(strain_query, temperature, log10(strain_rate), density, shear_modulus)`. Log-rate encoding is a proposed preprocessing choice, not a new measured variable or guaranteed improvement.
- Predicting a whole curve by evaluating this function over strain queries is sufficient for interpolation among similar histories. It does not establish the ability to reproduce arbitrary cyclic, relaxation, or multiaxial responses.
- A file's time column and large row count do not by themselves imply that an RNN is appropriate. Recurrence is justified by an unresolved dependence on loading history, not merely ordered storage.

### Gaps

- Actual generating equations, strain definitions, physical units, and loading paths remain unverified in the user's files. A local audit can support path classification; it cannot prove a universally memoryless material response.
- No source found establishes that an MLP is empirically best for this exact professor-supplied dataset. That claim requires training-only model selection followed by untouched test evaluation.

## What do path-dependent papers imply about data requirements?

### Takeaway

General path-dependent recurrent surrogates require suitable diversity of histories. The number of rows within a curve does not substitute for loading-path coverage. However, there is no universal minimum number of curves: correct embedded physics can change data requirements substantially.

### Cited Findings

- **Mozaffar et al., PNAS 2019:** used GRU-based sequence learning for heterogeneous material plasticity under varying multiaxial deformation paths. Their first example used 15,000 paths, each with 100 deformation states; the second used 8,000 samples with 80% used for training. One reported model used three stacked 500-unit recurrent layers, roughly three million parameters. These scales reflect their harder task, not a requirement or recommended configuration for every material dataset. The authors warn that data quantity/quality and model complexity affect performance. Full author-hosted paper inspected. [Author PDF](https://cpb-us-e2.wpmucdn.com/faculty.sites.uci.edu/dist/1/863/files/2021/04/paper-11.pdf), [journal record](https://doi.org/10.1073/pnas.1911815116).
- **Maia et al. (2022/2023):** in selected scenarios, their physics-embedded PRNN trained on 18 fundamental monotonic curves could reproduce unloading/reloading that a conventional RNN trained only on monotonic curves failed to capture. The benefit depends on embedding the actual constituent material models and maintaining their internal variables. It is not evidence that any generic 18-curve PINN or RNN will generalize in this way. [Full author preprint, sections 6.1–6.4](https://arxiv.org/pdf/2209.07320).

### Inferences

- With 73 available cases and a required 50/50 split, only 36 or 37 distinct condition combinations can train our material model. The first architecture should therefore be compact and matched to the limited task, even though each case contains many stress–strain points.
- Do not conclude that RNNs are impossible with this dataset solely from the case count. Conclude that a more elaborate sequence model needs a demonstrated task-specific reason, appropriate histories, and validation evidence.
- A recurrent model trained exclusively on one-direction ramps would not automatically justify claims about unseen unloading cycles. If general loading-path prediction becomes mandatory, the dataset itself may need expansion.

### Gaps

- We cannot infer an optimal hidden-state size, architecture, or expected error for 36 training cases from papers using different materials and protocols.
- Constituent laws needed for a faithful PRNN have not been established for the professor's simulations; the old deck's Johnson–Cook constants must not simply be assumed to be those laws.

## What concrete first architecture and decision rule are defensible?

### Takeaway

Recommend a **regularized, scalar-output MLP** for the material-curve task, conditional on a monotonic fixed-path audit. Recommend an architecture family now; choose its exact capacity using case-level validation, not a literature-derived claim of optimality.

### Cited Findings

- Official scikit-learn documentation describes MLP regression, linear output activation for continuous prediction, L2 regularization, sensitivity to feature scaling, and starting with few layers and neurons. It instructs fitting scalers only on training data and reports L-BFGS as a useful small-dataset optimizer. This is general implementation guidance, not a constitutive-material validation study. [Supervised neural-network guide, accessed 24 October 2026](https://scikit-learn.org/stable/modules/neural_networks_supervised.html).

### Inferences

- **Starting configuration, not experimentally selected:** five inputs, two hidden layers of 16 neurons, one stress output (`5–16–16–1`, 385 weights/biases). A smooth activation such as tanh is reasonable to test, with train-only input/target scaling, L2 regularization, and case-balanced sampling. Neither layer count nor activation has been proven optimal here.
- Make preprocessing and the architecture selection rule explicit before opening final test results. Reserve half the cases as requested; obtain validation cases or folds only from the training half. Keep all samples and derived versions of each case together. Report per-case errors, not only pooled row-wise metrics.
- **Overturn the recommendation** if the audit finds non-unique stress for the same chosen inputs along distinct loading paths, if the target becomes general cyclic or multiaxial constitutive updating, or if known internal variables/constituent equations make a structured model more appropriate.
- **Second-model decision:** do not select an LSTM merely to fill the two-model allowance. A second model should test a meaningful hypothesis after the audit, such as whether a validated physical structure or curve-level representation improves generalization.

### Gaps

- Meaning of `Evm` versus `E11`, `Svm` versus axial stress, and the scope of the strain query still need a documented prediction contract.
- No aerodynamic training data was identified. This material recommendation cannot be extended to coefficient-of-lift prediction by analogy alone.
