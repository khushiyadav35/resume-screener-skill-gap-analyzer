import pytest
from src.matcher.taxonomy import SkillTaxonomy, extract_skills
from src.matcher.similarity import compute_tfidf_similarity, compute_token_overlap
from src.matcher.ats_scorer import ATSScorer, calculate_ats_score


def test_taxonomy_alias_and_extraction():
    tax = SkillTaxonomy()
    text = "Proficient in k8s, reactjs, postgres, and dsa. Also experience with Python and Docker."
    extracted = tax.extract_skills(text)
    skills = extracted["skills"]

    assert "Kubernetes" in skills
    assert "React" in skills
    assert "PostgreSQL" in skills
    assert "Data Structures & Algorithms" in skills
    assert "Python" in skills
    assert "Docker" in skills


def test_similarity_computation():
    text1 = "Experienced software engineer skilled in Python, Django, REST APIs, and PostgreSQL database optimization."
    text2 = "Looking for a software engineer with Python, Django, REST APIs, and relational databases."
    text_irrelevant = "Chef experienced in baking bread, pastry design, and restaurant kitchen management."

    sim_high = compute_tfidf_similarity(text1, text2)
    sim_low = compute_tfidf_similarity(text1, text_irrelevant)

    assert sim_high["cosine_similarity"] > sim_low["cosine_similarity"]
    assert sim_high["token_overlap"] > 0.10


def test_ats_scorer_evaluation():
    resume = """
    Aarav Sharma | aarav@example.com | +91 9876543210 | https://github.com/aarav
    EDUCATION: B.Tech in Computer Science, 2026. CGPA: 8.8
    SKILLS: Python, SQL, Docker, PostgreSQL, Redis, REST APIs, Git, DSA
    EXPERIENCE: Intern at TechCorp. Built APIs serving 10,000+ users.
    PROJECTS: Distributed Task Queue using Python, Redis, and Docker with 92% coverage.
    """
    jd = """
    SDE-1 role. Requires strong Python, SQL, Docker, PostgreSQL, REST APIs, Git.
    Preferred: Redis, Kubernetes, CI/CD.
    """
    bench = {
        "core_skills": ["Python", "SQL", "Docker", "PostgreSQL", "REST APIs", "Git"],
        "bonus_skills": ["Redis", "Kubernetes", "CI/CD"],
    }

    result = calculate_ats_score(resume, jd, benchmark=bench)
    assert result["overall_score"] >= 65.0
    assert result["tier"] in ["Gold", "Platinum"]
    assert len(result["matched_skills"]["core"]) >= 5
    assert "Docker" in result["matched_skills"]["core"]
