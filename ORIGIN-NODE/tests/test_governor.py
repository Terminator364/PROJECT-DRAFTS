import unittest
from origin.governor import Snapshot, decide

GOOD = dict(battery_pct=80, battery_temp_c=32, charging=True,
            free_memory_mb=1300, storage_free_mb=4000, network_metered=False)

class GovernorTests(unittest.TestCase):
    def test_normal(self):
        d=decide(Snapshot(**GOOD)); self.assertEqual(d.tier, 'normal')
        self.assertEqual(d.max_workers, 2)
    def test_unknown(self):
        d=decide(Snapshot()); self.assertEqual(d.tier, 'conserve')
        self.assertFalse(d.run_heavy)
    def test_hot(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_temp_c':46})).tier,'protect')
    def test_warm(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_temp_c':41})).tier,'conserve')
    def test_low_battery(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_pct':5,'charging':False})).tier,'protect')
    def test_charging_low_battery(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_pct':5,'charging':True})).tier,'normal')
    def test_low_memory(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'free_memory_mb':125})).tier,'protect')
    def test_low_storage(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'storage_free_mb':100})).tier,'protect')
    def test_metered(self):
        d=decide(Snapshot(**{**GOOD,'network_metered':True}))
        self.assertFalse(d.allow_network_bulk)
    def test_invalid_percent(self):
        with self.assertRaises(ValueError):decide(Snapshot(battery_pct=101))
    def test_negative_percent(self):
        with self.assertRaises(ValueError):decide(Snapshot(battery_pct=-1))
    def test_unknown_temp(self):
        self.assertFalse(decide(Snapshot(**{**GOOD,'battery_temp_c':None})).run_heavy)
    def test_negative_celsius(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_temp_c':-2})).tier,'normal')
    def test_45_boundary(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_temp_c':45})).tier,'protect')
    def test_25_boundary(self):
        self.assertEqual(decide(Snapshot(**{**GOOD,'battery_pct':25,'charging':False})).tier,'conserve')
if __name__=='__main__':unittest.main()
