import copy, unittest
from functional_mechanisms_h4 import evaluate_h4_diagnostics,H4EvidenceError

T='2026-10-16T11:05:00Z'
def doc(value, unit, state='PLANNED', at=T):
    return {'value':value,'unit':unit,'state':state,'available_at_utc':at,'source':'H4_HYPOTHETICAL_PRESTART'}

def packet():
    def field(value, kind='ASSUMPTION'):
        return {'value':value,'available_at_utc':T,'kind':kind,'source':'SYNTHETIC_PRESTART'}
    def case(value,unit,state='OBSERVED'):
        return {'value':value,'unit':unit,'state':state,'available_at_utc':T,'source':'SYNTHETIC_PRESTART'}
    def plan(state):
        return {'status':state,'available_at_utc':T,'source':'SYNTHETIC_PRESTART'}
    return {'prestart':{'freeze_utc':'2026-10-16T12:00:00Z','start_utc':'2026-10-16T13:00:00Z',
             'inputs':{'rice_mass_g':field(160),'surface_starch_index':field(.5),
                       'rinse_removal_fraction':field(.4,'PLANNED')}},
            'case_inputs':{'001':case(160,'g'),'003':case(None,'g','UNKNOWN'),
                           '029':case(None,'fraction','UNKNOWN'),'030':case(.5,'fraction')},
            'action_plans':{'049':plan('PLANNED'),'054':plan('PLANNED'),
                            '061':plan('PLANNED'),'082':plan('PLANNED')}}

class TestH4(unittest.TestCase):
    def test_unknown_not_zero(self):
        o=evaluate_h4_diagnostics(packet())
        self.assertIsNone(o['mechanisms']['salt']['feasible'])
        self.assertIsNone(o['mechanisms']['grain_rinse']['broken_dry_mass_g'])
        self.assertIsNone(o['scientific_ic_percent'])
    def test_stock_salt_feasible(self):
        x=evaluate_h4_diagnostics(packet(),salt_stock=doc(7,'g','OBSERVED'),salt_dose=doc(5,'g'))['mechanisms']['salt']
        self.assertTrue(x['feasible']);self.assertEqual(x['shortfall_g'],0);self.assertAlmostEqual(x['planned_salt_per_dry_rice_g'],.03125)
    def test_stock_salt_shortfall(self):
        x=evaluate_h4_diagnostics(packet(),salt_stock=doc(3,'g','OBSERVED'),salt_dose=doc(5,'g'))['mechanisms']['salt']
        self.assertFalse(x['feasible']);self.assertEqual(x['shortfall_g'],2)
    def test_zero_salt_stock_is_observed_zero(self):
        x=evaluate_h4_diagnostics(packet(),salt_stock=doc(0,'g','OBSERVED'),salt_dose=doc(1,'g'))['mechanisms']['salt']
        self.assertEqual(x['available_g'],0);self.assertFalse(x['feasible'])
    def test_zero_salt_dose_is_valid_plan(self):
        x=evaluate_h4_diagnostics(packet(),salt_stock=doc(0,'g','OBSERVED'),salt_dose=doc(0,'g'))['mechanisms']['salt']
        self.assertTrue(x['feasible'])
    def test_portions_two(self):
        x=evaluate_h4_diagnostics(packet(),portion_count=doc(2,'count'))['mechanisms']['portions']
        self.assertEqual(x['dry_rice_per_portion_g'],80)
    def test_portions_four_changes_dry_share_only(self):
        a=evaluate_h4_diagnostics(packet(),portion_count=doc(2,'count'))
        b=evaluate_h4_diagnostics(packet(),portion_count=doc(4,'count'))
        self.assertEqual(b['mechanisms']['portions']['dry_rice_per_portion_g'],40)
        self.assertIsNone(a['scientific_ic_percent']);self.assertIsNone(b['scientific_ic_percent'])
    def test_broken_grain_mass_balance(self):
        f=doc(.25,'fraction','OBSERVED');f['basis']='dry_mass_fraction'
        x=evaluate_h4_diagnostics(packet(),broken_grain_fraction=f)['mechanisms']['grain_rinse']
        self.assertAlmostEqual(x['broken_dry_mass_g']+x['intact_dry_mass_g'],160)
    def test_ambiguous_broken_fraction_rejected(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),broken_grain_fraction=doc(.25,'fraction','OBSERVED'))
    def test_count_fraction_cannot_be_interpreted_as_mass(self):
        f=doc(.25,'fraction','OBSERVED');f['basis']='grain_count_fraction'
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),broken_grain_fraction=f)
    def test_rinse_starch_index(self):
        x=evaluate_h4_diagnostics(packet())['mechanisms']['grain_rinse']
        self.assertEqual(x['planned_surface_starch_index_after_rinse'],.3)
    def test_no_undeclared_salt_action(self):
        p=packet();p['action_plans']['061']['status']='UNKNOWN'
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p,salt_dose=doc(5,'g'))
    def test_no_undeclared_portion_action(self):
        p=packet();p['action_plans']['082']['status']='UNKNOWN'
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p,portion_count=doc(2,'count'))
    def test_no_undeclared_rinse(self):
        p=packet();p['action_plans']['054']['status']='UNKNOWN'
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p)
    def test_postfreeze_rejected(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),salt_dose=doc(4,'g',at='2026-10-16T12:01:00Z'))
    def test_poststart_rejected(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),portion_count=doc(2,'count',at='2026-10-16T13:00:01Z'))
    def test_timezone_required(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),salt_dose=doc(4,'g',at='2026-10-16T10:00:00'))
    def test_wrong_unit_rejected(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),salt_stock=doc(5,'kg'))
    def test_negative_or_nonfinite_rejected(self):
        for v in (-1,float('nan'),float('inf'),True):
            with self.subTest(v=v),self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),salt_stock=doc(v,'g'))
    def test_fraction_out_of_range(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),broken_grain_fraction=doc(1.2,'fraction'))
    def test_fraction_not_override_known(self):
        p=packet();p['case_inputs']['029']['value']=.2;p['case_inputs']['029']['state']='OBSERVED'
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p,broken_grain_fraction=doc(.3,'fraction'))
    def test_starch_shared_primitive_mismatch(self):
        p=packet();p['case_inputs']['030']['value']=.8
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p)
    def test_rice_mass_shared_primitive_mismatch(self):
        p=packet();p['case_inputs']['001']['value']=300
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p)
    def test_future_target_never_read(self):
        p=packet();p['target_contract']={'final_quality':100,'available_at_utc':'2026-10-16T14:00:00Z'}
        a=evaluate_h4_diagnostics(p)
        del p['target_contract']
        self.assertEqual(a,evaluate_h4_diagnostics(p))
    def test_immutability_and_repeat(self):
        p=packet();before=copy.deepcopy(p)
        a=evaluate_h4_diagnostics(p,salt_stock=doc(6,'g'),salt_dose=doc(3,'g'),portion_count=doc(2,'count'))
        self.assertEqual(p,before);self.assertEqual(a,evaluate_h4_diagnostics(p,salt_stock=doc(6,'g'),salt_dose=doc(3,'g'),portion_count=doc(2,'count')))
    def test_bad_freeze_order(self):
        p=packet();p['prestart']['freeze_utc']=p['prestart']['start_utc']
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p)
    def test_unknown_with_numeric_value_rejected(self):
        p=packet();p['case_inputs']['003']['value']=0
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(p)
    def test_integral_count_only(self):
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),portion_count=doc(2.5,'count'))
    def test_no_timestamp_unsupported(self):
        x=doc(4,'g');del x['available_at_utc']
        with self.assertRaises(H4EvidenceError):evaluate_h4_diagnostics(packet(),salt_stock=x)

if __name__=='__main__':unittest.main()