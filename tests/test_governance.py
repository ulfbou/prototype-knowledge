import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"src"))
from prototype_knowledge.governance import validate_governance,cluster_view,knowledge_checkpoint,model

class GovernanceTests(unittest.TestCase):
    def test_governance_validates(self): self.assertEqual([],validate_governance(ROOT))
    def test_mold_driver_and_blocker_priority(self):
        view=cluster_view(ROOT,"moldfirstbloom")
        self.assertEqual("moldfirstbloom",view["cluster"]["driver"])
        self.assertEqual("work.collab.windows-dx-recovery",view["prioritized_work"][0]["id"])
    def test_dx_driver(self): self.assertEqual("dx-carrier-android",cluster_view(ROOT,"dx-carrier-android")["cluster"]["driver"])
    def test_checkpoint_no_change(self): self.assertEqual("NO_KNOWLEDGE_CHANGE",knowledge_checkpoint({})["outcome"])
    def test_checkpoint_knowledge(self): self.assertEqual("ADD_KNOWLEDGE_VERSION",knowledge_checkpoint({"cross_repo":True,"durable_rule":True})["outcome"])
    def test_decision_support_recovery_direction(self):
        items={x["id"]:x for x in model(ROOT)["work-index"]["items"]}
        diagnostics=items["work.collab.structured-diagnostics"]
        actions=items["work.collab.github-actions-failure-similarity"]
        self.assertEqual(("P2","proposed"),(diagnostics["priority"],diagnostics["status"]))
        self.assertEqual(("P3","candidate"),(actions["priority"],actions["status"]))
        self.assertIn("work.collab.structured-diagnostics",actions["depends_on"])
        self.assertTrue(diagnostics["acceptance_direction"])
        self.assertTrue(actions["revisit_triggers"])

    def test_checkpoint_deferral_requires_trace(self):
        with self.assertRaises(Exception): knowledge_checkpoint({"cross_repo":True,"must_defer":True})

if __name__=="__main__": unittest.main()