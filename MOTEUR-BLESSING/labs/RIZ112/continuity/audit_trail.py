#!/usr/bin/env python3
"""RIZ112 explicit audit trail for each available message/action/test.

Cannot access, scrape or record chats while not invoked. Records text made
available to this command, keeping exact bytes in context JSONL and Cahier mère.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
LAB=HERE.parent
sys.path.insert(0,str(LAB/'journal'))
from journal_tool import inspect as inspect_journal, append as append_journal
REG=LAB/'CONTEXTE_INTEGRAL'/'REGISTRE_MESSAGES.jsonl'
JOURNAL=LAB/'journal'/'JOURNAL_EVENEMENTS.jsonl'
MOTHER=LAB/'CAHIER_MERE.md'
VALID_ROLES={'USER','ASSISTANT'}

def text_sha(txt):return hashlib.sha256(txt.encode('utf-8')).hexdigest()
def context_rows():
 rows=[json.loads(s) for s in REG.read_text(encoding='utf-8').splitlines() if s.strip()]
 for i,r in enumerate(rows,1):
  if r.get('event_ref')!=f'CTX-{i:04d}':raise ValueError('Context order not contiguous at '+str(i))
 return rows

def check():
 contexts=context_rows();journals=inspect_journal(JOURNAL)
 if not MOTHER.exists() or not MOTHER.read_text(encoding='utf-8').startswith('# CAHIER MÈRE'):
  raise ValueError('Mother notebook not accessible')
 for row in contexts:
  if row.get('origin')=='USER' and row.get('full_raw_message_available') and not row.get('content'):
   raise ValueError('Malformed full user context')
  # Enforce traceability for all messages captured via this tool, including
  # Unicode-exact text, journal citation and mother-notebook inclusion.
  if 'journal_event_id' in row:
   cid=row['event_ref'];eid=row['journal_event_id'];raw=row['content']
   if text_sha(raw)!=row.get('utf8_sha256'):
    raise ValueError('Context SHA mismatch: '+cid)
   matches=[e for e in journals if e['id']==eid]
   if len(matches)!=1:
    raise ValueError('Missing journal event: '+cid)
   # E126/E127 (imported pre-1000 simulation) place the exact ID and
   # UTF-8 digest in evidence, whereas explicit capture() writes both in
   # summary. Accept EITHER verifiable location, not unlinked assertions.
   event=matches[0]
   proof_text=event['summary']+'\n'+event['evidence']
   if cid not in proof_text or row['utf8_sha256'] not in proof_text:
    raise ValueError('Missing journal evidence: '+cid)
   mother_text=MOTHER.read_text(encoding='utf-8')
   legacy_header=('Archive '+cid+' / '+eid) in mother_text
   capture_header=('Archive verbatim '+cid+' / '+eid) in mother_text
   if not (legacy_header or capture_header) or row['utf8_sha256'] not in mother_text or ('\n'+raw+'\n') not in mother_text:
    raise ValueError('Mother notebook capture missing: '+cid)
 return {'context_rows':len(contexts),'journal_events':len(journals),
         'journal_head':journals[-1]['digest'] if journals else 'GENESIS','journal_chain_valid':True}

def _fence(s):
 maxrun=max((len(t) for t in re.findall(r'`+',s)),default=0)
 return '`'*max(4,maxrun+1)

def capture(message_text,role,*,kind='USER_DIRECTIVE',date='2026-10-17',source_label='direct_user_message'):
 if role not in VALID_ROLES:raise ValueError('Invalid role')
 if role=='USER' and kind not in {'USER_DIRECTIVE','USER_FEEDBACK'}:raise ValueError('Invalid user event type')
 if role=='ASSISTANT' and kind not in {'ASSISTANT_ACTION','DESIGN_DECISION','HYPOTHESIS','TESTED','FAILED','CORRECTION','SYNC','CHECKPOINT','OPEN_QUESTION'}:raise ValueError('Invalid assistant event type')
 if not isinstance(message_text,str) or not message_text.strip():raise ValueError('Empty capture')
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):raise ValueError('Date must be YYYY-MM-DD')
 if not REG.exists() or not JOURNAL.exists() or not MOTHER.exists():raise ValueError('Source files missing')
 check()
 lock=HERE/'.capture.lock'
 try:
  fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 except FileExistsError as ex:raise ValueError('Concurrent capture requires reconciliation') from ex
 try:
  os.close(fd)
  rows=context_rows();events=inspect_journal(JOURNAL)
  cid=f'CTX-{len(rows)+1:04d}'
  eid=f'E{len(events)+1:03d}'
  sha=text_sha(message_text)
  row={'event_ref':cid,'origin':role,'date':date,'content':message_text,
       'provenance':('VERBATIM_USER_MESSAGE' if role=='USER' else 'VERBATIM_ASSISTANT_MESSAGE'),
       'full_raw_message_available':True,'note':source_label,'project':'RIZ112→MATRICE',
       'utf8_sha256':sha,'journal_event_id':eid}
  # The content register stores the full supplied message; journal stores the
  # reference and integrity digest rather than duplicating large message text.
  with REG.open('a',encoding='utf-8',newline='\n') as f:
   f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
  event={'id':eid,'date':date,'origin':role,'type':kind,
         'summary':f'Archive exacte message {cid}; rôle {role}; hash UTF-8 {sha}; voir registre intégral',
         'evidence':f'{source_label} | {cid} | sha256={sha}',
         'confidence':'VERBATIM_SUPPLIED_TO_CAPTURE','supersedes':None}
  append_journal(JOURNAL,event)
  fence=_fence(message_text)
  with MOTHER.open('a',encoding='utf-8',newline='\n') as f:
   f.write('\n\n### Archive verbatim '+cid+' / '+eid+' / '+date+'\n')
   f.write('**Rôle** '+role+' ; **SHA-256 UTF-8** `'+sha+'` ; **provenance** '+source_label+'\n\n')
   f.write(fence+'text\n'+message_text+'\n'+fence+'\n');f.flush();os.fsync(f.fileno())
  out=check();out.update(context_id=cid,journal_id=eid,utf8_sha256=sha)
  return out
 finally:
  try:lock.unlink()
  except FileNotFoundError:pass

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('command',choices=['verify','capture'])
 p.add_argument('--role',choices=sorted(VALID_ROLES))
 p.add_argument('--type',dest='kind',default='USER_DIRECTIVE')
 p.add_argument('--date',default='2026-10-17')
 p.add_argument('--message-file',type=Path)
 p.add_argument('--source-label',default='direct_user_message')
 args=p.parse_args(argv)
 if args.command=='verify':result=check()
 else:
  if args.role is None or args.message_file is None:p.error('capture requires --role and --message-file')
  result=capture(args.message_file.read_text(encoding='utf-8'),args.role,kind=args.kind,date=args.date,source_label=args.source_label)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
