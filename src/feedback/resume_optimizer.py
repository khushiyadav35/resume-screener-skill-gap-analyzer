import re
from typing import Any, Dict, List, Optional, Tuple

WEAK_VERBS = {
    "helped", "worked on", "worked with", "responsible for", "handled",
    "assisted", "did", "made", "tried", "learned", "participated in",
    "was part of", "contributed to", "involved in", "looked after",
}

STRONG_ACTION_VERBS = {
    "Technical Architecture": [
        "Architected", "Engineered", "Constructed", "Implemented", "Designed",
        "Developed", "Formulated", "Synthesized", "Integrated",
    ],
    "Performance Optimization": [
        "Optimized", "Accelerated", "Refactored", "Streamlined", "Minimized",
        "Maximized", "Elevated", "Scaled", "Enhanced", "Surpassed",
    ],
    "DevOps & Automation": [
        "Automated", "Containerized", "Orchestrated", "Provisioned",
        "Configured", "Deployed", "Standardized", "Modernized",
    ],
    "Analytics & Research": [
        "Analyzed", "Benchmarked", "Quantified", "Audited", "Modeled",
        "Discovered", "Predicted", "Evaluated", "Validated",
    ],
    "Leadership & Delivery": [
        "Spearheaded", "Directed", "Pioneered", "Orchestrated", "Championed",
        "Mentored", "Delivered", "Coordinated",
    ],
}

ALL_STRONG_VERBS = {v.lower() for cat in STRONG_ACTION_VERBS.values() for v in cat}

STUDENT_STAR_EXAMPLES = [
    {
        "role": "Backend / SDE Intern",
        "weak": "Worked on backend APIs using FastAPI and helped optimize database queries.",
        "star": "Architected 8 asynchronous RESTful API endpoints using FastAPI and PostgreSQL, optimizing database indexing to reduce 95th percentile query latency by 35%.",
        "breakdown": "Action (Architected) + Tech Stack (FastAPI, PostgreSQL) + Metric (35% latency reduction).",
    },
    {
        "role": "Frontend Web Developer",
        "weak": "Made website pages in React and fixed some styling bugs with CSS.",
        "star": "Engineered responsive client-side component architecture using React and Tailwind CSS, increasing Google Lighthouse mobile performance score from 62 to 94.",
        "breakdown": "Action (Engineered) + Tech Stack (React, Tailwind CSS) + Metric (Lighthouse 62 -> 94).",
    },
    {
        "role": "Data Science / ML Intern",
        "weak": "Responsible for training machine learning models on customer churn data.",
        "star": "Trained and benchmarked 4 predictive classification models using Scikit-Learn and XGBoost on 100k+ customer records, achieving an 89.4% ROC-AUC score.",
        "breakdown": "Action (Trained & benchmarked) + Scope (100k+ records) + Metric (89.4% ROC-AUC).",
    },
    {
        "role": "Cloud & DevOps",
        "weak": "Helped team with Docker containers and deployment.",
        "star": "Containerized multi-service web backend using multi-stage Dockerfiles and automated CI/CD pipeline with GitHub Actions, cutting staging deployment cycle from 40 mins to 8 mins.",
        "breakdown": "Action (Containerized & automated) + Tools (Docker, GitHub Actions) + Metric (40m -> 8m).",
    },
]


def audit_action_verbs(text: str) -> Dict[str, Any]:
    """
    Scan resume text for weak passive phrases and identify strong impact verbs used.
    """
    if not text:
        return {"weak_verbs_found": [], "strong_verbs_found": [], "ratio": 0.0}

    text_lower = text.lower()
    weak_found: List[str] = []
    for verb in WEAK_VERBS:
        # Match as word phrase
        pattern = r"\b" + re.escape(verb) + r"\b"
        if re.search(pattern, text_lower):
            weak_found.append(verb)

    strong_found: List[str] = []
    for verb in ALL_STRONG_VERBS:
        pattern = r"\b" + re.escape(verb) + r"\b"
        if re.search(pattern, text_lower):
            strong_found.append(verb.title())

    total_verbs = len(weak_found) + len(strong_found)
    strong_ratio = round((len(strong_found) / max(1, total_verbs)) * 100.0, 1)

    return {
        "weak_verbs_found": sorted(weak_found),
        "strong_verbs_found": sorted(list(set(strong_found))),
        "weak_count": len(weak_found),
        "strong_count": len(strong_found),
        "strong_verb_percentage": strong_ratio,
        "recommendations": STRONG_ACTION_VERBS,
    }


def star_rewrite_suggestion(bullet_text: str) -> Dict[str, Any]:
    """
    Evaluate a specific resume bullet point against the STAR framework.
    """
    clean = bullet_text.strip().lstrip("*-•▪► 0123456789.")
    metric_pat = r"(?:\b\d+(?:\.\d+)?\s*(?:%|ms|s|sec|min|k|m|users|requests|req/s|stars|cgpa|gpa)\b|\d+%\b|\d+,\d+|\b\d+\+\b|[+\$₹]\d+)"
    has_metric = bool(re.search(metric_pat, clean, re.IGNORECASE))

    # Detect action verb at beginning
    first_word = clean.split()[0].lower() if clean.split() else ""
    is_strong_start = first_word in ALL_STRONG_VERBS
    is_weak_start = any(clean.lower().startswith(w) for w in WEAK_VERBS)

    quality_score = 30
    if is_strong_start:
        quality_score += 35
    elif not is_weak_start:
        quality_score += 15

    if has_metric:
        quality_score += 35

    feedback = []
    if is_weak_start:
        feedback.append(f"Replace weak passive starter ('{first_word}') with a decisive action verb (e.g. 'Architected', 'Engineered', 'Optimized').")
    elif not is_strong_start:
        feedback.append("Begin the bullet point with a strong past-tense engineering verb.")

    if not has_metric:
        feedback.append("Missing quantifiable impact metric! Add measurable results (e.g., latency reduction %, user scale, test coverage, efficiency gain).")

    return {
        "original": bullet_text,
        "quality_score": min(100, quality_score),
        "has_metric": has_metric,
        "has_strong_action_verb": is_strong_start,
        "is_weak_verb": is_weak_start,
        "improvement_feedback": feedback,
    }


def generate_bullet_improvements(text: str) -> List[Dict[str, Any]]:
    """
    Extract lines that look like bullet points and evaluate each one.
    """
    lines = text.split("\n")
    bullet_results = []
    bullet_pattern = r"^\s*(?:[\*\-•▪►]|\d+\.)\s+"

    for line in lines:
        if re.match(bullet_pattern, line) and len(line.strip()) > 20:
            analysis = star_rewrite_suggestion(line)
            bullet_results.append(analysis)

    return bullet_results


def audit_ats_hygiene(
    text: str,
    sections: Dict[str, str],
    contacts: Dict[str, Optional[str]],
) -> Dict[str, Any]:
    """
    Perform a complete checklist audit for student ATS resume readiness.
    """
    checklist = []
    issues_found = []

    # 1. Email check
    if contacts.get("email"):
        checklist.append({"item": "Professional Email Address", "status": "PASS", "detail": contacts["email"]})
    else:
        checklist.append({"item": "Professional Email Address", "status": "FAIL", "detail": "No valid email found in header."})
        issues_found.append("Add a professional email address (e.g., firstname.lastname@gmail.com).")

    # 2. Phone check
    if contacts.get("phone"):
        checklist.append({"item": "Contact Phone Number", "status": "PASS", "detail": contacts["phone"]})
    else:
        checklist.append({"item": "Contact Phone Number", "status": "FAIL", "detail": "Missing contact phone number."})
        issues_found.append("Add contact phone number with country code (+91 for India).")

    # 3. GitHub Profile check
    if contacts.get("github"):
        checklist.append({"item": "GitHub Profile Link", "status": "PASS", "detail": contacts["github"]})
    else:
        checklist.append({"item": "GitHub Profile Link", "status": "WARNING", "detail": "GitHub link missing. Critical for CS/IT engineering students!"})
        issues_found.append("Include an active GitHub profile link showing your code repositories.")

    # 4. LinkedIn Profile check
    if contacts.get("linkedin"):
        checklist.append({"item": "LinkedIn Profile Link", "status": "PASS", "detail": contacts["linkedin"]})
    else:
        checklist.append({"item": "LinkedIn Profile Link", "status": "WARNING", "detail": "LinkedIn profile link not found."})
        issues_found.append("Add your updated LinkedIn profile URL.")

    # 5. Core Sections Check
    required = ["education", "skills", "projects"]
    missing = [s for s in required if len(sections.get(s, "").strip()) < 12]
    if not missing:
        checklist.append({"item": "Essential Section Headers", "status": "PASS", "detail": "Education, Skills, and Projects sections present."})
    else:
        checklist.append({"item": "Essential Section Headers", "status": "FAIL", "detail": f"Missing critical sections: {', '.join(missing)}"})
        issues_found.append(f"Add standard ATS section headers for: {', '.join(missing)}.")

    # 6. Word count & length
    words = len(re.findall(r"\b\w+\b", text))
    if 350 <= words <= 850:
        checklist.append({"item": "Resume Length & Word Count", "status": "PASS", "detail": f"{words} words (Optimal for 1-page student resume)."})
    elif words < 350:
        checklist.append({"item": "Resume Length & Word Count", "status": "WARNING", "detail": f"{words} words (Too sparse. Expand on project details)."})
        issues_found.append("Resume is too brief. Expand on technical project implementations and tools used.")
    else:
        checklist.append({"item": "Resume Length & Word Count", "status": "WARNING", "detail": f"{words} words (May exceed 1 page. Consider condensing)."})
        issues_found.append("Resume exceeds recommended 1-page length for freshers. Condense descriptions.")

    # 7. Action verbs check
    verb_audit = audit_action_verbs(text)
    if verb_audit["weak_count"] > 0:
        checklist.append({"item": "Action Verb Quality", "status": "WARNING", "detail": f"Found {verb_audit['weak_count']} passive verbs ({', '.join(verb_audit['weak_verbs_found'][:4])})."})
        issues_found.append(f"Replace passive phrases like '{', '.join(verb_audit['weak_verbs_found'][:3])}' with impactful engineering action verbs.")
    else:
        checklist.append({"item": "Action Verb Quality", "status": "PASS", "detail": f"Strong verb usage ({verb_audit['strong_count']} active verbs)."})

    # Determine letter grade
    fails = sum(1 for c in checklist if c["status"] == "FAIL")
    warns = sum(1 for c in checklist if c["status"] == "WARNING")
    if fails == 0 and warns == 0:
        grade = "A+"
    elif fails == 0 and warns <= 2:
        grade = "A"
    elif fails <= 1:
        grade = "B"
    elif fails <= 2:
        grade = "C"
    else:
        grade = "D"

    return {
        "grade": grade,
        "checklist": checklist,
        "issues_found": issues_found,
        "star_examples": STUDENT_STAR_EXAMPLES,
        "action_verb_audit": verb_audit,
    }
