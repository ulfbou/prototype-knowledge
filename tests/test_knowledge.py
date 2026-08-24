import json,os,subprocess,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from prototype_knowledge.core import load,validate,select,render

class KnowledgeTests(unittest.TestCase):
    def test_repository_validates(self): self.assertEqual([],validate(ROOT))
    def test_dx_query_is_readonly_and_lf(self):
        q=load(ROOT/'queries/dx-recovery.yaml'); out=render(select(ROOT,q),'dx')
        self.assertTrue(out.startswith('%%DX v1.3.1\n')); self.assertIn('readonly="true"',out); self.assertNotIn('\r',out)
    def test_query_returns_dx_contract(self):
        ids={x['id'] for _,x in select(ROOT,load(ROOT/'queries/dx-recovery.yaml'))}
        self.assertIn('contract.dx.canonical-carrier',ids)
    def test_event_paths_are_dated(self):
        for p in (ROOT/'events').rglob('*.yaml'):
            self.assertRegex(p.relative_to(ROOT).as_posix(),r'^events/\d{4}/\d{2}/event\..+\.yaml$')

if __name__=='__main__': unittest.main()
