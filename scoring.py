"""Rule-based scoring/ranking of job listings based on config/preferences.yaml
and config/resume.txt.

Ranking model:
  Jobs are ordered by an "ease of getting in" score: higher score = easier
  for this candidate to land, based on skill/resume overlap, security
  clearance mentions, degree-requirement fit, and how competitive the
  company typically is. Location is intentionally NOT part of the score.
"""
import os
import re
import time

import yaml

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
PREFS_PATH = os.path.join(CONFIG_DIR, "preferences.yaml")
RESUME_PATH = os.path.join(CONFIG_DIR, "resume.txt")

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z+#.]{1,}")
STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "are", "from", "this",
    "that", "have", "will", "has", "was", "were", "but", "not", "all",
    "can", "our", "their", "they", "them", "his", "her", "she", "him",
}


def load_preferences():
    with open(PREFS_PATH) as f:
        return yaml.safe_load(f) or {}


def load_resume_keywords():
    if not os.path.exists(RESUME_PATH):
        return set()
    with open(RESUME_PATH) as f:
        text = f.read()
    words = {w.lower() for w in WORD_RE.findall(text)}
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def _is_research(job):
    if job.get("listing_type") == "research":
        return True
    haystack = (job.get("category", "") + " " + job.get("title", "")).lower()
    return "research" in haystack


def score_job(job, prefs, resume_keywords):
    """Returns (score, breakdown dict) for a single job."""
    title_category = (job.get("title", "") + " " + job.get("category", "")).lower()
    breakdown = {}
    score = 0.0

    # 1. Skill/resume keyword matches -- direct fit with your background.
    skill_score = 0.0
    for kw, weight in (prefs.get("skill_keywords") or {}).items():
        if kw.lower() in title_category:
            skill_score += weight
    if skill_score:
        breakdown["skill_match"] = skill_score
        score += skill_score

    # 2. Security clearance mentions -- big advantage for this candidate.
    clearance_score = 0.0
    for kw, weight in (prefs.get("clearance_keywords") or {}).items():
        if kw.lower() in title_category:
            clearance_score += weight
    if clearance_score:
        breakdown["clearance_match"] = clearance_score
        score += clearance_score

    # 3. Degree requirement fit.
    degrees = job.get("degrees") or []
    acceptable = {d.lower() for d in (prefs.get("acceptable_degrees") or [])}
    if degrees and not any(d.lower() in acceptable for d in degrees):
        penalty = prefs.get("degree_mismatch_penalty", 0)
        if penalty:
            breakdown["degree_mismatch"] = penalty
            score += penalty

    # 4. Competitive company penalty.
    company = job.get("company", "").lower()
    for kw, weight in (prefs.get("competitive_companies") or {}).items():
        if kw.lower() in company:
            breakdown["competitive_company"] = weight
            score += weight
            break

    # 5. Resume keyword overlap.
    resume_weight = prefs.get("resume_match_weight", 0)
    if resume_keywords and resume_weight:
        title_words = {w.lower() for w in WORD_RE.findall(title_category)}
        overlap = title_words & resume_keywords
        if overlap:
            resume_score = len(overlap) * resume_weight
            breakdown["resume_overlap"] = resume_score
            breakdown["resume_overlap_terms"] = sorted(overlap)
            score += resume_score

    # 6. Recency decay.
    decay = prefs.get("recency_decay_per_day", 0)
    date_posted = job.get("date_posted")
    if decay and date_posted:
        days_old = max(0.0, (time.time() - date_posted) / 86400)
        penalty = days_old * decay
        if penalty:
            breakdown["recency_penalty"] = -penalty
            score -= penalty

    return score, breakdown


def compute_fit_tier(job, prefs):
    """Returns (tier, reason) -- an honest read on how competitive this
    posting realistically is for the candidate, separate from the ranking
    score. Tiers: 'Strong Fit', 'Target', 'Reach'.
    """
    title_category = (job.get("title", "") + " " + job.get("category", "")).lower()
    company = job.get("company", "").lower()

    strong_fit_kws = [k.lower() for k in (prefs.get("strong_fit_keywords") or [])]
    matched_strong = [k.strip() for k in strong_fit_kws if k in title_category]

    reach_companies = [c.lower() for c in (prefs.get("reach_companies") or [])]
    is_reach_company = any(c in company for c in reach_companies)

    # PhD/Master's-only requirement -> Reach (you're a CC student, no degree yet).
    degrees = job.get("degrees") or []
    acceptable = {d.lower() for d in (prefs.get("acceptable_degrees") or [])}
    grad_only = bool(degrees) and not any(d.lower() in acceptable for d in degrees)

    # The curated dataset's "degrees" field is often wrong/incomplete --
    # also check the title/category text itself for grad-level language.
    grad_text_match = any(
        kw in title_category for kw in ("phd", "ph.d", "master's", "masters", "doctoral", "graduate research")
    )

    if is_reach_company or grad_only or grad_text_match:
        reasons = []
        if is_reach_company:
            reasons.append("company hires mostly from top-tier PhD pipelines")
        if grad_only:
            reasons.append(f"listed degree requirement is {', '.join(degrees)} (you're community college / pre-bachelor's)")
        if grad_text_match:
            reasons.append("title/category mentions PhD/Master's/doctoral -- verify exact requirements on the company site, curated data can be wrong")
        return "Reach", "; ".join(reasons)

    if matched_strong:
        return "Strong Fit", f"Matches your differentiators: {', '.join(matched_strong)}"

    if _is_research(job):
        return "Target", "Research role, no major red flags, but you're early-career vs. typical applicants"

    return "Target", "Reasonable fit based on skills/background"


def rank_jobs(jobs, prefs=None, resume_keywords=None):
    if prefs is None:
        prefs = load_preferences()
    if resume_keywords is None:
        resume_keywords = load_resume_keywords()

    excluded = [c.lower() for c in (prefs.get("excluded_companies") or [])]
    include_categories = {c.lower() for c in (prefs.get("include_categories") or [])}

    results = []
    for job in jobs:
        company = job.get("company", "").lower()
        if any(ex in company for ex in excluded):
            continue
        if include_categories:
            if job.get("category", "").lower() not in include_categories:
                continue

        score, breakdown = score_job(job, prefs, resume_keywords)
        tier, tier_reason = compute_fit_tier(job, prefs)
        item = dict(job)
        item["score"] = round(score, 2)
        item["breakdown"] = breakdown
        item["fit_tier"] = tier
        item["fit_reason"] = tier_reason
        results.append(item)

    results.sort(key=lambda j: j["score"], reverse=True)
    return results
