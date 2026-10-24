#!/usr/bin/env python3
"""Create a visibly fictional trial from the authentic R8 graph, not fabricated IDs."""
from pathlib import Path
import argparse,json
from moteur_logique_v1 import original_graph

WANT={
 'HOME': ['TEAM_STRENGTH','WEATHER','ATTACK_BUILDUP','SHOT_QUALITY','SHOT_CONVERSION','SHOT_SUPPRESSION'],
 'AWAY': ['TEAM_STRENGTH','ATTACK_BUILDUP','SHOT_CREATION','SHOT_CONVERSION','DEFENCE_STRUCTURE']}
def fixture(graph,with_rates=False):
 original_graph(graph)
 available={}
 for n in graph['nodes']:
  available.setdefault(n['parent'],n['id'])
 rows={}
 for team,worlds in WANT.items():
  for world in worlds:
   rows[(team,available[world])]={'subparameter_id':available[world],'team':team,
                                   'state':'TRUE','evidence_kind':'SYNTHETIC_ASSUMPTION'}
 # Declare one actual R8 documentary cooccurrence as an observed lab pairing,
 # without calling the original relation a causal law.
 for edge in graph['edges']:
  world=edge.get('to_world')
  if world and world in available:
   src=edge['from'];dst=available[world];side='HOME'
   rows[(side,src)]={'subparameter_id':src,'team':side,'state':'TRUE',
                      'evidence_kind':'SYNTHETIC_ASSUMPTION'}
   rows[(side,dst)]={'subparameter_id':dst,'team':side,'state':'TRUE',
                      'evidence_kind':'SYNTHETIC_ASSUMPTION'}
   break
 ans={'schema':'MOTEUR_R8_LOGIQUE_V1_INPUT','fixture_id':'ESSAI_PUREMENT_HYPOTHETIQUE_R8',
      'mode':'LAB_SYNTHETIC','analysis_asof_utc':'2026-10-22T12:00:00Z',
      'kickoff_utc':'2026-10-23T19:00:00Z', 'observations':list(rows.values()),
      'note':'No real match, no real observation, no real probability calibration.'}
 if with_rates:
  ans['hypothetical_goal_rates']={'lambda_home':1.1,'lambda_away':0.9}
 return ans
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source-graph',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True);a.add_argument('--with-rates',action='store_true')
 args=a.parse_args();g=json.loads(args.source_graph.read_text(encoding='utf-8'))
 args.out.write_text(json.dumps(fixture(g,args.with_rates),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(args.out)