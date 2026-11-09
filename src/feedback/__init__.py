"""
Resume optimization, action verb auditing, and STAR bullet enhancer module.
"""

from .resume_optimizer import (
    audit_action_verbs,
    audit_ats_hygiene,
    star_rewrite_suggestion,
    generate_bullet_improvements,
)

__all__ = [
    "audit_action_verbs",
    "audit_ats_hygiene",
    "star_rewrite_suggestion",
    "generate_bullet_improvements",
]
