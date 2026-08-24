from __future__ import annotations
import argparse,sys
from pathlib import Path
from .core import KnowledgeError,root_from,load,validate,select,render

def main(argv=None):
    p=argparse.ArgumentParser(prog='prototype-knowledge'); sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('validate')
    for name in ('query','compile'):
        q=sub.add_parser(name); q.add_argument('--file',required=True); q.add_argument('--format',choices=['json','yaml','markdown','dx'],default='json'); q.add_argument('--out')
    a=p.parse_args(argv)
    try:
        root=root_from()
        if a.cmd=='validate':
            errors=validate(root)
            if errors:
                for e in errors: print('ERROR:',e,file=sys.stderr)
                return 1
            print('PASS: knowledge repository validated')
            return 0
        query=load((root/a.file).resolve()); items=select(root,query); output=render(items,a.format)
        if a.out:
            target=(root/a.out).resolve(); target.parent.mkdir(parents=True,exist_ok=True); target.write_text(output,encoding='utf-8',newline='\n'); print(target)
        else: print(output,end='')
        return 0
    except KnowledgeError as e: print(f'ERROR: {e}',file=sys.stderr); return 1
