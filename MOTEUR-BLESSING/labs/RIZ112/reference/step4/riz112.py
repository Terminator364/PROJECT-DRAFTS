#!/usr/bin/env python3
"""RIZ-112 ETAPE 4 — transparent pre-start computation graph (not a calibrated predictor).

Standard-library-only educational engineering prototype. No recipe, no success probability.
Scientific constants simplified: heat capacity of water 4.186 J/(g K), latent heat
of vaporization of water at ~100 C approx 2257 J/g. Rice heat capacity is an
explicit hypothesis in each packet. Ambient/altitude/actual heat loss are not modeled.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

INPUT_SPECS = {
    "rice_mass_g": ("OBSERVED", "01", "masse de riz"),
    "rice_variety": ("OBSERVED", "24", "variété (contexte, pas calcul direct)"),
    "water_added_g": ("PLANNED", "35", "eau initialement prévue"),
    "water_retained_g": ("ASSUMPTION", "36", "eau résiduelle attendue"),
    "water_initial_C": ("OBSERVED", "37", "température eau initiale"),
    "rice_initial_C": ("OBSERVED", "38", "température riz initiale"),
    "power_W": ("PLANNED", "41", "puissance nominale du foyer"),
    "transfer_efficiency": ("ASSUMPTION", "42", "rendement thermique de transfert"),
    "total_heating_min": ("PLANNED", "47", "durée de chauffe annoncée"),
    "evap_reference_g_per_min": ("ASSUMPTION", "45", "vitesse référence d'évaporation"),
    "lid_multiplier": ("ASSUMPTION", "14", "effet du couvercle sur perte vapeur"),
    "water_capacity_g_per_g": ("ASSUMPTION", "33", "capacité d'hydratation ciblée"),
    "hot_time_needed_min": ("ASSUMPTION", "34", "temps chaud nécessaire pour cette hypothèse de riz"),
    "rice_heat_capacity_J_gK": ("ASSUMPTION", "24", "capacité calorifique supposée selon le grain"),
    "surface_starch_index": ("ASSUMPTION", "30", "indice initial amidon de surface, non texture"),
    "rinse_removal_fraction": ("PLANNED", "54", "fraction d'amidon retirée prévue, incertaine"),
}

REQUIRED = set(INPUT_SPECS)
ALLOWED_TOP = {"preparation_id", "freeze_utc", "start_utc", "inputs"}
POSITIVE = {"rice_mass_g", "power_W", "total_heating_min", "water_capacity_g_per_g",
            "hot_time_needed_min", "rice_heat_capacity_J_gK"}
NONNEGATIVE = {"water_added_g", "water_retained_g", "evap_reference_g_per_min", "lid_multiplier"}
FRACTIONS = {"transfer_efficiency", "surface_starch_index", "rinse_removal_fraction"}

class InvalidPacket(ValueError):
    pass


def utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise InvalidPacket(f"{label}: horodatage UTC ISO-8601 manquant")
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if d.tzinfo is None:
            raise ValueError('timezone missing')
        return d.astimezone(timezone.utc)
    except ValueError as e:
        raise InvalidPacket(f"{label}: horodatage sans fuseau ou invalide") from e


def check_packet(packet: dict) -> dict:
    if not isinstance(packet, dict):
        raise InvalidPacket("paquet JSON non objet")
    if set(packet) != ALLOWED_TOP:
        raise InvalidPacket("clés racine non autorisées ou manquantes: " + str(sorted(set(packet) ^ ALLOWED_TOP)))
    frozen = utc(packet['freeze_utc'], 'freeze_utc')
    start = utc(packet['start_utc'], 'start_utc')
    if not frozen < start:
        raise InvalidPacket("freeze_utc doit être STRICTEMENT avant start_utc")
    if not isinstance(packet['preparation_id'], str) or not packet['preparation_id'].strip():
        raise InvalidPacket('preparation_id vide')
    rows = packet['inputs']
    if not isinstance(rows, dict) or set(rows) != REQUIRED:
        raise InvalidPacket('inputs: manque/excès: ' + str(sorted(set(rows) ^ REQUIRED)) if isinstance(rows, dict) else 'inputs non objet')
    vals = {}
    for key, (expected, case, _) in INPUT_SPECS.items():
        row = rows[key]
        if not isinstance(row, dict) or set(row) != {"value", "available_at_utc", "kind", "source"}:
            raise InvalidPacket(key + ' : métadonnées {value, available_at_utc, kind, source} requises')
        if row['kind'] != expected:
            raise InvalidPacket(key + f' : rôle attendu {expected}')
        if not isinstance(row['source'], str) or not row['source'].strip():
            raise InvalidPacket(key + ' : provenance déclarée obligatoire')
        if utc(row['available_at_utc'], key+'.available_at_utc') > frozen:
            raise InvalidPacket(key + ' : information datée APRÈS le gel')
        value = row['value']
        if key == 'rice_variety':
            if not isinstance(value, str) or not value:
                raise InvalidPacket('rice_variety: chaîne attendue')
        elif type(value) not in (float, int) or not -1e20 < float(value) < 1e20:
            raise InvalidPacket(key + ' : valeur réelle finie attendue, UNKNOWN ≠ ZERO')
        elif key in POSITIVE and value <= 0:
            raise InvalidPacket(key + ' : strictement positif attendu')
        elif key in NONNEGATIVE and value < 0:
            raise InvalidPacket(key + ' : négatif interdit')
        elif key in FRACTIONS and not (0 < value <= 1 if key == "transfer_efficiency" else 0 <= value <= 1):
            raise InvalidPacket(key + ' : fraction hors [0,1]')
        elif key in ('water_initial_C','rice_initial_C') and not 0 <= value < 100:
            raise InvalidPacket(key + ' : température hors plage du prototype [0,100)')
        vals[key] = value
    return vals


def analyze(packet: dict) -> dict:
    v = check_packet(packet)
    graph = []

    def node(code: str, label: str, formula: str, deps: list[str], value: float, unit: str, cases: list[str]) -> float:
        value = round(float(value), 6)
        graph.append({"node": code,"label": label, "formula": formula,"dependencies": deps,
                      "value": value, "unit": unit, "cases": cases})
        return value

    # A mass balance and a deliberately simple upper-bound thermal model.
    water = node('W0','Eau au départ','water_added_g + water_retained_g',
                 ['water_added_g','water_retained_g'],
                 v['water_added_g'] + v['water_retained_g'],'g',['35','36'])
    effective_power = node('P','Transfert thermique utile (hypothèse)', 'power_W * transfer_efficiency',
                           ['power_W','transfer_efficiency'], v['power_W']*v['transfer_efficiency'], 'W',['41','42'])
    sensible_heat = node('Q','Énergie théorique pour atteindre 100 °C',
         '(W0 * 4.186 * (100 - water_initial_C)) + (rice_mass_g * rice_heat_capacity_J_gK * (100 - rice_initial_C))',
         ['W0','water_initial_C','rice_mass_g','rice_heat_capacity_J_gK','rice_initial_C'],
         water * 4.186 * (100 - v['water_initial_C']) + v['rice_mass_g']*v['rice_heat_capacity_J_gK']*(100-v['rice_initial_C']),
         'J',['01','24','37','38'])
    preheat_min = node('T_boiling', 'Temps idéal de montée à température', 'Q / (P * 60)',
                       ['Q','P'], sensible_heat/(effective_power*60), 'min',['41','42'])
    hot_time = node('T_hot','Durée chaude restante','max(0, total_heating_min - T_boiling)',
                    ['total_heating_min','T_boiling'], max(0,v['total_heating_min']-preheat_min),'min',['47'])
    evap_rate = node('E_rate','Évaporation de scénario liée au couvercle',
                     'evap_reference_g_per_min * lid_multiplier',
                     ['evap_reference_g_per_min','lid_multiplier'],
                     v['evap_reference_g_per_min']*v['lid_multiplier'],'g/min',['14','45'])
    evap_energy_limit = node('E_energy_cap','Limite d’évaporation énergétique idéale',
                             'P * T_hot * 60 / 2257', ['P','T_hot'], effective_power*hot_time*60/2257,
                             'g',['41','42','45'])
    evap = node('E_evap','Évaporation estimée bornée','min(W0, E_rate * T_hot, E_energy_cap)',
                ['W0','E_rate','T_hot','E_energy_cap'],min(water,evap_rate*hot_time,evap_energy_limit),
                'g',['14','45','47'])
    water_left = node('W_after','Eau restante (absorbée + libre)','W0 - E_evap',
                      ['W0','E_evap'],water-evap,'g',['35','36','45'])
    target = node('W_target','Capacité d’hydratation cible supposée','rice_mass_g * water_capacity_g_per_g',
                  ['rice_mass_g','water_capacity_g_per_g'],v['rice_mass_g']*v['water_capacity_g_per_g'],
                  'g',['01','33'])
    thermal_fraction = node('F_hot','Progrès thermique indicatif (pas gélatinisation mesurée)',
                            'min(1, T_hot / hot_time_needed_min)', ['T_hot','hot_time_needed_min'],
                            min(1,hot_time/v['hot_time_needed_min']),'1',['34','47'])
    potential_absorb = node('W_potential','Hydratation atteignable selon hypothèse thermique',
                            'W_target * F_hot', ['W_target','F_hot'],target*thermal_fraction,
                            'g',['33','34'])
    absorbed = node('W_absorb','Eau possiblement absorbée','min(W_after, W_potential)',
                    ['W_after','W_potential'],min(water_left,potential_absorb),'g',['33','35','45'])
    free = node('W_free','Eau libre théorique','W_after - W_absorb',
                ['W_after','W_absorb'],water_left-absorbed,'g',['35','45'])
    unmet = node('W_shortfall','Hydratation cible non atteinte','W_target - W_absorb',
                 ['W_target','W_absorb'],target-absorbed,'g',['33','34'])
    residual_starch = node('S_residual','Indice amidon résiduel (NON texture)',
                           'surface_starch_index * (1 - rinse_removal_fraction)',
                           ['surface_starch_index','rinse_removal_fraction'],
                           v['surface_starch_index']*(1-v['rinse_removal_fraction']),
                           'index',['30','54'])
    audit_used = sorted({case for n in graph for case in n['cases']}, key=int)
    notes = ['Les coefficients de cuisson sont des hypothèses fournies dans le JSON et non calibrées.',
             'Les températures, pertes vers ambiance et phénomènes de gélatinisation sont simplifiés.',
             'L’amidon de surface n’est PAS converti en grains collants : lien expérimental non établi ici.',
             'Les horodatages et provenances sont déclaratifs ; une archive indépendante serait nécessaire pour attester la date.']
    if preheat_min > v['total_heating_min']:
        notes.append('Sous les hypothèses fournies, l’atteinte de 100 °C est hors du temps prévu.')
    if evap_rate > effective_power*60/2257:
        notes.append('Le débit d’évaporation demandé excède la limite énergétique idéale ; scénario écrêté.')
    return {
        'preparation_id':packet['preparation_id'],
        'goal':'riz moelleux, grains séparés (qualité finale Q >= 85/100)',
        'mode':'PRE_START_ENGINEERING_SCENARIO',
        'calibrated_success_probability_percent':None,
        'decision':'ABSTAIN_IC_NON_CALIBRE',
        'graph_trace':graph,
        'diagnostics':{
            'mass_balance_residual_g':round(water-evap-absorbed-free,5),
            'hydration_shortfall_g':unmet,'free_water_g':free,
            'thermal_progress_proxy':thermal_fraction,
            'surface_starch_proxy_not_texture':residual_starch,
            'model_assumptions':'illustrative mass and energy balance; NOT validated edible texture or safety',
            'no_doubled_evaporation_loss':True,
        },
        'traceability':{
            'cases_consumed':audit_used,
            'cases_consumed_count':len(audit_used),
            'catalogue_scope':'112 cases specified in conceptual design, only subset executed in step 4',
            'input_roles':{k:spec[0] for k,spec in INPUT_SPECS.items()},
            'unused_context_inputs':['rice_variety'],
            'outcome_fields_used':[],
            'third_party_pre_start_capture_verified':False,
        },
        'caveats':notes,
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('packet',type=Path)
    p.add_argument('-o','--output',type=Path)
    args=p.parse_args()
    packet=json.loads(args.packet.read_text(encoding='utf-8'))
    result=analyze(packet)
    data=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.write_text(data,encoding='utf-8')
    else:
        print(data,end='')

if __name__=='__main__':
    main()
