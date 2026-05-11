from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any

# Load model lazily
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def compute_similarity(text1: str, text2: str) -> float:
    """Computes cosine similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    model = get_model()
    emb1 = model.encode(text1)
    emb2 = model.encode(text2)
    cos_sim = util.cos_sim(emb1, emb2)
    return float(cos_sim[0][0])

def match_skills(jd_skills: List[str], candidate_skills: List[str]) -> Dict[str, Any]:
    """Matches JD skills with Candidate skills using semantic similarity."""
    if not jd_skills or not candidate_skills:
        return {"match_percentage": 0.0, "matched": [], "missing": jd_skills}
    
    model = get_model()
    jd_embs = model.encode(jd_skills)
    cand_embs = model.encode(candidate_skills)
    
    cos_scores = util.cos_sim(jd_embs, cand_embs)
    
    matched = []
    missing = []
    threshold = 0.65  # Semantic match threshold
    
    for i, jd_skill in enumerate(jd_skills):
        best_score = max(cos_scores[i]).item()
        if best_score >= threshold:
            # Find which candidate skill matched best
            best_idx = cos_scores[i].argmax().item()
            matched.append({
                "jd_skill": jd_skill,
                "candidate_skill": candidate_skills[best_idx],
                "score": best_score
            })
        else:
            missing.append(jd_skill)
            
    match_percentage = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0.0
    
    return {
        "match_percentage": match_percentage,
        "matched": matched,
        "missing": missing
    }
