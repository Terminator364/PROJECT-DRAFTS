import unittest
from pipeline44 import run44
from test_bridge44 import packet, mutated

class TestPipeline44(unittest.TestCase):
    def test_legacy_score_only_after_routing_44(self):
        seen=[]
        def fake(p,c,n_draws,seed):
            seen.append((n_draws,seed))
            return {'ic_demo_percent':44.5}
        result=run44(packet(),contract={},n_draws=123,seed=9,simulator=fake)
        self.assertEqual(result['prestart_routed'],44)
        self.assertEqual(result['prestart_evaluated'],44)
        self.assertEqual(result['ic_demo_percent'],44.5)
        self.assertIsNone(result['scientific_ic_percent'])
        self.assertEqual(seen,[(123,9)])
    def test_water_shortage_abstains_without_score(self):
        p=packet()
        p['case_inputs']['002']['value']=1.
        seen=[]
        def fake(*args,**kwargs):seen.append(True)
        r=run44(p,simulator=fake)
        self.assertEqual(r['status'],'ABSTAIN_PRET0_CONSTRAINT')
        self.assertIsNone(r['ic_demo_percent'])
        self.assertFalse(seen)
    def test_incompatible_energy_source_abstains(self):
        p=mutated(packet(),'006')
        r=run44(p,simulator=lambda *a,**k:{'ic_demo_percent':1})
        self.assertEqual(r['status'],'ABSTAIN_PRET0_CONSTRAINT')
        self.assertTrue(any('incompatible' in s for s in r['prestart_gate_issues']))
    def test_missing_measuring_device_abstains_if_plan_requires_it(self):
        p=mutated(packet(),'020')
        r=run44(p,simulator=lambda *a,**k:{'ic_demo_percent':1})
        self.assertEqual(r['status'],'ABSTAIN_PRET0_CONSTRAINT')
    def test_batch_identity_does_not_change_quality_proxy(self):
        fake=lambda *a,**k:{'ic_demo_percent':21}
        a=run44(packet(),simulator=fake)
        b=run44(mutated(packet(),'027'),simulator=fake)
        self.assertEqual(a['ic_demo_percent'],b['ic_demo_percent'])
        self.assertNotEqual(a['trace']['routes']['027'],b['trace']['routes']['027'])

if __name__=='__main__':unittest.main()
