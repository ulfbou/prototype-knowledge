from __future__ import annotations
import argparse,json,sys
from .core import KnowledgeError,root_from,load,validate,select,render
from .governance import validate_governance,cluster_view,knowledge_checkpoint

def main(argv=None):
    p=argparse.ArgumentParser(prog="prototype-knowledge"); sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("validate")
    for name in ("query","compile"):
        q=sub.add_parser(name);q.add_argument("--file",required=True);q.add_argument("--format",choices=["json","yaml","markdown","dx"],default="json");q.add_argument("--out")
    c=sub.add_parser("cluster");c.add_argument("--id",required=True)
    k=sub.add_parser("knowledge-checkpoint")
    for flag in ("planning","repeat-failure","authority","cross-repo","compatibility","verification","retrieval","decision","procedure","invalidation","invalidates-existing","registry-change","durable-rule","must-defer"):
        k.add_argument("--"+flag,action="store_true")
    k.add_argument("--deferral-reason");k.add_argument("--revisit-trigger")
    a=p.parse_args(argv)
    try:
        root=root_from()
        if a.cmd=="validate":
            errors=validate(root)+validate_governance(root)
            if errors:
                for e in errors: print("ERROR:",e,file=sys.stderr)
                return 1
            print("PASS: knowledge repository and governance validated");return 0
        if a.cmd=="cluster": print(json.dumps(cluster_view(root,a.id),indent=2,sort_keys=True));return 0
        if a.cmd=="knowledge-checkpoint":
            values={k.replace("_","-"):v for k,v in vars(a).items()}
            normalized={k.replace("-","_"):v for k,v in values.items()}
            print(json.dumps(knowledge_checkpoint(normalized),indent=2,sort_keys=True));return 0
        query=load((root/a.file).resolve());output=render(select(root,query),a.format)
        if a.out:
            target=(root/a.out).resolve();target.parent.mkdir(parents=True,exist_ok=True);target.write_text(output,encoding="utf-8",newline="\n");print(target)
        else: print(output,end="")
        return 0
    except KnowledgeError as e: print(f"ERROR: {e}",file=sys.stderr);return 1