#!/usr/bin/env python3
"""RIZ112: PRE-T0 laboratory IC* with 44 genuinely consumed inputs.

Research toy / synthetic physical and decision model: NOT calibrated rice quality,
NOT 44 experimentally demonstrated independent causal effects, NOT a recipe.
A parameter can have zero local effect when the corresponding plan is inactive.
"""
from __future__ import annotations
import copy, math
from bridge44 import evaluate44, PRESTART, TWINS, BridgeError, when

class IC44Error(ValueError): pass
VARIETY={'long_white_hypothesis':(1.,1.),'medium_white_hypothesis':(1.10,.88),'short_white_hypothesis':(1.18,.79)}
PROCESS={'polished':(1.,1.),'parboiled':(.89,.79),'unprocessed':(.83,1.12)}
# Synthetic batch characterization: these are hypothesized properties, not a
# magical score based on batch name. An unknown batch must abstain.
BATCH={'lot_A_synthetic':(1.,1.,1.),'lot_B_synthetic':(.93,1.06,1.08),'lot_C_synthetic':(1.07,.96,.92)}
SOURCE={'gas':.98,'electricity':1.02,'charcoal':.89}
BURNER={'gas_burner':.98,'electric_hotplate':1.04,'charcoal_stove':.86}
PAIR={'gas':'gas_burner','electricity':'electric_hotplate','charcoal':'charcoal_stove'}
MATERIAL={'aluminium':205.,'steel':16.,'copper':385.,'ceramic':2.}
BOTTOM={'clean_flat':1.,'slightly_warped':.89,'worn':.74}
VENT={'unvented':.79,'narrow_vent':.94,'vented':1.16}
TOL={'hydration':.40,'thermal':.55,'separation':.36,'integrity':.36,'flavour':.60,'service':.70,'hygiene':.35}

def clamp(x,lo=0.,hi=1.): return min(hi,max(lo,x))
def sigmoid(x):
    x=max(-700.,min(700.,x))
    return 1./(1.+math.exp(-x))
def lookup(table,k,name):
    if k not in table: raise IC44Error('unknown model profile '+name+': '+str(k))
    return table[k]
def scalar(v,rid,lo,hi):
    if type(v) not in (int,float) or not math.isfinite(v) or not lo<=v<=hi:
        raise IC44Error('R'+rid+' not finite or outside synthetic range')
    return float(v)

def simulate(packet):
    trace=evaluate44(packet)
    case=packet['case_inputs']; unknown=[k for k in PRESTART if case[k]['state']=='UNKNOWN']
    if unknown:return {'schema':'riz112/IC44-v2','status':'ABSTAIN_UNKNOWN',
        'missing':unknown,'routes':44,'IC_DEMO_PCT':None,'IC_SCIENTIFIQUE_PCT':None}
    v={k:case[k]['value'] for k in PRESTART}
    for rid in ('007','018','029','030','031','032','042'):
        scalar(v[rid],rid,0.,1.)
    for rid in ('001','008','009','011','025','033','034','035','041','047'):
        scalar(v[rid],rid,0.0000001,100000.)
    for rid in ('002','003','004','005','028','036','040','045'):
        scalar(v[rid],rid,0.,100000.)
    for rid in ('037','038','039'):scalar(v[rid],rid,-20.,120.)
    scalar(v['014'],'014',0.,2.)
    if v['040']>3500:raise IC44Error('altitude outside model scope')
    for rid in ('013','017','019','020','021','022','023'):
        if type(v[rid]) is not bool:raise IC44Error('R'+rid+' expected boolean')
    plans=packet['action_plans']
    for k,p in plans.items():
        if when(p['available_at_utc'])>when(packet['prestart']['freeze_utc']):
            raise IC44Error('future declared plan '+k)
    for k,p in packet.get('correction_policies',{}).items():
        if when(p['available_at_utc'])>when(packet['prestart']['freeze_utc']):
            raise IC44Error('future correction policy '+k)
    def planned(rid):return plans.get(rid,{}).get('status')=='PLANNED'
    var=lookup(VARIETY,v['024'],'variety')
    proc=lookup(PROCESS,v['026'],'processing')
    batch=lookup(BATCH,v['027'],'synthetic batch')
    src=lookup(SOURCE,v['006'],'energy')
    burner=lookup(BURNER,v['016'],'burner')
    material=lookup(MATERIAL,v['010'],'vessel material')
    bottom=lookup(BOTTOM,v['012'],'vessel condition')
    vent=lookup(VENT,v['015'],'steam ventilation')
    compatible=1. if PAIR[v['006']]==v['016'] else .15
    # Hydration mass budget: measured equipment affects dose precision; stocks
    # affect achievable dose; effects only when preparation plan is applicable.
    dose_precision=(1. if v['019'] and planned('050') else .88)*(
                    1. if v['020'] and planned('053') else .90)
    water=min(v['035'],v['002'])*dose_precision
    rinse=0.
    if planned('054'):
        rinse=.45*clamp(v['005']/300.)*(1. if v['021'] and planned('057') else .58)
    retained=v['036']*(1.+.18*(1. if v['021'] and planned('054') else -.5))
    age_factor=math.exp(-v['028']/3000.)
    mass=v['001']
    target_water=mass*v['033']*(1.-.35*v['032'])*(1.+.04*(1.-age_factor))
    dry_solids=mass*(1.-v['032'])
    diffusion=var[0]*proc[0]*batch[0]/max(.2,(v['025']/7.)**2)
    # Coupled heat, evaporation, geometry, pressure and vessel response
    boil=100.-.003*v['040']
    area_ratio=(v['009']/20.)**2
    resistance=v['011']/max(1.,material)
    uniformity=clamp(v['018']*.75+.25*bottom,.05,1.)
    useful_power=v['041']*v['042']*v['007']*src*burner*compatible
    if planned('068') and v['017']:useful_power*=.91
    useful_power*=1./(1.+resistance/2.)*(.8+.2*uniformity)
    lid=(1. if v['013'] and planned('064') else 1.44)*v['014']
    evap=clamp(v['045']*v['047']*area_ratio*lid*vent,0,water+retained)
    heat_loss=max(0.,boil-v['039'])*(.8+area_ratio)
    energy=max(0.,useful_power-heat_loss)*60*v['047']
    need_energy=(water+retained)*4.186*max(0.,boil-v['037'])+mass*1.6*max(0.,boil-v['038'])
    hot=max(0.,energy-need_energy)
    thermal_progress=hot/(v['034']*60*max(1.,useful_power)*.42)*diffusion
    evap+=.00012*hot/2257.
    remaining=max(0.,water+retained-evap)
    absorbed=min(remaining,target_water*min(1.2,max(0.,thermal_progress)))
    hydration=absorbed/max(1.,target_water)
    free_water=max(0.,remaining-absorbed)
    occupancy=(mass/.85+water+retained)/v['008']
    boilover=clamp((occupancy-.58)*1.2)
    # Starch, surface, integrity, temperature and safety proxies
    starch=v['030']*(1.-rinse)*proc[1]*batch[1]
    stickiness=starch*(.55+.45*v['029'])*(1.+.15*free_water/max(1.,mass))
    spatial=(1.-uniformity)*(1.+.25*resistance)
    agitation=.07 if planned('071') and v['022'] else .18
    intact=(1.-v['029'])*(1.-agitation)*(.90+.10*min(1.,thermal_progress))
    burnt=clamp((thermal_progress-1.45)*.19+spatial*.18)
    salt=min(v['003'],2.5) if planned('061') else 0.
    fat=min(v['004'],6.) if planned('062') else 0.
    salt_target=max(.1,mass*.011)
    salt_match=math.exp(-abs(salt-salt_target)/max(.5,salt_target))
    separation_help=clamp(1.+(fat/max(1.,mass))*3.,1.,1.22)
    fluff=1. if planned('077') and v['022'] else .88
    serving=1. if v['023'] and planned('081') else .88
    serve_temp=boil-(boil-v['039'])*(1.-serving)*.95
    dose_sigma=(.015 if v['019'] and planned('050') else .07)+(
                .015 if v['020'] and planned('053') else .07)
    feasibility=clamp(v['002']/max(1.,v['035']))*clamp(v['008']/max(1.,mass/.85+v['035']+retained))*compatible*v['007']
    hygiene=clamp(1.-v['031']*batch[2]*6.)
    margins={
      'hydration':(hydration-1.)/TOL['hydration'],
      'thermal':(thermal_progress-1.)/TOL['thermal'],
      'separation':(.52-stickiness/max(.1,separation_help*fluff))/TOL['separation'],
      'integrity':(intact-burnt-boilover*.4-.70)/TOL['integrity'],
      'flavour':(salt_match+fat/max(1.,mass)*2.-.50)/TOL['flavour'],
      'service':(serve_temp-55.)/(TOL['service']*30.),
      'hygiene':(hygiene-.83)/TOL['hygiene']
    }
    # Illustrative conjunctive probability proxy with unvalidated independence
    # and independently disclosed channel tolerances, NOT measured rice success.
    ice=100.*math.prod(sigmoid(m) for m in margins.values())*feasibility*math.exp(-dose_sigma*.8)
    return {'schema':'riz112/IC44-v2','status':'SYNTHETIC_NOT_CALIBRATED',
        'routes':44,'evaluated_routes':trace['numeric_or_logic_calculations'],
        'IC_DEMO_PCT':round(ice,10),'IC_SCIENTIFIQUE_PCT':None,
        'quality_channels':{k:round(sigmoid(m),8) for k,m in margins.items()},
        'physical_proxies':{
          'remaining_water_g':remaining,'target_water_g':target_water,
          'hot_progress':thermal_progress,'hydration_ratio':hydration,
          'evaporation_g':evap,'dry_solids_g':dry_solids,'batch_diffusivity':batch[0],
          'salt_plan_g':salt,'fat_plan_g':fat,'serve_temp_C':serve_temp,
          'feasibility':feasibility,'dose_sigma':dose_sigma},
        'assumptions':{'synthetic_lot_table':BATCH,
          'synthetic_variety_table':VARIETY,'synthetic_processing_table':PROCESS,
          'unfitted_channel_tolerances':TOL,'unverified_independence':True,
          'no_real_trials':True,'not_real_probability':True}}

def perturb(packet,rid,value):
    if rid not in PRESTART:raise IC44Error('not one of 44')
    p=copy.deepcopy(packet)
    p['case_inputs'][rid]['value']=value
    p['case_inputs'][rid]['state']='ASSUMPTION'
    if rid in TWINS:p['prestart']['inputs'][TWINS[rid]]['value']=value
    return p

def audit_44(packet,alternatives):
    base=simulate(packet)
    checks=[]
    for rid in PRESTART:
        r=simulate(perturb(packet,rid,alternatives[rid]))
        delta=None if base['IC_DEMO_PCT'] is None or r['IC_DEMO_PCT'] is None else round(r['IC_DEMO_PCT']-base['IC_DEMO_PCT'],10)
        checks.append({'id':rid,'delta_ICE_DEMO_PCT':delta,'changed':delta is not None and abs(delta)>1e-8})
    return {'schema':'riz112/IC44-ablation-v2','routed':44,
        'baseline_ICE_demo':base['IC_DEMO_PCT'],
        'IC_demo_changed_count':sum(x['changed'] for x in checks),
        'cases':checks,'IC_scientifique':None}
