from __future__ import annotations
from .core import load, KnowledgeError

def model(root):
    return {name: load(root / "registry" / f"{name}.yaml") for name in ("clusters", "priorities", "rule-strengths", "work-index")}

def validate_governance(root):
    m=model(root); errors=[]
    clusters={x["id"] for x in m["clusters"]["clusters"]}
    priorities={x["id"] for x in m["priorities"]["bands"]}
    items={x["id"] for x in m["work-index"]["items"]}
    if len(items)!=len(m["work-index"]["items"]): errors.append("duplicate work item ID")
    for x in m["work-index"]["items"]:
        if x["priority"] not in priorities: errors.append(f"unknown priority for {x['id']}")
        for c in x["clusters"]:
            if c not in clusters: errors.append(f"unknown cluster {c} for {x['id']}")
    strengths=m["rule-strengths"]["strengths"]
    if len({x["id"] for x in strengths})!=len(strengths): errors.append("duplicate rule strength")
    return errors

def cluster_view(root, cluster_id):
    m=model(root); cluster=next((x for x in m["clusters"]["clusters"] if x["id"]==cluster_id),None)
    if cluster is None: raise KnowledgeError(f"unknown cluster: {cluster_id}")
    rank={x["id"]:x["rank"] for x in m["priorities"]["bands"]}
    work=[x for x in m["work-index"]["items"] if cluster_id in x["clusters"] and x["status"] in ("active","planned")]
    work.sort(key=lambda x:(-rank[x["priority"]],x["id"]))
    return {"schema_version":"1.0","cluster":cluster,"prioritized_work":work}

def knowledge_checkpoint(values):
    valuable=any(values.get(k) for k in ("planning","repeat_failure","authority","cross_repo","compatibility","verification","retrieval","decision","procedure","invalidation"))
    if not valuable: return {"outcome":"NO_KNOWLEDGE_CHANGE","reason":"No durable knowledge-value trigger was selected."}
    if values.get("must_defer"):
        if not values.get("deferral_reason") or not values.get("revisit_trigger"): raise KnowledgeError("deferral requires reason and revisit trigger")
        return {"outcome":"DEFER_WITH_REASON","reason":values["deferral_reason"],"revisit_trigger":values["revisit_trigger"]}
    if values.get("invalidates_existing"): return {"outcome":"SUPERSEDE_KNOWLEDGE"}
    if values.get("registry_change"): return {"outcome":"UPDATE_MAINTAINED_REGISTRY"}
    if values.get("durable_rule"): return {"outcome":"ADD_KNOWLEDGE_VERSION"}
    return {"outcome":"ADD_EVENT"}
