"""Every supplied value has an auditable rule role and 3 alternate-state tests.

An input can have zero LOCAL effect: never fabricate a positive influence.
This audits active input parameters, not all 355 documentary children.
"""
from pathlib import Path
import csv, json, argparse
from logic_engine import STATES, analyze, compare

def run(case):
    baseline=analyze(case)
    rows=[]
    for key,val in case['facts'].items():
        prior=val['state']
        comparisons=[compare(case,key,alternative) for alternative in ('LOW','MEDIUM','HIGH','UNKNOWN') if alternative!=prior]
        assert len(comparisons)==3
        for alt in comparisons:
            rows.append({'fixture_id':case['fixture_id'],'child':key,'original_state':prior,
                        'alternative_state':alt['new_state'],
                        'original_issue':alt['old_issue'],'counterfactual_issue':alt['new_issue'],
                        'rule_status_changes':len(alt['changed_rule_statuses']),
                        'changed_rules':';'.join(z['team']+':'+z['rule_id'] for z in alt['changed_rule_statuses']),
                        'interpretation':'CONDITIONAL_LOGICAL_TEST_NO_NUMERIC_IC'})
    count_changed=sum(v['rule_status_changes']>0 for v in rows)
    unique_changed=len({v['child'] for v in rows if v['rule_status_changes']>0})
    return baseline,rows,{'fixture_id':case['fixture_id'],'supplied_values':len(case['facts']),
        'fact_roles_covered':len(baseline['input_roles']),
        'tested_alternative_configurations':len(rows),
        'alternatives_modifying_some_rule':count_changed,
        'input_values_with_at_least_one_local_status_change':unique_changed,
        'inputs_with_no_status_change_in_any_3_alternatives':len(case['facts'])-unique_changed,
        'probabilistic_IC':None}

def cli():
    p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('--out',type=Path,required=True)
    arg=p.parse_args();base,rows,receipt=run(json.loads(arg.case.read_text()))
    arg.out.mkdir(parents=True,exist_ok=True)
    with (arg.out/'conditional_effects.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (arg.out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':cli()