#!/usr/bin/env python3
"""FACTORY 3.0 G1-G4 and copyright/owner release gate. Nonpublishing checker."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE = HERE / 'docs' / 'A4_ACCEPTANCE_EVIDENCE.json'
DEFAULT_REPORT = HERE / 'docs' / 'A4_RELEASE_GATE_REPORT.json'


def evaluate(evidence):
    def passed(name):
        return evidence.get(name) is True
    gates = {
        'G1_FUNCTIONAL': 'PASS' if all(passed(k) for k in ('unit_tests','python_tests','two_complete_missions','save_roundtrip','collision_review')) else 'BLOCKED',
        'G2_VISUAL': 'PASS' if all(passed(k) for k in ('real_webgl_capture','user_visual_acceptance','visual_reference_comparison')) else 'BLOCKED',
        'G3_TARGET_PERFORMANCE': 'PASS' if all(passed(k) for k in ('hp_fps_memory','a21s_fps_memory','a21s_thermal_battery')) else 'BLOCKED',
        'G4_REAL_PLAYABILITY': 'PASS' if all(passed(k) for k in ('hp_human_15min','a21s_human_15min','iphone_real_browser')) else 'BLOCKED',
        'A1_ENGINE_DECISION': 'PASS' if all(passed(k) for k in ('three_engines_full_dynamic_comparison','engine_scorecard_real_data','engine_selection_authorized')) else 'BLOCKED',
        'ASSETS_AND_LEGAL': 'PASS' if passed('all_embedded_asset_licenses_checked') else 'BLOCKED',
        'OWNER_PUBLICATION_GO': 'PASS' if passed('owner_publication_go') else 'BLOCKED',
    }
    blockers = [name for name,v in gates.items() if v!='PASS']
    return {'schema':1,'project':'KINMOTO','pipeline':'DEV-PREVIEW-CANDIDATE-STABLE',
            'candidate':'A2A3A4_V057_LAB_REVIEW', 'gates':gates,
            'release_decision':'GO' if not blockers else 'NO_GO',
            'blockers':blockers,
            'notes':'Do not convert source QA, software WebGL, simulated routes or emulated phones into device proof.'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence',type=Path,default=DEFAULT_EVIDENCE)
    parser.add_argument('--report',type=Path,default=DEFAULT_REPORT)
    parser.add_argument('--strict',action='store_true')
    args=parser.parse_args()
    e=json.loads(args.evidence.read_text(encoding='utf-8'))
    result=evaluate(e)
    args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'decision':result['release_decision'],'gates':result['gates'],'blockers':result['blockers']},ensure_ascii=False))
    return 2 if args.strict and result['release_decision']=='NO_GO' else 0


if __name__=='__main__':
    raise SystemExit(main())
