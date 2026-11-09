import re
from typing import Dict, List, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _tokenize(text: str) -> List[str]:
    """Tokenize text preserving tech symbols like C++, C#, .NET, CI/CD."""
    if not text:
        return []
    # Replace slashes and hyphens inside words cautiously
    clean = text.lower()
    clean = re.sub(r"c\+\+", "cpp", clean)
    clean = re.sub(r"c\#", "csharp", clean)
    clean = re.sub(r"\.net", "dotnet", clean)
    clean = re.sub(r"ci/cd", "cicd", clean)
    tokens = re.findall(r"[a-z0-9_]{2,}", clean)
    return tokens


def compute_token_overlap(text1: str, text2: str) -> float:
    """Compute Jaccard similarity coefficient between two texts."""
    tokens1: Set[str] = set(_tokenize(text1))
    tokens2: Set[str] = set(_tokenize(text2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return float(intersection) / float(union) if union > 0 else 0.0


def compute_tfidf_similarity(resume_text: str, jd_text: str) -> Dict[str, float]:
    """
    Compute sublinear TF-IDF Cosine Similarity and bi-gram n-gram contextual match.
    Returns cosine similarity float (0.0 to 1.0) and percentage (0.0 to 100.0).
    """
    if not resume_text.strip() or not jd_text.strip():
        return {
            "cosine_similarity": 0.0,
            "similarity_percentage": 0.0,
            "token_overlap": 0.0,
        }

    try:
        vectorizer = TfidfVectorizer(
            sublinear_tf=True,
            ngram_range=(1, 2),
            stop_words="english",
            max_features=5000,
            token_pattern=r"(?u)\b[a-zA-Z0-9_+#.]{2,}\b",
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim_val = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
    except Exception:
        # Fallback to token overlap
        sim_val = compute_token_overlap(resume_text, jd_text)

    overlap = compute_token_overlap(resume_text, jd_text)

    # Blend cosine with token overlap to reward exact keyword presence
    blended_sim = 0.85 * sim_val + 0.15 * overlap
    blended_sim = max(0.0, min(1.0, blended_sim))

    return {
        "cosine_similarity": round(float(blended_sim), 4),
        "similarity_percentage": round(float(blended_sim * 100.0), 2),
        "token_overlap": round(float(overlap), 4),
    }
