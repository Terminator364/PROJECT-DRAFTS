import copy, math, unittest
from functional_mechanisms_h4b import evaluate_h4b,H4BError,GROUPS,RUBRICS
T='2026-10-16T11:00:00Z'
def obs(v,unit='enum',state='ASSUMPTION',date=T):
    return dict(value=v,unit=unit,state=state,available_at_utc=date,source='PRE_T0_SYNTHETIC')
def packet():
    def case(v,state='ASSUMPTION'):
        return dict(value=v,state=state,unit=None,available_at_utc=T,source='PRE_T0_SYNTHETIC')
    def action(s):
        return dict(status=s,available_at_utc=T,source='PRE_T0_SYNTHETIC')
    return {'prestart':{'freeze_utc':'2026-10-16T12:00:00Z','start_utc':'2026-10-16T13:00:00Z',
                        'inputs':{'rice_mass_g':{'value':160,'unit':'g','kind':'OBSERVED','available_at_utc':T,'source':'PRE_T0_SYNTHETIC'}}},
            'case_inputs':{'010':case(None,'UNKNOWN'),'011':case(None,'UNKNOWN'),
              '018':case(None,'UNKNOWN'),'022':case(True),'023':case(True),
              '024':case('long_white_hypothesis','OBSERVED'),'031':case(None,'UNKNOWN')},
            'action_plans':{k:action('PLANNED') for k in ['071','077','081','083','084','085']},
            'correction_policies':{k:action('DEFINED') for k in ['094','098']}}
def full():
    return {'conductivity_W_mK':obs(50,'W/m/K'), 'thickness_mm':obs(2,'mm'),
      'diameter_cm':obs(18,'cm'),'contact_R_K_W':obs(.05,'K/W'), 'heat_delta_K':obs(20,'K'),
      'temperature_min_C':obs(85,'degC'),'temperature_max_C':obs(110,'degC'),
      'burn_threshold_C':obs(100,'degC'),'agitation_count':obs(2,'count','PLANNED'),
      'fluff_count':obs(1,'count','PLANNED'),'utensil_type':obs('fork'),
      'amylose_fraction':obs(.2,'dry_mass_fraction'),'impurity_mass_fraction':obs(.04,'dry_mass_fraction'),
      'sorting_removal_fraction':obs(.5,'fraction','PLANNED'),
      'service_UA_W_K':obs(.3,'W/K'),'service_initial_C':obs(80,'degC'),
      'service_ambient_C':obs(25,'degC'),'service_heat_capacity_J_K':obs(2000,'J/K'),
      'service_delay_min':obs(10,'min','PLANNED'),'service_target_min_C':obs(70,'degC','PLANNED'),
      'planned_max_delay_min':obs(8,'min','PLANNED'),'stop_temperature_C':obs(120,'degC')}
class TestH4B(unittest.TestCase):
    def go(self,fields=None,p=None):return evaluate_h4b(p or packet(),fields)
    def test_15_unique_all_covered(self):
        self.assertEqual(len(RUBRICS),15)
        self.assertEqual(set(RUBRICS),set(sum((list(g) for g in GROUPS.values()),[])))
    def test_default_missing_not_zero(self):
        q=self.go()
        self.assertIsNone(q['mechanism_groups']['thermal_wall'])
        self.assertIsNone(q['mechanism_groups']['service']['forecast_service_C'])
        self.assertIsNone(q['scientific_ic_percent'])
    def test_all_groups_explicit_complete(self):
        q=self.go(full())
        self.assertEqual(q['groups_without_full_numeric_path'],[])
        self.assertEqual(set(q['rubric_paths']),set(RUBRICS))
        self.assertIsNone(q['scientific_ic_percent'])
    def test_thermal_resistance_decreases_with_conductivity(self):
        a=full();b=copy.deepcopy(a);b['conductivity_W_mK']['value']=100
        self.assertLess(self.go(b)['mechanism_groups']['thermal_wall']['wall_resistance_K_W'],
                        self.go(a)['mechanism_groups']['thermal_wall']['wall_resistance_K_W'])
    def test_thermal_resistance_rises_with_thickness(self):
        a=full();b=copy.deepcopy(a);b['thickness_mm']['value']=4
        self.assertGreater(self.go(b)['mechanism_groups']['thermal_wall']['wall_resistance_K_W'],
                           self.go(a)['mechanism_groups']['thermal_wall']['wall_resistance_K_W'])
    def test_energy_limit_always_nonnegative(self):
        q=self.go(full());self.assertGreater(q['mechanism_groups']['thermal_wall']['available_heat_W'],0)
    def test_zero_delta_has_zero_heat_limit(self):
        s=full();s['heat_delta_K']['value']=0
        self.assertEqual(self.go(s)['mechanism_groups']['thermal_wall']['available_heat_W'],0)
    def test_spatial_range(self):
        self.assertEqual(self.go(full())['mechanism_groups']['temperature_distribution']['spread_C'],25)
    def test_spatial_inverted_rejected(self):
        s=full();s['temperature_min_C']['value']=120
        with self.assertRaises(H4BError):self.go(s)
    def test_unknown_hotspot_does_not_infer_burn(self):
        s=full();del s['temperature_max_C']
        self.assertIsNone(self.go(s)['mechanism_groups']['policies']['burn_trigger_hypothetical'])
    def test_burn_branch_true_and_stop_false(self):
        q=self.go(full())['mechanism_groups']['policies']
        self.assertTrue(q['burn_trigger_hypothetical']);self.assertFalse(q['stop_trigger_hypothetical'])
    def test_burn_branch_threshold_rise_changes(self):
        s=full();s['burn_threshold_C']['value']=115
        self.assertFalse(self.go(s)['mechanism_groups']['policies']['burn_trigger_hypothetical'])
    def test_burn_policy_requires_defined(self):
        p=packet();p['correction_policies']['094']['status']='UNDEFINED'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_stop_policy_requires_defined(self):
        p=packet();p['correction_policies']['098']['status']='UNDEFINED'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_handling_count(self):
        self.assertEqual(self.go(full())['mechanism_groups']['handling']['total_planned_contacts'],3)
    def test_unknown_handling_remains_unknown(self):
        s=full();s.pop('fluff_count')
        self.assertIsNone(self.go(s)['mechanism_groups']['handling']['total_planned_contacts'])
    def test_agitation_action_gate(self):
        p=packet();p['action_plans']['071']['status']='UNKNOWN'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_fluff_action_gate(self):
        p=packet();p['action_plans']['077']['status']='UNKNOWN'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_fractions_and_counts_reject_bool(self):
        s=full();s['agitation_count']['value']=True
        with self.assertRaises(H4BError):self.go(s)
    def test_counts_reject_fractional(self):
        s=full();s['fluff_count']['value']=1.2
        with self.assertRaises(H4BError):self.go(s)
    def test_tool_availability_gate(self):
        p=packet();p['case_inputs']['022']['value']=False
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_amylose_mass_only_assumption(self):
        self.assertEqual(self.go(full())['mechanism_groups']['variety']['dry_amylose_mass_g'],32)
    def test_variety_required(self):
        p=packet();p['case_inputs']['024']['value']=None;p['case_inputs']['024']['state']='UNKNOWN'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_impurity_fraction_mass_only(self):
        self.assertAlmostEqual(self.go(full())['mechanism_groups']['impurities']['expected_remaining_dry_mass_fraction'],.02)
    def test_impurity_range(self):
        s=full();s['impurity_mass_fraction']['value']=1.1
        with self.assertRaises(H4BError):self.go(s)
    def test_impurity_conflict_existing_rejected(self):
        p=packet();p['case_inputs']['031']['state']='OBSERVED';p['case_inputs']['031']['value']=.2
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_service_temperature_in_bounds(self):
        q=self.go(full())['mechanism_groups']['service']
        self.assertLess(q['forecast_service_C'],80);self.assertGreater(q['forecast_service_C'],25)
    def test_service_more_delay_cools_more(self):
        s=full();s['service_delay_min']['value']=60
        self.assertLess(self.go(s)['mechanism_groups']['service']['forecast_service_C'],
                        self.go(full())['mechanism_groups']['service']['forecast_service_C'])
    def test_service_ambient_equal_start_constant(self):
        s=full();s['service_ambient_C']['value']=60;s['service_initial_C']['value']=60
        self.assertEqual(self.go(s)['mechanism_groups']['service']['forecast_service_C'],60)
    def test_service_delay_overrun(self):
        self.assertEqual(self.go(full())['mechanism_groups']['service']['delay_overrun_min'],2)
    def test_service_delay_action_gate(self):
        p=packet();p['action_plans']['084']['status']='UNKNOWN'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_service_target_action_gate(self):
        p=packet();p['action_plans']['085']['status']='UNKNOWN'
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_service_plan_requires_vessel(self):
        p=packet();p['case_inputs']['023']['value']=False
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_postfreeze_rejected(self):
        s=full();s['amylose_fraction']['available_at_utc']='2026-10-16T12:01:00Z'
        with self.assertRaises(H4BError):self.go(s)
    def test_timezone_missing_rejected(self):
        s=full();s['conductivity_W_mK']['available_at_utc']='2026-10-16T10:00:00'
        with self.assertRaises(H4BError):self.go(s)
    def test_invalid_unit_rejected(self):
        s=full();s['thickness_mm']['unit']='cm'
        with self.assertRaises(H4BError):self.go(s)
    def test_nonnumeric_rejected(self):
        for v in (True,float('inf'),float('nan'),-1,'hi'):
            s=full();s['contact_R_K_W']['value']=v
            with self.subTest(v=v),self.assertRaises(H4BError):self.go(s)
    def test_unknown_supplement_null_preserved(self):
        s=full();s['conductivity_W_mK']=obs(None,'W/m/K','UNKNOWN')
        self.assertIsNone(self.go(s)['mechanism_groups']['thermal_wall'])
    def test_unknown_supplement_nonnull_rejected(self):
        s=full();s['conductivity_W_mK']['state']='UNKNOWN'
        with self.assertRaises(H4BError):self.go(s)
    def test_invalid_new_field_rejected(self):
        s=full();s['secret_after_cooking']=obs(99)
        with self.assertRaises(H4BError):self.go(s)
    def test_future_label_ignored(self):
        p=packet();a=self.go(full(),p)
        p['final_rice_observation']={'score':100,'date':'2026-10-16T14:00:00Z'}
        self.assertEqual(self.go(full(),p),a)
    def test_no_mutation(self):
        p=packet();s=full();a=copy.deepcopy(p);b=copy.deepcopy(s)
        self.go(s,p)
        self.assertEqual(p,a);self.assertEqual(s,b)
    def test_determinism(self):self.assertEqual(self.go(full()),self.go(full()))
    def test_only_stop_threshold_not_burn_still_usable(self):
        s=full();s.pop('burn_threshold_C')
        self.assertTrue(self.go(s)['mechanism_groups']['policies']['stop_trigger_hypothetical'] is False)
    def test_ambiguous_impurity_method_rejected(self):
        s=full();s['impurity_mass_fraction']['unit']='count_fraction'
        with self.assertRaises(H4BError):self.go(s)
    def test_untrusted_policy_source_rejected(self):
        p=packet();p['correction_policies']['098']['source']=''
        with self.assertRaises(H4BError):self.go(full(),p)
    def test_end_before_start_guard(self):
        p=packet();p['prestart']['freeze_utc']='2026-10-16T14:00:00Z'
        with self.assertRaises(H4BError):self.go(full(),p)

if __name__=='__main__':unittest.main()
