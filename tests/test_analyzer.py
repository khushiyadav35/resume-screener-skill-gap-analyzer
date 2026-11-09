import pytest
from src.analyzer.gap_analyzer import analyze_skill_gap
from src.analyzer.roadmap_generator import get_skill_learning_plan, generate_learning_roadmap


def test_analyze_skill_gap():
    resume_skills = ["Python", "SQL", "Git", "React"]
    core_req = ["Python", "SQL", "Docker", "PostgreSQL"]
    bonus_req = ["Kubernetes", "Redis"]

    report = analyze_skill_gap(resume_skills, core_req, bonus_req)

    assert "Python" in report.matched_skills
    assert "SQL" in report.matched_skills
    assert "Docker" in report.missing_critical_skills
    assert "PostgreSQL" in report.missing_critical_skills
    assert "Kubernetes" in report.missing_secondary_skills
    assert report.total_matched == 2
    assert report.total_missing == 4


def test_learning_roadmap_generation():
    plan_docker = get_skill_learning_plan("Docker")
    assert "Docker" in plan_docker["portfolio_project"]["bullet_point"]
    assert len(plan_docker["milestones"]) >= 3
    assert len(plan_docker["free_resources"]) >= 2

    # Test dynamic fallback for custom skill
    plan_custom = get_skill_learning_plan("Rust")
    assert "Rust" in plan_custom["summary"]

    roadmap = generate_learning_roadmap(["Docker", "PostgreSQL", "Redis"], max_skills=2)
    assert len(roadmap) == 2
    assert roadmap[0]["skill"] == "Docker"
    assert roadmap[1]["skill"] == "PostgreSQL"
