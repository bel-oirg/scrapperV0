from __future__ import annotations

from .config import CandidateProfile
from .models import JobPosting
from .utils import build_fit_statement, is_known_tech_company, is_recent


ENTRY_LEVEL_TITLE_MARKERS = ("junior", "stagiaire", "alternance", "intern")


def score_job(job: JobPosting, profile: CandidateProfile) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    title = job.title.lower()
    location = (job.location or "").lower()

    if any(marker in title for marker in ENTRY_LEVEL_TITLE_MARKERS):
        score += 3
        reasons.append("entry-level title")

    if len(job.matching_skills) >= 3:
        score += 2
        reasons.append("3+ matching skills")

    if job.workplace in {"remote", "hybrid"}:
        score += 2
        reasons.append(f"{job.workplace} setup")

    if "casablanca" in location or "rabat" in location:
        score += 1
        reasons.append("preferred city")

    job.is_known_tech = job.is_known_tech or is_known_tech_company(job.company, profile)
    if job.is_known_tech:
        score += 1
        reasons.append("known tech company or startup")

    if is_recent(job.date_posted, 14):
        score += 1
        reasons.append("recent posting")

    if job.experience_years is not None and job.experience_years >= 5:
        score -= 3
        reasons.append("requires 5+ years")
    elif job.experience_years is not None and job.experience_years >= 3:
        score -= 2
        reasons.append("requires 3+ years")

    return max(0, min(10, score)), reasons


def annotate_job(job: JobPosting, profile: CandidateProfile) -> JobPosting:
    score, reasons = score_job(job, profile)
    job.relevance_score = score
    job.why_fit = build_fit_statement(
        company=job.company,
        matching_skills=job.matching_skills,
        workplace=job.workplace,
        languages=profile.languages,
    )
    if reasons and not job.why_fit:
        job.why_fit = ", ".join(reasons)
    return job
