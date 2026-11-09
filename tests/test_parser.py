import pytest
from src.parser.extractor import clean_text, extract_contact_info, extract_text
from src.parser.section_detector import detect_sections, compute_section_hygiene


def test_clean_text():
    raw = "Hello   world!\r\n\r\n\n\nThis is a test.\u00a0\u00a0"
    cleaned = clean_text(raw)
    assert "Hello world!" in cleaned
    assert "\r" not in cleaned
    assert "\u00a0" not in cleaned


def test_extract_contact_info():
    sample = """
    Aarav Sharma
    Email: aarav.sharma.tech@gmail.com | Phone: +91 98765 43210
    LinkedIn: https://linkedin.com/in/aarav-sharma-cs
    GitHub: https://github.com/aaravsharma
    Portfolio: https://aaravsharma.dev
    """
    contacts = extract_contact_info(sample)
    assert contacts["email"] == "aarav.sharma.tech@gmail.com"
    assert "98765" in contacts["phone"]
    assert contacts["linkedin"] == "https://linkedin.com/in/aarav-sharma-cs"
    assert contacts["github"] == "https://github.com/aaravsharma"
    assert contacts["name"] == "Aarav Sharma"


def test_detect_sections():
    sample = """
    Aarav Sharma
    aarav@gmail.com

    EDUCATION
    B.Tech Computer Science

    TECHNICAL SKILLS
    Python, SQL, Docker

    PROJECTS
    Built a URL shortener

    EXPERIENCE
    Software Intern at TechCorp
    """
    sections = detect_sections(sample)
    assert "B.Tech Computer Science" in sections["education"]
    assert "Python, SQL, Docker" in sections["skills"]
    assert "URL shortener" in sections["projects"]
    assert "Software Intern" in sections["experience"]


def test_compute_section_hygiene():
    sample = """
    EDUCATION
    B.Tech in CS at DTU | CGPA: 8.85 / 10.0

    TECHNICAL SKILLS
    Python, C++, Docker, Kubernetes

    PROJECTS
    * Engineered a task queue serving 25,000 req/s with 35% latency drop.
    * Containerized app using Docker with 92% test coverage.

    EXPERIENCE
    * Developed REST APIs for 10,000+ users.
    """
    sections = detect_sections(sample)
    hygiene = compute_section_hygiene(sample, sections)
    assert hygiene["bullet_count"] >= 3
    assert hygiene["metrics_count"] >= 2
    assert hygiene["hygiene_score"] >= 50.0
