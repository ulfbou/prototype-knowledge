#!/usr/bin/env python3
import subprocess,sys
base=sys.argv[1] if len(sys.argv)>1 else 'HEAD^'
p=subprocess.run(['git','diff','--name-status',base,'--','events'],text=True,stdout=subprocess.PIPE,check=True)
bad=[]
for line in p.stdout.splitlines():
    status=line.split('\t',1)[0]
    if status!='A': bad.append(line)
if bad:
    print('ERROR: accepted event files are append-only',file=sys.stderr)
    print('\n'.join(bad),file=sys.stderr); raise SystemExit(1)
print('PASS: event history is append-only')
