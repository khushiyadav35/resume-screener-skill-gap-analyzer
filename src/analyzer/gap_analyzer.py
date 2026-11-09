from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from src.matcher.taxonomy import load_taxonomy


@dataclass
class SkillGapReport:
    """Data container for detailed skill gap analysis."""
    matched_skills: List[str]
    missing_critical_skills: List[str]
    missing_secondary_skills: List[str]
    total_matched: int
    total_missing: int
    overall_gap_percentage: float
    category_breakdown: Dict[str, Dict[str, Any]]
    priority_skills_to_learn: List[str]


def analyze_skill_gap(
    resume_skills: List[str],
    target_core_skills: List[str],
    target_bonus_skills: Optional[List[str]] = None,
) -> SkillGapReport:
    """
    Perform deep skill gap analysis comparing candidate skills against job requirements.
    Categorizes skills by technical domain and prioritizes missing competencies.
    """
    tax = load_taxonomy()
    target_bonus_skills = target_bonus_skills or []

    resume_set: Set[str] = set(resume_skills)
    core_set: Set[str] = set(target_core_skills)
    bonus_set: Set[str] = set(target_bonus_skills)
    all_target_set: Set[str] = core_set.union(bonus_set)

    matched = sorted(list(resume_set.intersection(all_target_set)))
    missing_critical = sorted(list(core_set - resume_set))
    missing_secondary = sorted(list(bonus_set - resume_set))

    total_req = len(all_target_set)
    gap_pct = round((len(missing_critical) + 0.5 * len(missing_secondary)) / max(1, total_req) * 100.0, 1)

    # Category breakdown
    category_breakdown: Dict[str, Dict[str, Any]] = {}
    for cat, cat_skills in tax.categories.items():
        cat_skills_set = set(cat_skills)
        cat_target = cat_skills_set.intersection(all_target_set)
        if not cat_target:
            continue

        cat_matched = sorted(list(cat_target.intersection(resume_set)))
        cat_missing = sorted(list(cat_target - resume_set))
        coverage = round((len(cat_matched) / len(cat_target)) * 100.0, 1)

        category_breakdown[cat] = {
            "target_count": len(cat_target),
            "matched_count": len(cat_matched),
            "missing_count": len(cat_missing),
            "coverage_percentage": coverage,
            "matched_skills": cat_matched,
            "missing_skills": cat_missing,
        }

    # Priority ranking of skills to learn:
    # 1. Critical core skills first (languages and core_cs / databases / frameworks get high priority)
    # 2. Secondary bonus skills
    domain_weight = {
        "core_cs": 10,
        "languages": 9,
        "databases": 8,
        "web_frameworks": 8,
        "cloud_devops": 7,
        "ml_ai": 7,
        "tools": 5,
        "soft_skills": 4,
    }

    def _priority_score(skill: str, is_critical: bool) -> int:
        cat = tax.skill_to_category.get(skill.lower(), "other")
        base = domain_weight.get(cat, 5)
        return (base * 2 + 10) if is_critical else base

    ranked_skills = sorted(
        missing_critical + missing_secondary,
        key=lambda s: _priority_score(s, s in missing_critical),
        reverse=True,
    )

    return SkillGapReport(
        matched_skills=matched,
        missing_critical_skills=missing_critical,
        missing_secondary_skills=missing_secondary,
        total_matched=len(matched),
        total_missing=len(missing_critical) + len(missing_secondary),
        overall_gap_percentage=gap_pct,
        category_breakdown=category_breakdown,
        priority_skills_to_learn=ranked_skills,
    )
