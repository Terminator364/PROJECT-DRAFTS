#!/usr/bin/env python3
"""Safe MB1 runner: never mislabel a league baseline as full 62-world IC."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from rice_formula_integrity_gate import audit


def run(engine_root: Path, packet_path: Path, model_path: Path | None = None):
    root = engine_root.resolve()
    scripts = root/'code'
    catalogue_path = root/'config'/'RECETTES_62_EXECUTABLES.json'
    if not scripts.is_dir() or not catalogue_path.is_file():
        raise FileNotFoundError('Engine root needs code/ and config/RECETTES_62_EXECUTABLES.json')
    sys.path.insert(0, str(scripts))
    try:
        from moteur_v112 import calculate
        packet = json.loads(packet_path.read_text(encoding='utf-8'))
        model = json.loads(model_path.read_text(encoding='utf-8')) if model_path else None
        raw = calculate(packet, model)
        cat = json.loads(catalogue_path.read_text(encoding='utf-8'))
        return audit(packet, raw, cat)
    finally:
        sys.path.remove(str(scripts))


def main():
    p=argparse.ArgumentParser(description='MOTEUR: guarded research baseline, not a certified IC')
    p.add_argument('--engine-root',type=Path,required=True)
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--model',type=Path)
    p.add_argument('--output',type=Path)
    opts=p.parse_args()
    result=run(opts.engine_root,opts.packet,opts.model)
    blob=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if opts.output: opts.output.write_text(blob,encoding='utf-8')
    else: print(blob,end='')

if __name__=='__main__':main()
