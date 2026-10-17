#!/usr/bin/env python3
"""Append full available text of a conversation message to the durable context register.
Does not scrape chats or operate when the assistant is inactive.
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl'

def capture(role,text,provenance='VERBATIM_USER_MESSAGE',note='',date='2026-10-17'):
 if role not in ('USER','ASSISTANT'):raise ValueError('role invalid')
 if not isinstance(text,str) or not text.strip():raise ValueError('empty text')
 rows=[json.loads(x) for x in REG.read_text(encoding='utf8').splitlines() if x.strip()]
 ref=f'CTX-{len(rows)+1:04d}'
 row=dict(event_ref=ref,origin=role,date=date,content=text,provenance=provenance,
          full_raw_message_available=provenance.startswith('VERBATIM'),note=note,
          project='RIZ112→MATRICE')
 with REG.open('a',encoding='utf8',newline='\n') as f:
  f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
 return ref

def main():
 p=argparse.ArgumentParser();p.add_argument('--role',required=True,choices=['USER','ASSISTANT']);p.add_argument('--message-file',required=True,type=Path)
 p.add_argument('--provenance',default='VERBATIM_USER_MESSAGE');p.add_argument('--note',default='')
 a=p.parse_args();print(capture(a.role,a.message_file.read_text(encoding='utf8'),a.provenance,a.note))
if __name__=='__main__':main()
