"""Isolation, scalar-equation orientation, batch inference and reload checks."""
import json
from pathlib import Path
import sys
import unittest
import numpy as np
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from single_mlp import fit,predict,export_equation,equation_predict,queries,select,lookup
from models import LookupBaseline


class SingleMLPTests(unittest.TestCase):
    def setUp(self):
        self.X=np.random.default_rng(4).normal(size=(9,4))
        self.e=np.linspace(.001,.09,12)
        self.Y=100+3*self.X[:,:1]+2*self.X[:,1:2]*self.e+5*self.e
        self.cfg=dict(hidden=[16,16],seed=42,max_iter=500,max_fun=1000,tol=1e-8,folds=3,alphas=[.001])

    def test_equation_and_frozen_scaling(self):
        with threadpool_limits(limits=1): m,_=fit(self.X[:6],self.Y[:6],self.e,.001,self.cfg)
        np.testing.assert_allclose(m['xs'].mean_,queries(self.X[:6],self.e).mean(0))
        p=predict(m,self.X[6:],self.e)
        eq=json.loads(json.dumps(export_equation(m)))
        q=equation_predict(eq,queries(self.X[6:],self.e)).reshape(p.shape)
        np.testing.assert_allclose(p,q,rtol=0,atol=1e-10)
        n=m['net'];self.assertEqual(sum(v.size for v in n.coefs_+n.intercepts_),385)
        single=equation_predict(eq,queries(self.X[6:7],self.e))
        np.testing.assert_allclose(single,p[0],rtol=0,atol=1e-10)

    def test_folds_and_original_baseline_agree(self):
        ids=np.arange(9)
        with threadpool_limits(limits=1): best,trials,base=select(self.X,self.Y,ids,self.e,self.cfg)
        seen=[]
        for rec in best['folds']:
            tr,va=rec['fit_ids'],rec['validation_ids'];seen+=va
            self.assertFalse(set(tr)&set(va))
            np.testing.assert_allclose(rec['mean'],queries(self.X[tr],self.e).mean(0))
        self.assertEqual(sorted(seen),list(ids))
        np.testing.assert_array_equal(lookup(self.X[:6],self.Y[:6],self.X[6:]),LookupBaseline().fit(self.X[:6],self.Y[:6]).predict(self.X[6:]))


if __name__=='__main__':unittest.main()
