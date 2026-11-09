import pytest
from src.feedback.resume_optimizer import (
    audit_action_verbs,
    audit_ats_hygiene,
    star_rewrite_suggestion,
    generate_bullet_improvements,
)


def test_audit_action_verbs():
    sample = "Worked on backend service and helped professor. Later architected and optimized a caching layer."
    audit = audit_action_verbs(sample)
    assert "worked on" in audit["weak_verbs_found"]
    assert "helped" in audit["weak_verbs_found"]
    assert "Architected" in audit["strong_verbs_found"]
    assert "Optimized" in audit["strong_verbs_found"]


def test_star_bullet_suggestion():
    weak_bullet = "Worked on website in summer using HTML and CSS."
    strong_bullet = "Architected a microservices backend serving 15,000 req/s with 40% latency reduction."

    res_weak = star_rewrite_suggestion(weak_bullet)
    res_strong = star_rewrite_suggestion(strong_bullet)

    assert res_strong["quality_score"] > res_weak["quality_score"]
    assert res_strong["has_metric"] is True
    assert res_strong["has_strong_action_verb"] is True
    assert res_weak["has_metric"] is False


def test_audit_ats_hygiene_checklist():
    text = (
        "Aarav | aarav@gmail.com | 9876543210 | github.com/aarav | linkedin.com/in/aarav\n"
        "Architected scalable microservices and optimized database queries.\n"
        + ("word " * 420)
    )
    sections = {"education": "B.Tech CSE at DTU", "skills": "Python, SQL, Docker", "projects": "Distributed System Project"}
    contacts = {"email": "aarav@gmail.com", "phone": "9876543210", "github": "github.com/aarav", "linkedin": "linkedin.com/in/aarav"}

    audit = audit_ats_hygiene(text, sections, contacts)
    assert audit["grade"] in ["A", "A+"]
