"""Candidate Knowledge Graph builder."""

from typing import Any


def build_knowledge_graph(parsed_resume: dict) -> dict:
    nodes = []
    edges = []

    candidate_name = parsed_resume.get("name", "Candidate")
    root_id = "candidate_root"
    nodes.append({"id": root_id, "type": "candidate", "label": candidate_name})

    for i, skill in enumerate(parsed_resume.get("skills", [])[:20]):
        name = skill.get("name", skill) if isinstance(skill, dict) else str(skill)
        node_id = f"skill_{i}"
        nodes.append({"id": node_id, "type": "skill", "label": name})
        edges.append({"source": root_id, "target": node_id, "relation": "has_skill"})

    for i, exp in enumerate(parsed_resume.get("experience", [])):
        node_id = f"exp_{i}"
        label = f"{exp.get('title', 'Role')} @ {exp.get('company', 'Company')}"
        nodes.append({"id": node_id, "type": "experience", "label": label, "properties": {
            "start": exp.get("start_date"), "end": exp.get("end_date"),
        }})
        edges.append({"source": root_id, "target": node_id, "relation": "worked_at"})
        for j, tech in enumerate(exp.get("technologies", [])[:5]):
            tech_id = f"exp_{i}_tech_{j}"
            nodes.append({"id": tech_id, "type": "technology", "label": tech})
            edges.append({"source": node_id, "target": tech_id, "relation": "used"})

    for i, edu in enumerate(parsed_resume.get("education", [])):
        node_id = f"edu_{i}"
        label = f"{edu.get('degree', '')} - {edu.get('institution', '')}"
        nodes.append({"id": node_id, "type": "education", "label": label.strip(" -")})
        edges.append({"source": root_id, "target": node_id, "relation": "educated_at"})

    for i, cert in enumerate(parsed_resume.get("certifications", [])):
        name = cert.get("name", cert) if isinstance(cert, dict) else str(cert)
        node_id = f"cert_{i}"
        nodes.append({"id": node_id, "type": "certification", "label": name})
        edges.append({"source": root_id, "target": node_id, "relation": "certified_in"})

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def flatten_for_storage(graph: dict) -> list[dict]:
    return [
        {"node_type": n["type"], "label": n["label"], "properties": n.get("properties", {})}
        for n in graph.get("nodes", [])
        if n["type"] != "candidate"
    ]
