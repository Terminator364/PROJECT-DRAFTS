from datetime import datetime,timezone
import copy, json
from pathlib import Path
from logic_engine import FIELDS
ROOT=Path(__file__).resolve().parent
T0='2026-10-24T18:00:00+00:00'
CUT='2026-10-23T16:00:00+00:00'
ISS='2026-10-22T17:00:00+00:00'
SEEN='2026-10-22T17:15:00+00:00'

def fact(state):return {'state':state,'source_id':'SYNTHETIC_LOGIC_DEMO_NOT_REAL_SOURCE','source_issued_utc':ISS,'source_first_seen_utc':SEEN,'assessment_status':'DOCUMENTED_SYNTHETIC'}

def make(name,states):
    base={'fixture_id':'DEMO_'+name,'analysis_asof_utc':CUT,'kickoff_utc':T0,'facts':{}}
    for side,alias,state in states:
        base['facts'][side+'.'+FIELDS[alias][0]]=fact(state)
    return base
open_match=make('OPEN_PRESSING_COUNTER',[
  ('A','PRESS','HIGH'),('B','BALL_SECURITY','LOW'),
  ('A','HIGH_BLOCK','HIGH'),('A','REST_DEFENSE','LOW'),('B','COUNTER_SPEED','HIGH'),
  ('A','SHOT_VOLUME','HIGH'),('A','SHOT_QUALITY','HIGH'),('B','SHOT_DENIAL','LOW'),
  ('B','GK_SAVE','LOW'),('A','FINISHING','HIGH'),('A','ATTACK_OPPOSITION','HIGH'),
  ('A','SETPIECE_ATTACK','LOW'),('B','SETPIECE_DEFENSE','HIGH'),
  ('A','TRAIL_RESPONSE','MEDIUM'),('B','TRAIL_RESPONSE','HIGH'),
  ('B','PRESS','MEDIUM'),('A','BALL_SECURITY','HIGH'),
  ('B','HIGH_BLOCK','MEDIUM'),('B','REST_DEFENSE','HIGH'),('A','COUNTER_SPEED','LOW'),
  ('B','SHOT_VOLUME','MEDIUM'),('B','SHOT_QUALITY','MEDIUM'),('A','SHOT_DENIAL','HIGH'),
  ('A','GK_SAVE','HIGH'),('B','FINISHING','MEDIUM'),('B','ATTACK_OPPOSITION','MEDIUM'),
  ('B','SETPIECE_ATTACK','MEDIUM'),('A','SETPIECE_DEFENSE','HIGH')])
closed=make('COMPACT_DEFENSE',[
  ('A','PRESS','LOW'),('B','PRESS','LOW'),
  ('A','BALL_SECURITY','HIGH'),('B','BALL_SECURITY','HIGH'),
  ('A','COUNTER_SPEED','LOW'),('B','COUNTER_SPEED','LOW'),
  ('A','HIGH_BLOCK','LOW'),('B','HIGH_BLOCK','LOW'),
  ('A','REST_DEFENSE','HIGH'),('B','REST_DEFENSE','HIGH'),
  ('A','SHOT_VOLUME','LOW'),('B','SHOT_VOLUME','LOW'),
  ('A','SHOT_QUALITY','LOW'),('B','SHOT_QUALITY','LOW'),
  ('A','SHOT_DENIAL','HIGH'),('B','SHOT_DENIAL','HIGH'),
  ('A','SETPIECE_ATTACK','LOW'),('B','SETPIECE_ATTACK','LOW'),
  ('A','SETPIECE_DEFENSE','HIGH'),('B','SETPIECE_DEFENSE','HIGH'),
  ('A','GK_SAVE','HIGH'),('B','GK_SAVE','HIGH'),
  ('A','FINISHING','LOW'),('B','FINISHING','LOW'),
  ('A','TRAIL_RESPONSE','LOW'),('B','TRAIL_RESPONSE','LOW'),
  ('A','ATTACK_OPPOSITION','LOW'),('B','ATTACK_OPPOSITION','LOW')])
ambiguous=make('INSUFFICIENT_DATA',[
    ('A','PRESS','HIGH'),('B','BALL_SECURITY','UNKNOWN'),('B','COUNTER_SPEED','HIGH'),
    ('A','HIGH_BLOCK','HIGH'),('A','REST_DEFENSE','UNKNOWN')])
for name,case in [('open_pressing_counter.json',open_match),('compact_defense.json',closed),('insufficient_data.json',ambiguous)]:
    (ROOT/'examples'/name).write_text(json.dumps(case,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':print('Wrote 3 scenario examples')