from __future__ import annotations
import json, hashlib
from pathlib import Path

class KnowledgeError(Exception): pass

def root_from(start: Path|None=None)->Path:
    p=(start or Path.cwd()).resolve()
    for c in (p,*p.parents):
        if (c/'registry/catalog.yaml').is_file(): return c
    raise KnowledgeError('repository root not found')

def load(path:Path)->dict:
    data=path.read_bytes()
    if b'\r' in data: raise KnowledgeError(f'CR byte found: {path}')
    if data.startswith(b'\xef\xbb\xbf'): raise KnowledgeError(f'BOM found: {path}')
    try: value=json.loads(data.decode('utf-8'))
    except Exception as e: raise KnowledgeError(f'invalid YAML 1.2 JSON profile: {path}: {e}') from e
    if not isinstance(value,dict) or value.get('schema_version')!='1.0': raise KnowledgeError(f'invalid document envelope: {path}')
    return value

def knowledge_files(root:Path): return sorted((root/'knowledge').rglob('*.yaml'))
def event_files(root:Path): return sorted((root/'events').rglob('*.yaml'))
def load_knowledge(root:Path): return [(p,load(p)) for p in knowledge_files(root)]
def hash_file(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(root:Path)->list[str]:
    errors=[]
    def check(cond,msg):
        if not cond: errors.append(msg)
    catalog=load(root/'registry/catalog.yaml')
    check(catalog['id']=='catalog.prototype-knowledge','catalog identity differs')
    repos=load(root/'registry/repositories.yaml'); repo_ids={x['id'] for x in repos['repositories']}
    check(len(repo_ids)==len(repos['repositories']),'duplicate repository ID')
    check(sum(bool(x['product_driver']) for x in repos['repositories'])==1,'exactly one product driver required')
    for x in repos['repositories']:
        for dep in x['consumes']: check(dep in repo_ids,f'unknown repository dependency: {dep}')
    topics={x['id'] for x in load(root/'registry/topics.yaml')['topics']}
    roles={x['id'] for x in load(root/'registry/roles.yaml')['roles']}
    phases={x['id'] for x in load(root/'registry/lifecycle.yaml')['phases']}
    authorities={x['id'] for x in load(root/'registry/authority.yaml')['classes']}
    seen=set(); versions={}
    for p,x in load_knowledge(root):
        key=(x['id'],x['version']); check(key not in seen,f'duplicate knowledge version: {key}'); seen.add(key)
        versions.setdefault(x['id'],[]).append(x)
        for r in x['scope'].get('repositories',[]): check(r in repo_ids,f'{p}: unknown repository {r}')
        for t in x['scope'].get('topics',[]): check(t in topics,f'{p}: unknown topic {t}')
        for r in x['scope'].get('roles',[]): check(r in roles,f'{p}: unknown role {r}')
        for ph in x['scope'].get('phases',[]): check(ph in phases,f'{p}: unknown phase {ph}')
        check(x['authority']['class'] in authorities,f'{p}: unknown authority')
    for kid,items in versions.items():
        active=[x for x in items if x['status']=='active']; check(len(active)<=1,f'multiple active versions: {kid}')
    ev_ids=set()
    for p in event_files(root):
        x=load(p); check(x['id'] not in ev_ids,f'duplicate event ID: {x["id"]}'); ev_ids.add(x['id'])
    for p in sorted((root/'queries').glob('*.yaml')):
        q=load(p)
        for t in q['select'].get('topics',[]): check(t in topics,f'{p}: unknown topic {t}')
        for r in q['select'].get('roles',[]): check(r in roles,f'{p}: unknown role {r}')
        for ph in q['select'].get('phases',[]): check(ph in phases,f'{p}: unknown phase {ph}')
    return errors

def select(root:Path,query:dict):
    selected=[]; s=query['select']; statuses=set(query['filters'].get('statuses',['active']))
    for p,x in load_knowledge(root):
        if x['status'] not in statuses: continue
        scope=x['scope']
        def overlap(field): return not s.get(field) or not scope.get(field) or bool(set(s[field]) & set(scope[field]))
        if all(overlap(f) for f in ('repositories','topics','roles','phases')): selected.append((p,x))
    selected.sort(key=lambda z:(z[1]['authority']['class'],z[1]['id'],z[1]['version']))
    return selected[:query['limits'].get('maximum_items',50)]

def render(items,fmt):
    model={'schema_version':'1.0','items':[x for _,x in items]}
    if fmt in ('json','yaml'): return json.dumps(model,indent=2,ensure_ascii=False,sort_keys=True)+'\n'
    if fmt=='markdown':
        out=['# Compiled Knowledge Context','']
        for _,x in items: out += [f"## {x['title']}",'',x['summary'],'',f"- ID: `{x['id']}@{x['version']}`",f"- Authority: `{x['authority']['class']}`",'']
        return '\n'.join(out)
    if fmt=='dx':
        data=json.dumps(model,indent=2,ensure_ascii=False,sort_keys=True)+'\n'; out=['%%DX v1.3.1\n','%%FILE path="knowledge-context.json" readonly="true"\n']
        out += ['    '+line for line in data.splitlines(keepends=True)]; out += ['%%ENDBLOCK\n','%%END\n']; return ''.join(out)
    raise KnowledgeError(f'unknown format: {fmt}')
