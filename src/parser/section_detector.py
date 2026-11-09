import re
from typing import Any, Dict, List, Tuple

SECTION_PATTERNS = {
    "education": [
        r"^={2,}\s*education\s*={0,}",
        r"^education(?:\s+and\s+qualifications)?(?:\s*:)?$",
        r"^academic\s+(?:background|history|qualifications)(?:\s*:)?$",
        r"^studies(?:\s*:)?$",
    ],
    "experience": [
        r"^={2,}\s*experience(?:\s*/\s*internships)?\s*={0,}",
        r"^(?:work|professional)\s+experience(?:\s*:)?$",
        r"^internships?(?:\s*:)?$",
        r"^employment\s+history(?:\s*:)?$",
        r"^experience(?:\s*:)?$",
        r"^work(?:\s*:)?$",
    ],
    "projects": [
        r"^={2,}\s*projects\s*={0,}",
        r"^(?:key\s+|academic\s+|personal\s+)?projects(?:\s*:)?$",
        r"^project\s+work(?:\s*:)?$",
    ],
    "skills": [
        r"^={2,}\s*technical\s+skills\s*={0,}",
        r"^(?:technical\s+)?skills(?:\s+and\s+competencies|\s+and\s+expertise|\s*:)?$",
        r"^core\s+competencies(?:\s*:)?$",
        r"^my\s+skills(?:\s*:)?$",
    ],
    "certifications": [
        r"^={2,}\s*certifications(?:\s*&\s*courses)?\s*={0,}",
        r"^certifications?(?:\s+and\s+licenses)?(?:\s*:)?$",
        r"^licenses\s+and\s+certifications(?:\s*:)?$",
        r"^courses(?:\s*:)?$",
    ],
    "achievements": [
        r"^={2,}\s*achievements(?:\s*&\s*certifications)?\s*={0,}",
        r"^(?:honors|awards|achievements)(?:\s+and\s+honors|\s+and\s+awards)?(?:\s*:)?$",
        r"^extracurricular\s+activities(?:\s*:)?$",
        r"^leadership(?:\s+and\s+activities)?(?:\s*:)?$",
    ],
    "summary": [
        r"^={2,}\s*(?:professional\s+)?summary\s*={0,}",
        r"^(?:career\s+)?objective(?:\s*:)?$",
        r"^professional\s+summary(?:\s*:)?$",
        r"^about\s+me(?:\s*:)?$",
        r"^summary(?:\s*:)?$",
    ],
}


def _match_header(line: str) -> Tuple[bool, str]:
    """Test if a line is a known resume section header."""
    clean = line.strip().lower()
    clean_no_decor = re.sub(r"^[\-=#_*~]+\s*", "", clean)
    clean_no_decor = re.sub(r"\s*[\-=#_*~]+$", "", clean_no_decor).strip()

    for sec_name, patterns in SECTION_PATTERNS.items():
        for pat in patterns:
            if re.match(pat, clean, re.IGNORECASE) or re.match(pat, clean_no_decor, re.IGNORECASE):
                return True, sec_name
    return False, ""


def detect_sections(text: str) -> Dict[str, str]:
    """
    Segment raw resume text into standardized section blocks.
    Returns a dict mapping section keys to section text bodies.
    """
    sections: Dict[str, str] = {
        "header": "",
        "summary": "",
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": "",
        "achievements": "",
        "other": "",
    }

    if not text:
        return sections

    lines = text.split("\n")
    current_sec = "header"
    buffer: List[str] = []

    for line in lines:
        is_header, sec_name = _match_header(line)
        if is_header:
            # Save accumulated lines to previous section
            if buffer:
                content = "\n".join(buffer).strip()
                if sections[current_sec]:
                    sections[current_sec] += "\n" + content
                else:
                    sections[current_sec] = content
                buffer = []
            current_sec = sec_name
        else:
            buffer.append(line)

    # Flush final section
    if buffer:
        content = "\n".join(buffer).strip()
        if sections[current_sec]:
            sections[current_sec] += "\n" + content
        else:
            sections[current_sec] = content

    return sections


def compute_section_hygiene(text: str, sections: Dict[str, str]) -> Dict[str, Any]:
    """
    Calculate ATS formatting hygiene metrics:
    - Bullet points count
    - Quantifiable metrics (numbers, %, ms, users, dollars/rupees)
    - Section completeness score
    - Word count & length analysis
    """
    total_words = len(re.findall(r"\b\w+\b", text)) if text else 0

    # Count bullet markers (*, -, •, numbered)
    bullet_pattern = r"(?:^|\n)\s*(?:[\*\-•▪►]|\d+\.)\s+"
    bullets = re.findall(bullet_pattern, text)
    bullet_count = len(bullets)

    # Count quantifiable metrics (e.g. 15%, 45ms, 12,000+, 8.85 CGPA, $50k)
    metric_pattern = r"\b(?:\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s*(?:ms|s|sec|min|k|m|users|requests|req/s|stars|cgpa|gpa)|[+\$₹]\d+|\d+,\d+|\d+\+)\b"
    metrics = re.findall(metric_pattern, text, re.IGNORECASE)
    metrics_count = len(metrics)

    # Required core sections for engineering students
    core_sections = ["education", "skills", "projects", "experience"]
    present_core = [sec for sec in core_sections if len(sections.get(sec, "").strip()) > 30]
    missing_core = [sec for sec in core_sections if sec not in present_core]

    # Calculate hygiene score (0 to 100)
    score = 0.0

    # 1. Structure completeness (up to 40 pts)
    score += (len(present_core) / len(core_sections)) * 40.0

    # 2. Bullet point usage (up to 20 pts)
    if bullet_count >= 10:
        score += 20.0
    elif bullet_count >= 5:
        score += 12.0
    elif bullet_count >= 1:
        score += 6.0

    # 3. Quantifiable metrics presence (up to 25 pts)
    if metrics_count >= 6:
        score += 25.0
    elif metrics_count >= 3:
        score += 18.0
    elif metrics_count >= 1:
        score += 10.0

    # 4. Resume word count hygiene (up to 15 pts)
    # Typical fresher 1-page resume: 350-750 words
    if 350 <= total_words <= 800:
        score += 15.0
    elif 250 <= total_words < 350 or 800 < total_words <= 1100:
        score += 10.0
    elif total_words > 100:
        score += 5.0

    return {
        "total_words": total_words,
        "bullet_count": bullet_count,
        "metrics_count": metrics_count,
        "metrics_examples": metrics[:8],
        "present_sections": [k for k, v in sections.items() if len(v.strip()) > 20],
        "missing_core_sections": missing_core,
        "hygiene_score": round(min(100.0, max(0.0, score)), 1),
    }
