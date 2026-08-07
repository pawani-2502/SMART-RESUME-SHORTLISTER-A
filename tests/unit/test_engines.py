import pytest
from ai.engines.scoring import compute_final_score
from ai.engines.scoring import compute_final_score
from ai.engines.confidence import compute_confidence, assess_human_review
from ai.engines.skill_graph import build_skill_graph, compute_skill_coverage
from ai.engines.skill_decay import compute_skill_freshness, decay_factor
from ai.engines.eligibility import check_eligibility
from ai.engines.credibility import detect_credibility_issues
from ai.engines.career_trajectory import analyze_career_trajectory
from ai.engines.recommendation import generate_recommendation
from ai.engines.jd_quality import analyze_jd_quality
from backend.services.dedup_service import compute_checksum, fuzzy_similarity, detect_duplicate


class TestScoringEngine:
    def test_final_score_range(self):
        scores = {
            "semantic_fit": 0.8, "skill_coverage": 0.7, "career_trajectory": 0.6,
            "must_have_coverage": 0.75, "reciprocal_fit": 0.7, "interview_readiness": 0.65,
            "verification_score": 0.5, "leadership_score": 0.6, "domain_experience": 0.7,
            "credibility_penalty": 0.05,
        }
        result = compute_final_score(scores)
        assert 0 <= result["final_score"] <= 1

    def test_confidence_levels(self):
        score, level = compute_confidence(8, 0.8, 0.7, 0.75, 0.9)
        assert level in ("High", "Medium", "Low")
        assert 0 <= score <= 1

    def test_human_review_borderline(self):
        review, reasons = assess_human_review(0.45, "Low", [], ["skill1", "skill2", "skill3"], 0.58)
        assert review is True
        assert len(reasons) > 0


class TestSkillGraph:
    def test_pytorch_inference(self):
        graph = build_skill_graph(["pytorch"])
        inferred = [s["name"].lower() for s in graph["inferred_skills"]]
        assert any("machine learning" in i or "deep learning" in i for i in inferred)

    def test_skill_coverage(self):
        coverage, matched, missing = compute_skill_coverage(
            ["python", "react", "fastapi"], ["python", "kubernetes"]
        )
        assert coverage > 0
        assert "python" in [m.lower() for m in matched]


class TestSkillDecay:
    def test_decay_recent_higher(self):
        assert decay_factor(2) > decay_factor(48)

    def test_freshness_computation(self):
        resume = {
            "skills": [{"name": "python"}],
            "experience": [{
                "technologies": ["python"],
                "end_date": "2024-06",
                "description": "Used python daily",
            }],
        }
        result = compute_skill_freshness(resume)
        assert result["avg_freshness"] > 0


class TestEligibility:
    def test_insufficient_experience(self):
        resume = {"skills": [{"name": "python"}], "experience": [], "education": []}
        job = {"experience_years_min": 5, "required_skills": []}
        override = {"min_years_experience": 5}
        eligible, reasons = check_eligibility(resume, job, override)
        assert eligible is False
        assert any("experience" in r.lower() for r in reasons)


class TestCredibility:
    def test_many_skills_few_years(self):
        resume = {
            "skills": [{"name": f"skill{i}"} for i in range(35)],
            "experience": [{"title": "Dev", "start_date": "2024-01", "end_date": "present"}],
        }
        result = detect_credibility_issues(resume)
        assert result["credibility_score"] < 1.0


class TestCareerTrajectory:
    def test_senior_progression(self):
        resume = {
            "experience": [
                {"title": "Junior Developer", "start_date": "2018", "end_date": "2020"},
                {"title": "Software Engineer", "start_date": "2020", "end_date": "2022"},
                {"title": "Senior Engineer", "start_date": "2022", "end_date": "present"},
            ]
        }
        metrics = analyze_career_trajectory(resume, "senior")
        assert metrics["career_trajectory_score"] > 0.5


class TestRecommendation:
    def test_strong_candidate(self):
        rec = generate_recommendation(0.85, "High", "eligible", False, [], 0.8, 0.02)
        assert rec["label"] == "Strong Interview"

    def test_ineligible(self):
        rec = generate_recommendation(0, "Low", "ineligible", False, [], 0, 0)
        assert rec["label"] == "Reject"


class TestJDQuality:
    def test_short_jd_penalized(self):
        result = analyze_jd_quality("Short job post.", {})
        assert result["overall_score"] < 0.8


class TestDedup:
    def test_exact_duplicate(self):
        text = "John Doe\nSoftware Engineer\nPython React"
        checksum = compute_checksum(text)
        dup = detect_duplicate(text, [{"candidate_id": "1", "checksum": checksum, "text": text}])
        assert dup is not None
        assert dup["type"] == "exact"

    def test_fuzzy_duplicate(self):
        a = "John Doe Software Engineer Python React AWS Docker"
        b = "John Doe Software Engineer Python React AWS Docker Kubernetes"
        assert fuzzy_similarity(a, b) > 0.9
