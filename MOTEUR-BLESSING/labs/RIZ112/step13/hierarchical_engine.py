#!/usr/bin/env python3
"""RIZ112 hierarchical prestart demonstrator (not a calibrated quality model).

A root rubric may have multiple nested, typed subparameters and condition-dependent
anticipations. Physical material properties are NOT direct quality weights.
The heat-through-wall constraint is a steady-state upper-bound analogy, not a
validated heating or food-safety model; only Q*_DEMO is estimated by the existing
Step9 toy model. No information after T0 is used.
"""
from __future__ import annotations
import copy, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step9'))
from ic_simulation_v1 import simulate,CONTRACT
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import PRESTART,FORECAST,ACTIONS,POLICIES,OUTCOMES

# Representative k at ordinary temperatures (W m^-1 K^-1), NOT exact pot values.
# Copper, iron from engineeringtoolbox.com/thermal-conductivity-metals-d_858.html;
# fireclay and oak wood from engineeringtoolbox.com/thermal-conductivity-d_429.html
MATERIALS={
 'copper':{'k':401.0,'evidence':'TABULATED_GENERIC_APPROXIMATION','direct_heat_approved':True},
 'iron':{'k':83.5,'evidence':'TABULATED_GENERIC_APPROXIMATION','direct_heat_approved':True},
 'metal':{'k':83.5,'evidence':'GENERIC_IRON_PROXY_FOR_LEGACY_LABEL','direct_heat_approved':True},
 'ceramic_rated':{'k':1.4,'evidence':'FIRECLAY_PROXY_NOT_CERTIFIED_COOKWARE','direct_heat_approved':True},
 'wood_unrated':{'k':0.16,'evidence':'OAK_PROXY_NOT_CERTIFIED_COOKWARE','direct_heat_approved':False},
}

class HierarchyError(ValueError):pass

def registry(catalogue:dict)->dict:
    entries=catalogue['cases']
    if len(entries)!=112 or len({r['id'] for r in entries})!=112:raise HierarchyError('112 unique rubrics required')
    result={}
    for item in entries:
        key=item['id'];role=item['temporal_role']
        if key in PRESTART:
            children={'donnee_initiale':{'valeur':'FROM_INPUT_JSON','unite':'CASE_SPECIFIC'},
                      'mesure':{'horodatage':'PRE_T0_ONLY','provenance':'SOURCE_DECLARED','fiabilite':'UNMEASURED'},
                      'incertitude':{'aleatoire':'NOT_ESTIMATED','epistemique':'NOT_ESTIMATED'}}
        elif key in FORECAST:
            children={'prevision':{'modele':'MUST_BE_DEFINED','intervalle':'UNKNOWN','source':'PRE_T0'},
                      'incertitude':{'dispersion':'UNKNOWN','validite':'NOT_VALIDATED'}}
        elif key in ACTIONS:
            children={'plan':{'statut':'PLANNED_OR_NOT_PLANNED','declencheur':'PREDECLARED'},
                      'execution_anticipable':{'probabilite':'NOT_LEARNED','conditions':'RESOURCE_DEPENDENT'}}
        elif key in POLICIES:
            children={'condition':{'declencheur':'PREDECLARED','indicateur':'FORECAST_OR_SIMULATION'},
                      'reponse':{'action':'PREDECLARED','effet':'NOT_LEARNED'}}
        else:
            children={'mesure_finale':{'methode':'TO_BE_APPROVED','date':'POST_T0_ONLY'},
                      'contrat':{'seuil':'TARGET_DECLARED','role':'OUTPUT_NOT_PREDICTOR'}}
        # Meaningful deep subparameters in selected physical/behavioural rubrics.
        special={
         '010':{'materiau':{'famille':'WOOD_METAL_CERAMIC','proprietes_thermiques':{'conductivite_W_mK':'MATERIAL_TABLE_OR_MEASURED','temperature_dependance':'UNMEASURED'},
                              'compatibilite':{'methode_chauffe':'METHOD_DEPENDENT','revetement_contact_alimentaire':'UNVERIFIED'}},
                'fond':{'epaisseur_mm':'CASE_011','diametre_cm':'CASE_009','etat':'CASE_012'},
                'liaisons':{'source':'CASE_016','puissance':'CASE_041','rendement':'CASE_042'}},
         '009':{'geometrie':{'diametre_cm':'DIRECT_INPUT','aire_m2':'PI_D2_OVER_4'},'echange':{'epaisseur_mm':'CASE_011'}},
         '011':{'fond':{'epaisseur_mm':'DIRECT_INPUT','materiau':'CASE_010'},'conduction':{'resistance_K_W':'THICKNESS_OVER_K_AREA'}},
         '013':{'couvercle':{'present':'DIRECT_INPUT','ajustement':'CASE_014'},'vapeur':{'evacuation':'CASE_015','fuites':'CASE_046'}},
         '014':{'etancheite':{'coefficient_evaporation':'HYPOTHESIS','present':'CASE_013'}},
         '001':{'riz':{'masse_g':'DIRECT_INPUT','lot':'CASE_027','humidite':'CASE_032'},'demande':{'cible_eau_g':'CASE_033'}},
         '035':{'eau':{'masse_initiale_g':'DIRECT_INPUT','eau_retenue_g':'CASE_036'},'disponibilite':{'stock_g':'CASE_002'}},
         '041':{'source':{'puissance_nominale_W':'DIRECT_INPUT','regulation':'CASE_017'},'chaleur':{'rendement':'CASE_042'}},
         '042':{'transfert':{'rendement_base':'DIRECT_INPUT','resistance_paroi':'CASES_009_010_011'},
                'interface':{'deltaT_K':'HYPOTHESIS','R_contact_K_W':'HYPOTHESIS'}},
         '024':{'variete':{'identite':'DIRECT_INPUT','traitement':'CASE_026'},'profil':{'capacite_hydratation':'CASE_033','temps_chaud':'CASE_034'}},
         '054':{'rincage':{'decision':'PREDECLARED','disponibilite_eau':'CASE_005'},'amidon':{'initial':'CASE_030','fraction_eliminee':'MEASURE_OR_ASSUMPTION'}},
         '087':{'manque_eau':{'seuil_declencheur':'PREDECLARED','quantite_reponse':'PREDECLARED'},'execution':{'stock_disponible':'CASE_002'}},
         '098':{'non_recuperable':{'conditions':'PREDECLARED','decision':'POLICY_NOT_OBSERVED'}},
        }
        if key in special:children.update(special[key])
        result[key]={'name':item['name'],'temporal_role':role,'children':children,
                     'numeric_effect_validated':False,'hierarchy_is_prediction_proof':False}
    return result

def _set(packet:dict,key:str,value,physical_field:str|None=None):
    packet['case_inputs'][key].update(value=value,state='ASSUMPTION',source='STAGE13_HIERARCHICAL_SCENARIO')
    if physical_field is not None:
        packet['prestart']['inputs'][physical_field].update(value=value,source='STAGE13_HIERARCHICAL_SCENARIO')

def evaluate(packet:dict, *, material:str,heat_path:str='direct',
             wall_mm:float|None=None,contact_resistance_K_W:float=.065,
             driving_deltaT_K:float=24., diameter_cm:float|None=None, lid_present:bool|None=None,
             water_g:float|None=None, measured_k:float|None=None,
             draws:int=500,seed:int=20261017)->dict:
    if material not in MATERIALS:raise HierarchyError('unknown material: explicit properties required')
    if heat_path not in {'direct','indirect_metal_insert'}:raise HierarchyError('heat path must be stated')
    if any(type(x) not in (int,float) or not math.isfinite(x) or x<=0
           for x in (contact_resistance_K_W,driving_deltaT_K)):
        raise HierarchyError('positive finite thermal assumptions required')
    if measured_k is not None and (type(measured_k) not in (int,float) or not math.isfinite(measured_k) or measured_k<=0):
        raise HierarchyError('measured k must be positive finite')
    p=copy.deepcopy(packet)
    original_inputs=p['prestart']['inputs']
    predictions=[];warnings=[]
    if lid_present is not None:
        if type(lid_present)!=bool:raise HierarchyError('lid bool required')
        _set(p,'013',lid_present)
        # The plan cannot conjure a missing lid; physical reality wins over a future action.
        if not lid_present:
            for action in ('064','070','080'):
                if p['action_plans'][action]['status']=='PLANNED':
                    p['action_plans'][action]['status']='NOT_PLANNED'
                    predictions.append({'id':'ANTICIPATE_NO_LID','action':action,'kind':'RESOURCE_CONSTRAINED_PLAN'})
        _set(p,'014',1. if lid_present else 2.2,'lid_multiplier')
        predictions.append({'id':'ANTICIPATE_VAPOR_LOSS','condition':'lid_present',
                            'factor':p['prestart']['inputs']['lid_multiplier']['value'],'status':'UNVALIDATED_VAPOR_MULTIPLIER'})
    if water_g is not None:
        if type(water_g) not in (int,float) or not math.isfinite(water_g) or water_g<0:
            raise HierarchyError('water_g must be >= 0')
        _set(p,'035',water_g,'water_added_g')
    base_power=original_inputs['power_W']['value']
    base_eta=original_inputs['transfer_efficiency']['value']
    diameter_cm=p['case_inputs']['009']['value'] if diameter_cm is None else diameter_cm
    thick_mm=wall_mm if wall_mm is not None else p['case_inputs']['011']['value']
    if any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in (diameter_cm,thick_mm)):
        raise HierarchyError('physical diameter and thickness required')
    if wall_mm is not None:_set(p,'011',wall_mm)
    _set(p,'009',diameter_cm)
    # For a composite wood vessel with a metal insert, the actual HEATED WALL is metal.
    # No claim that an unrated wooden receptacle is fire-safe.
    conductive_material='iron' if heat_path=='indirect_metal_insert' else material
    k=measured_k if measured_k is not None else MATERIALS[conductive_material]['k']
    A=math.pi*(diameter_cm/200)**2
    R_wall=(thick_mm/1000)/(k*A)
    R_total=contact_resistance_K_W+R_wall
    qmax=driving_deltaT_K/R_total
    eta=min(base_eta,qmax/base_power)
    _set(p,'010',material)
    if material=='wood_unrated' and heat_path=='direct':
        # Do not instruct cooking in an unrated wooden vessel over direct heat.
        # Output a *scenario-specific feasibility result*, not an empirical risk %.
        return {'status':'UNSAFE_DIRECT_HEAT_PATH','ic_demo_percent':0.0,
                'ic_demo_interpretation':'STRUCTURAL_ZERO_IN_ASSUMED_SAFE_PROCESS_MODEL_NOT_EMPIRICAL_SUCCESS_PROBABILITY',
                'scientific_ic_percent':None,'no_poststart_input':True,
                'material':material,'heat_path':heat_path,'anticipations':predictions+[{'id':'ANTICIPATE_HEAT_COMPATIBILITY','reason':'unrated wooden vessel on direct heat lacks safe validated thermal path','decision':'ASSUMED_SAFE_PATH_UNAVAILABLE'}],
                'warning':'Do not attempt direct heating of an unrated wooden vessel; 0 is a model convention, not a measured probability of rice quality.'}
    _set(p,'042',eta,'transfer_efficiency')
    predictions.append({'id':'ANTICIPATE_WALL_CONDUCTION','equation':'R_wall=t/(k*A); P_wall_max=deltaT/(R_wall+R_contact); eta=min(eta_nominal,P_wall_max/P_heater)',
                        'material':conductive_material,'k_W_mK':k,'diameter_cm':diameter_cm,'thickness_mm':thick_mm,
                        'R_wall_K_W':round(R_wall,6),'R_total_K_W':round(R_total,6),'power_wall_upper_bound_W':round(qmax,3),
                        'effective_transfer_efficiency':round(eta,6),'assumption':'steady-state illustrative thermal circuit'} )
    # Remove ONLY impossible planned lid actions, keep all other conflicts auditable.
    try:r=simulate(p,json.loads(CONTRACT.read_text(encoding='utf-8')),draws,seed)
    except Exception as ex:raise HierarchyError('base simulator failed: '+str(ex)) from ex
    return {'status':r['status'],'material':material,'heat_path':heat_path,
            'ic_demo_percent':r.get('ic_demo_percent'),'scientific_ic_percent':None,
            'baseline_q_demo':r.get('baseline_q_demo'),'anticipations':predictions,
            'thermal_path':{'conductivity_W_mK':k,'area_m2':A,'wall_thickness_mm':thick_mm,'R_wall_K_W':R_wall,'effective_eta':eta},
            'warnings':warnings+['Q*_DEMO uses four unvalidated quality proxies, not actual rice quality',
                                 'contact resistance and driving delta T are scenario assumptions, not measurements',
                                 'all pot/safety compatibility assumptions are NOT certified'],
            'no_poststart_input':True,'source_packet_112_roles_preserved':True,
            'details':r.get('conflicts',[])}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--packet',type=Path,default=ROOT/'step6/examples/A_couvercle_ajuste_112.json')
    ap.add_argument('--material',default='copper')
    ap.add_argument('--lid',choices=['yes','no'])
    ap.add_argument('--water',type=float)
    ap.add_argument('--diameter-cm',type=float)
    ap.add_argument('--wall-mm',type=float)
    ap.add_argument('--draws',type=int,default=1000)
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    lid=None if a.lid is None else a.lid=='yes'
    p=json.loads(a.packet.read_text(encoding='utf8'))
    output=evaluate(p,material=a.material,lid_present=lid,water_g=a.water,diameter_cm=a.diameter_cm,wall_mm=a.wall_mm,draws=a.draws)
    s=json.dumps(output,ensure_ascii=False,indent=2)+'\n'
    if a.out:a.out.write_text(s,encoding='utf8')
    else:print(s,end='')
