"""RIZ112 V13: 112 semantic categories -> typed subparameters -> anticipation rules.

Mappings are engineering hypotheses, not calibrated physics. 14 Q-target rows
are definitions, not post-start measured predictors. No arbitrary 112 weights.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'reference/step4/CATALOGUE_112_ROLES_ETAPE4.json'

# 44 data inputs have one or more meaningful subparameter slots each. Mechanism
# roles define channels, not an arbitrary numerical parameter per case.
CHANNELS={
'001':'mass_and_required_water','002':'available_water_and_actual_dose',
'003':'taste_resource','004':'surface_adhesion_hypothesis',
'005':'rinsing_water_stock','006':'heat_source_compatibility',
'007':'heat_reliability','008':'vessel_capacity_and_spill',
'009':'contact_area_and_evaporation','010':'thermal_conduction_and_safety',
'011':'wall_thermal_resistance','012':'bottom_contact_quality',
'013':'lid_presence','014':'steam_loss_multiplier','015':'steam_venting',
'016':'stove_to_vessel_coupling','017':'power_control_availability',
'018':'hot_spot_distribution','019':'mass_measurement_uncertainty',
'020':'water_dosing_uncertainty','021':'drain_retained_water',
'022':'stirring_tool_compatibility','023':'service_availability',
'024':'variety_drives_hydration_hypothesis','025':'grain_length_and_hydration_time',
'026':'milling_and_surface_starch','027':'lot_uncertainty',
'028':'storage_age_uncertainty','029':'broken_grain_integrity',
'030':'surface_starch','031':'impurity_and_food_safety',
'032':'initial_moisture_and_dry_mass','033':'water_absorption_target',
'034':'gelatinization_duration','035':'planned_water_mass',
'036':'retained_rinse_water','037':'water_initial_temperature',
'038':'rice_initial_temperature','039':'ambient_thermal_losses',
'040':'boiling_point_altitude','041':'planned_power','042':'baseline_heat_transfer',
'045':'evaporation_rate','047':'planned_heating_duration'}
ACTION_GROUPS={
'measurement':('049','050','051','052','053'),
'rinse':('054','055','056','057','058'),
'composition':('059','060','061','062','063'),
'lid':('064','070','080'),
'heat':('065','066','067','068','069','072','073','074'),
'handling':('071','075','076','077','078','079'),
'service':('081','082','083','084','085')}
POLICY_GROUPS={
'water':('086','087','091'), 'heat':('088','089','092'),
'lid':('090',),'volume':('093',),'scorch':('094',),
'grain':('095','096','097'),'terminal':('098',)}
TARGET_GROUPS={
'food_safety':('099',), 'quantity':('100',),
'hydration':('101',), 'separation':('102',),
'heat_uniformity':('103',),'grain_integrity':('104',),
'free_water':('105',),'scorch':('106',),
'service_temperature':('107',),'taste':('108',),
'aroma':('109',),'appearance':('110',),
'holding_quality':('111',),'final_outcome':('112',)}
DERIVED={'043':'boiling_time','044':'simmer_stability','046':'steam_leakage','048':'water_balance'}

def inverse(groups):
 return {k:name for name,keys in groups.items() for k in keys}

A=inverse(ACTION_GROUPS);P=inverse(POLICY_GROUPS);T=inverse(TARGET_GROUPS)
assert len(CHANNELS)==44 and len(A)==37 and len(P)==13 and len(T)==14 and len(DERIVED)==4

def build_registry():
 catalog=json.loads(CATALOG.read_text(encoding='utf8'))['cases']
 rows={}
 for x in catalog:
  i=x['id'];label=x['name']
  if i in CHANNELS:
   role='INPUT';group=CHANNELS[i]
   sub=[{'key':'declared_value','meaning':label,'type':'input-or-prior'},
        {'key':'mechanism_channel','meaning':group,'type':'causal-hypothesis-slot'},
        {'key':'uncertainty','meaning':'Distribution or evidence status of this property','type':'uncertainty-slot'}]
   consequence='value/context may change an upstream mechanism; quantitative effect only if mapped and justified'
  elif i in DERIVED:
   role='DERIVED';group=DERIVED[i];sub=[{'key':'computed_from_upstream','meaning':group,'type':'derived-formula'},
    {'key':'uncertainty_propagation','meaning':'Derive with upstream uncertainty','type':'derived-uncertainty'}];consequence='computed, never randomly assigned as an independent input'
  elif i in A:
   role='PLANNED_ACTION';group=A[i];sub=[{'key':'predeclared_status','meaning':'planned/not planned/unknown','type':'plan'},
    {'key':'applicability','meaning':'may be attempted only when resources are available','type':'conditional-branch'},
    {'key':'resulting_mechanism','meaning':group,'type':'hypothesis-channel'}];consequence='changes anticipated execution, not proof the action happened'
  elif i in P:
   role='CONDITIONAL_POLICY';group=P[i];sub=[{'key':'trigger','meaning':'future event described only as scenario','type':'anticipated-branch'},
    {'key':'response','meaning':'declared contingent response','type':'policy'},
    {'key':'resulting_mechanism','meaning':group,'type':'hypothesis-channel'}];consequence='branch probabilities must be stipulated or learned; do not use realized event'
  else:
   role='TARGET_DEFINITION';group=T[i];sub=[{'key':'measurement_definition','meaning':label,'type':'target-definition'},
    {'key':'quality_observation_poststart','meaning':'excluded from inputs before start','type':'future-label'}];consequence='defines probability target or audit; never a future observed predictor'
  for child in sub:
   if child['type']=='input-or-prior':children=['value','unit','source','available_at_utc']
   elif child['type']=='causal-hypothesis-slot':children=['mechanism','upstream_links','downstream_links']
   elif child['type']=='uncertainty-slot':children=['observed_vs_assumed','range_or_distribution','missing_data_policy']
   elif child['type']=='derived-formula':children=['upstream_values','formula','output_units']
   elif child['type']=='derived-uncertainty':children=['distribution','dependency','correlation']
   elif child['type']=='plan':children=['planned_status','declared_source','freeze_time']
   elif child['type']=='conditional-branch':children=['resource_test','feasible_branch','fallback_branch']
   elif child['type']=='hypothesis-channel':children=['upstream_variable','physical_mechanism','anticipated_outcome']
   elif child['type']=='anticipated-branch':children=['trigger_definition','probability_prior','outcome_scenarios']
   elif child['type']=='policy':children=['response_if_triggered','resource_constraint','scenario_effect']
   elif child['type']=='target-definition':children=['measurement_method','threshold','quality_dimension']
   else:children=['poststart_label','forbidden_prestart','future_evidence']
   child['sub_subparameters']=[{'key':key,'status':'REQUIRES_CALIBRATION_OR_EXPLICIT_SCENARIO'} for key in children]
  rows[i]={'id':i,'name':label,'role':role,'group':group,'subparameters':sub,
           'anticipation':consequence,'calibrated_effect':False}
 assert len(rows)==112 and len({a for x in rows.values() for a in [x['id']]})==112
 return {'schema':'riz112/stage13/hierarchical-roles/v1','count':len(rows),
  'note':'112 semantic roles with subparameters; not 112 independent numeric drivers; none validated',
  'cases':rows}

if __name__=='__main__':print(json.dumps(build_registry(),indent=2,ensure_ascii=False))
