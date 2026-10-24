"""Professor's protocol: random half of the simulation cases for training, half for testing.

73 cases cannot split evenly, so we use 36 train / 37 test. The seed is fixed and the
split is saved once; we never re-roll it to get a better score.
"""
import json

import numpy as np

from data import DATA, build

SEED = 42
N_TRAIN = 36


def make_split():
    path = DATA / "split.json"
    if path.exists():
        return json.loads(path.read_text())
    ids, *_ = build()
    perm = np.random.default_rng(SEED).permutation(ids)
    split = {"seed": SEED, "train": sorted(int(i) for i in perm[:N_TRAIN]),
             "test": sorted(int(i) for i in perm[N_TRAIN:])}
    assert not set(split["train"]) & set(split["test"])
    path.write_text(json.dumps(split, indent=1))
    return split


if __name__ == "__main__":
    s = make_split()
    print(f"seed {s['seed']}: {len(s['train'])} train, {len(s['test'])} test; "
          f"case 60 in {'test' if 60 in s['test'] else 'train'}")
