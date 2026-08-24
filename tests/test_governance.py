import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"src"))
from prototype_knowledge.governance import validate_governance,cluster_view,knowledge_checkpoint

class GovernanceTests(unittest.TestCase):
    def test_governance_validates(self): self.assertEqual([],validate_governance(ROOT))
    def test_mold_driver_and_blocker_priority(self):
        view=cluster_view(ROOT,"moldfirstbloom")
        self.assertEqual("moldfirstbloom",view["cluster"]["driver"])
        self.assertEqual("work.collab.windows-dx-recovery",view["prioritized_work"][0]["id"])
    def test_dx_driver(self): self.assertEqual("dx-carrier-android",cluster_view(ROOT,"dx-carrier-android")["cluster"]["driver"])
    def test_checkpoint_no_change(self): self.assertEqual("NO_KNOWLEDGE_CHANGE",knowledge_checkpoint({})["outcome"])
    def test_checkpoint_knowledge(self): self.assertEqual("ADD_KNOWLEDGE_VERSION",knowledge_checkpoint({"cross_repo":True,"durable_rule":True})["outcome"])
    def test_checkpoint_deferral_requires_trace(self):
        with self.assertRaises(Exception): knowledge_checkpoint({"cross_repo":True,"must_defer":True})

if __name__=="__main__": unittest.main()