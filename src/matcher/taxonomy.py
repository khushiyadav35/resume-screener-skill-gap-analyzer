import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple


class SkillTaxonomy:
    """Manages skill taxonomy, aliases, categories, and regex extraction."""

    def __init__(self, dictionary_path: Optional[str] = None):
        if dictionary_path is None:
            # Default to repo data/skill_dictionary.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dictionary_path = os.path.join(base_dir, "data", "skill_dictionary.json")

        self.dictionary_path = dictionary_path
        self.categories: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.all_canonical_skills: Set[str] = set()
        self.skill_to_category: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.dictionary_path):
            # Fallback inline taxonomy if file missing
            self._load_fallback()
            return

        with open(self.dictionary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.categories = data.get("categories", {})
        self.aliases = {k.lower(): v for k, v in data.get("aliases", {}).items()}

        for cat, skills in self.categories.items():
            for skill in skills:
                self.all_canonical_skills.add(skill)
                self.skill_to_category[skill.lower()] = cat

    def _load_fallback(self) -> None:
        self.categories = {
            "languages": ["Python", "Java", "C++", "C", "JavaScript", "TypeScript", "SQL", "Go"],
            "web_frameworks": ["React", "Node.js", "Express.js", "FastAPI", "Django", "Tailwind CSS"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "cloud_devops": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD", "Git"],
            "ml_ai": ["Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Pandas", "NumPy"],
            "core_cs": ["Data Structures & Algorithms", "System Design", "OOP", "DBMS", "Operating Systems"],
        }
        for cat, skills in self.categories.items():
            for skill in skills:
                self.all_canonical_skills.add(skill)
                self.skill_to_category[skill.lower()] = cat

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extract canonical skills from text with alias resolution and category mapping.
        """
        if not text:
            return {"skills": [], "by_category": {}, "count": 0}

        text_lower = text.lower()
        detected_canonical: Set[str] = set()

        # 1. Check for Aliases first (e.g. k8s, dsa, oop, reactjs)
        for alias, canonical in self.aliases.items():
            # Use word boundaries or punctuation boundaries
            pattern = r"(?:^|[\s,;:\(\)\[\]/|\*•])" + re.escape(alias) + r"(?:$|[\s,;:\(\)\[\]/|\*•])"
            if re.search(pattern, text_lower):
                detected_canonical.add(canonical)

        # 2. Check for Canonical Skills
        # Sort by length descending so multi-word skills ("Data Structures & Algorithms") match before ("Data Structures")
        sorted_skills = sorted(self.all_canonical_skills, key=lambda s: len(s), reverse=True)

        for skill in sorted_skills:
            if skill in detected_canonical:
                continue

            skill_clean = skill.lower()

            # Special case for very short names like "C", "R", "Go"
            if skill_clean in ["c", "r", "go"]:
                # Specific guarded regex to avoid common English word matches
                if skill_clean == "c":
                    pat = r"(?:\bC\s*[/,]\s*C\+\+|\bC\+\+\s*[/,]\s*C\b|\b[Pp]rogramming\s+in\s+C\b|\b[Ll]anguage\s*:\s*.*?\bC\b|\bC\s+programming\b)"
                    if re.search(pat, text):
                        detected_canonical.add("C")
                elif skill_clean == "r":
                    pat = r"(?:\bR\s+programming\b|\bprogramming\s+in\s+R\b|\bR\s+language\b|\bR\s*[,/]\s*Python\b|\bPython\s*[,/]\s*R\b)"
                    if re.search(pat, text):
                        detected_canonical.add("R")
                elif skill_clean == "go":
                    pat = r"(?:\bgolang\b|\b[Gg]o\s+programming\b|\b[Gg]o\s+language\b|\b[Gg]o\s*[,/]\s*Python\b|\bGo\s*[,/]\s*Java\b)"
                    if re.search(pat, text):
                        detected_canonical.add("Go")
                continue

            # Standard boundary matching for skills
            pat = r"(?:^|[\s,;:\(\)\[\]/|\*•])" + re.escape(skill_clean) + r"(?:$|[\s,;:\(\)\[\]/|\*•])"
            if re.search(pat, text_lower):
                detected_canonical.add(skill)

        # Categorize detected skills
        by_category: Dict[str, List[str]] = {}
        for skill in detected_canonical:
            cat = self.skill_to_category.get(skill.lower(), "other")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(skill)

        # Sort within each category
        for cat in by_category:
            by_category[cat].sort()

        sorted_skills_list = sorted(list(detected_canonical))
        return {
            "skills": sorted_skills_list,
            "by_category": by_category,
            "count": len(sorted_skills_list),
        }


# Global singleton cache for performance
_TAXONOMY_INSTANCE: Optional[SkillTaxonomy] = None


def load_taxonomy(path: Optional[str] = None) -> SkillTaxonomy:
    global _TAXONOMY_INSTANCE
    if _TAXONOMY_INSTANCE is None or path is not None:
        _TAXONOMY_INSTANCE = SkillTaxonomy(path)
    return _TAXONOMY_INSTANCE


def extract_skills(text: str) -> Dict[str, Any]:
    tax = load_taxonomy()
    return tax.extract_skills(text)
