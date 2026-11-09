import re
from typing import Any, Dict, List, Optional, Set
from src.parser.extractor import extract_contact_info
from src.parser.section_detector import detect_sections, compute_section_hygiene
from .similarity import compute_tfidf_similarity
from .taxonomy import extract_skills


class ATSScorer:
    """Comprehensive ATS Resume Evaluation & Scoring Engine."""

    DEFAULT_WEIGHTS = {
        "hard_skills": 0.35,
        "semantic_similarity": 0.25,
        "projects_experience": 0.20,
        "education": 0.10,
        "formatting_hygiene": 0.10,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def evaluate(
        self,
        resume_text: str,
        jd_text: str,
        benchmark: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute full ATS scoring pipeline on resume against job description.
        """
        # 1. Parse contact details and sections
        contacts = extract_contact_info(resume_text)
        sections = detect_sections(resume_text)
        hygiene = compute_section_hygiene(resume_text, sections)

        # 2. Extract skills from both documents
        resume_skills_info = extract_skills(resume_text)
        resume_skills_set = set(resume_skills_info["skills"])

        # Determine target skills from benchmark or JD text
        if benchmark and benchmark.get("core_skills"):
            target_core = list(benchmark["core_skills"])
            target_bonus = list(benchmark.get("bonus_skills", []))
        else:
            jd_skills_info = extract_skills(jd_text)
            all_jd_skills = jd_skills_info["skills"]
            # Split roughly into core and bonus
            target_core = all_jd_skills[: max(5, int(len(all_jd_skills) * 0.7))]
            target_bonus = all_jd_skills[len(target_core) :]

        core_set = set(target_core)
        bonus_set = set(target_bonus)

        matched_core = [s for s in target_core if s in resume_skills_set]
        matched_bonus = [s for s in target_bonus if s in resume_skills_set]
        missing_core = [s for s in target_core if s not in resume_skills_set]
        missing_bonus = [s for s in target_bonus if s not in resume_skills_set]

        # 3. Component Scores (0 to 100)
        # A) Hard Skills Score (0 - 100)
        core_coverage = (len(matched_core) / len(core_set)) if core_set else 1.0
        bonus_coverage = (len(matched_bonus) / len(bonus_set)) if bonus_set else 0.5
        hard_skills_score = round(min(100.0, (core_coverage * 85.0) + (bonus_coverage * 15.0)), 1)

        # B) Semantic / TF-IDF Cosine Similarity (0 - 100)
        # In NLP document comparison between resumes and JDs, cosine similarity 0.22+ is exceptionally high.
        sim_result = compute_tfidf_similarity(resume_text, jd_text)
        raw_cos = sim_result["cosine_similarity"]
        # Linear normalization where 0.25 maps to 100%
        semantic_score = round(min(100.0, max(0.0, (raw_cos / 0.22) * 100.0)), 1)

        # C) Projects & Practical Experience Depth (0 - 100)
        # Freshers highlight 3-6 core skills in projects. Matching 3+ core skills in projects represents solid hands-on depth.
        proj_exp_text = (sections.get("projects", "") + " " + sections.get("experience", "")).strip()
        proj_skills = extract_skills(proj_exp_text)["skills"]
        proj_skills_set = set(proj_skills)
        matched_in_proj = [s for s in matched_core if s in proj_skills_set]

        # 4+ core skills in projects gives full 70 pts; variety of tools gives up to 30 pts
        core_proj_ratio = min(1.0, len(matched_in_proj) / 4.0) if core_set else 0.8
        variety_ratio = min(1.0, len(proj_skills) / 6.0)
        proj_score = round((core_proj_ratio * 70.0) + (variety_ratio * 30.0), 1)

        # D) Education Qualification Score (0 - 100)
        edu_text = (sections.get("education", "") + " " + resume_text[:500]).lower()
        edu_score = 40.0  # Base score
        degree_patterns = [
            r"\bb\.?tech\b",
            r"\bb\.?e\.?\b",
            r"\bm\.?tech\b",
            r"\bmca\b",
            r"\bbca\b",
            r"\bbachelor",
            r"\bcomputer science\b",
            r"\binformation technology\b",
        ]
        if any(re.search(pat, edu_text) for pat in degree_patterns):
            edu_score += 35.0
        # GPA / Marks check
        if re.search(r"\b(?:cgpa|gpa|percentage|%|\b\d\.\d{1,2}\s*/\s*10)\b", edu_text):
            edu_score += 15.0
        # Graduation year check (e.g. 2022, 2024, 2025, 2026)
        if re.search(r"\b20[12]\d\b", edu_text):
            edu_score += 10.0
        edu_score = min(100.0, edu_score)

        # E) ATS Formatting & Contact Hygiene Score (0 - 100)
        contact_pts = 0.0
        if contacts.get("email"):
            contact_pts += 25.0
        if contacts.get("phone"):
            contact_pts += 25.0
        if contacts.get("github") or contacts.get("portfolio"):
            contact_pts += 25.0
        if contacts.get("linkedin"):
            contact_pts += 25.0

        fmt_score = round(0.5 * contact_pts + 0.5 * hygiene["hygiene_score"], 1)

        # 4. Composite Overall ATS Score
        overall_score = (
            self.weights["hard_skills"] * hard_skills_score
            + self.weights["semantic_similarity"] * semantic_score
            + self.weights["projects_experience"] * proj_score
            + self.weights["education"] * edu_score
            + self.weights["formatting_hygiene"] * fmt_score
        )
        overall_score = round(min(100.0, max(0.0, overall_score)), 1)

        # 5. Determine Placement Readiness Tier
        if overall_score >= 80.0:
            tier = "Platinum"
            tier_badge = "🏆 Top 5% Placement Candidate"
            tier_desc = "Strong ATS profile. Highly competitive for product-based company screening."
            color = "#10B981"  # Emerald Green
        elif overall_score >= 65.0:
            tier = "Gold"
            tier_badge = "🥇 Competitive Candidate"
            tier_desc = "Solid candidate profile. High probability of clearing automated ATS filters."
            color = "#3B82F6"  # Blue
        elif overall_score >= 50.0:
            tier = "Silver"
            tier_badge = "🥈 Moderate Match"
            tier_desc = "Meets several requirements but has notable skill or formatting gaps that could trigger rejection."
            color = "#F59E0B"  # Amber
        else:
            tier = "Bronze"
            tier_badge = "🥉 High ATS Rejection Risk"
            tier_desc = "Low compatibility with target role. Significant gaps in core skills, metrics, and structure."
            color = "#EF4444"  # Red

        return {
            "overall_score": overall_score,
            "tier": tier,
            "tier_badge": tier_badge,
            "tier_description": tier_desc,
            "tier_color": color,
            "sub_scores": {
                "hard_skills": hard_skills_score,
                "semantic_similarity": semantic_score,
                "projects_experience": proj_score,
                "education": edu_score,
                "formatting_hygiene": fmt_score,
            },
            "weights": self.weights,
            "matched_skills": {
                "core": matched_core,
                "bonus": matched_bonus,
                "total_matched": len(matched_core) + len(matched_bonus),
            },
            "missing_skills": {
                "critical": missing_core,
                "secondary": missing_bonus,
                "total_missing": len(missing_core) + len(missing_bonus),
            },
            "contacts": contacts,
            "sections": sections,
            "hygiene": hygiene,
            "raw_similarity": sim_result,
        }


def calculate_ats_score(
    resume_text: str,
    jd_text: str,
    benchmark: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    scorer = ATSScorer(weights=weights)
    return scorer.evaluate(resume_text, jd_text, benchmark)
