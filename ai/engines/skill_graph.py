"""Latent Skill Graph - Skill ontology and inference engine."""

SKILL_ONTOLOGY: dict[str, list[str]] = {
    "pytorch": ["deep learning", "machine learning", "python", "neural networks"],
    "tensorflow": ["deep learning", "machine learning", "python", "neural networks"],
    "keras": ["deep learning", "tensorflow", "machine learning"],
    "scikit-learn": ["machine learning", "python", "data science"],
    "pandas": ["data analysis", "python", "data science"],
    "numpy": ["python", "data science", "scientific computing"],
    "react": ["javascript", "frontend development", "ui development", "spa"],
    "vue": ["javascript", "frontend development", "ui development"],
    "angular": ["typescript", "frontend development", "spa"],
    "next.js": ["react", "javascript", "frontend development", "ssr"],
    "node.js": ["javascript", "backend development", "rest apis", "microservices"],
    "express": ["node.js", "backend development", "rest apis"],
    "fastapi": ["python", "backend development", "rest apis", "api development"],
    "django": ["python", "backend development", "web development"],
    "flask": ["python", "backend development", "web development"],
    "spring": ["java", "backend development", "enterprise"],
    "docker": ["containerization", "devops", "deployment"],
    "kubernetes": ["container orchestration", "devops", "docker", "cloud native"],
    "aws": ["cloud computing", "infrastructure", "devops"],
    "azure": ["cloud computing", "infrastructure", "devops"],
    "gcp": ["cloud computing", "infrastructure", "devops"],
    "postgresql": ["sql", "databases", "relational databases"],
    "mongodb": ["nosql", "databases", "document databases"],
    "redis": ["caching", "databases", "in-memory storage"],
    "graphql": ["api development", "backend development"],
    "rest": ["api development", "backend development", "web services"],
    "microservices": ["distributed systems", "backend development", "architecture"],
    "ci/cd": ["devops", "automation", "deployment"],
    "terraform": ["infrastructure as code", "devops", "cloud computing"],
    "langchain": ["llm", "ai", "python", "nlp"],
    "langgraph": ["llm", "ai", "agents", "python"],
    "nlp": ["machine learning", "ai", "text processing"],
    "computer vision": ["deep learning", "machine learning", "ai"],
    "agile": ["project management", "scrum", "software development"],
    "scrum": ["agile", "project management"],
    "leadership": ["management", "team leadership", "mentorship"],
    "mentorship": ["leadership", "team development"],
}


def normalize_skill(skill: str) -> str:
    return skill.lower().strip().replace("_", " ").replace("-", " ")


def build_skill_graph(candidate_skills: list[str]) -> dict:
    normalized = {normalize_skill(s): s for s in candidate_skills}
    inferred: dict[str, dict] = {}
    explicit = set(normalized.keys())

    for skill in explicit:
        parents = SKILL_ONTOLOGY.get(skill, [])
        for parent in parents:
            parent_norm = normalize_skill(parent)
            if parent_norm not in explicit:
                if parent_norm not in inferred:
                    inferred[parent_norm] = {
                        "name": parent,
                        "inferred_from": [],
                        "confidence": 0.0,
                    }
                inferred[parent_norm]["inferred_from"].append(normalized.get(skill, skill))
                inferred[parent_norm]["confidence"] = min(
                    0.9, inferred[parent_norm]["confidence"] + 0.3
                )

    all_skills = explicit | set(inferred.keys())
    coverage_paths = []
    for skill in explicit:
        path = [skill]
        for parent in SKILL_ONTOLOGY.get(skill, []):
            path.append(normalize_skill(parent))
        coverage_paths.append(path)

    expansion_score = len(inferred) / max(len(explicit), 1)

    return {
        "explicit_skills": list(explicit),
        "inferred_skills": [
            {"name": v["name"], "inferred_from": v["inferred_from"], "confidence": round(v["confidence"], 2)}
            for v in inferred.values()
        ],
        "coverage_paths": coverage_paths,
        "skill_graph_coverage": round(len(all_skills) / max(len(explicit), 1), 2),
        "knowledge_expansion_score": round(min(expansion_score, 1.0), 2),
    }


def compute_skill_coverage(candidate_skills: list[str], required_skills: list[str]) -> tuple[float, list[str], list[str]]:
    graph = build_skill_graph(candidate_skills)
    all_candidate = set(graph["explicit_skills"])
    for inf in graph["inferred_skills"]:
        if inf["confidence"] >= 0.5:
            all_candidate.add(normalize_skill(inf["name"]))

    required_norm = [normalize_skill(s) for s in required_skills]
    matched = [s for s in required_norm if s in all_candidate or any(s in c or c in s for c in all_candidate)]
    missing = [s for s in required_skills if normalize_skill(s) not in matched]

    coverage = len(matched) / max(len(required_norm), 1)
    return round(coverage, 4), matched, missing
