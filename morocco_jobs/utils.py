from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from typing import Any
from urllib.parse import urlencode, urljoin

try:
    import dateparser
except ImportError:  # pragma: no cover - graceful fallback when deps are not installed yet.
    dateparser = None

from .config import CandidateProfile


WHITESPACE_RE = re.compile(r"\s+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+", re.IGNORECASE)
EXPERIENCE_RE = re.compile(
    r"(?P<years>\d{1,2})\s*\+?\s*(?:ans|an|years|year|yrs)", re.IGNORECASE
)
SALARY_RE = re.compile(
    r"(?:(?:MAD|DH|DHS|EUR|USD|€|\$)\s?\d[\d\s.,]+(?:\s?(?:-|to|à)\s?(?:MAD|DH|DHS|EUR|USD|€|\$)?\s?\d[\d\s.,]+)?)",
    re.IGNORECASE,
)


def normalize_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return WHITESPACE_RE.sub(" ", value).strip()


def truncate(value: str, limit: int = 220) -> str:
    cleaned = normalize_whitespace(value)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def build_cache_key(url: str, params: dict[str, Any] | None = None) -> str:
    raw = url if not params else f"{url}?{urlencode(sorted(params.items()))}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def absolute_url(base_url: str, href: str | None) -> str:
    if not href:
        return ""
    return urljoin(base_url, href)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    parsed = None
    if dateparser is not None:
        parsed = dateparser.parse(
            value,
            settings={"RETURN_AS_TIMEZONE_AWARE": False, "PREFER_DATES_FROM": "past"},
            languages=["fr", "en", "ar"],
        )
    if parsed is None:
        for parser in (datetime.fromisoformat,):
            try:
                parsed = parser(value)
                break
            except (TypeError, ValueError):
                continue
    if not parsed:
        return None
    return parsed.date()


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def extract_emails(text: str) -> list[str]:
    return sorted({match.group(0) for match in EMAIL_RE.finditer(text or "")})


def parse_experience_years(text: str) -> int | None:
    values = [int(match.group("years")) for match in EXPERIENCE_RE.finditer(text or "")]
    if not values:
        return None
    return max(values)


def extract_salary_range(text: str) -> str | None:
    match = SALARY_RE.search(text or "")
    if not match:
        return None
    return normalize_whitespace(match.group(0))


def parse_contract_type(text: str) -> str | None:
    normalized = (text or "").lower()
    mapping = {
        "alternance": "Alternance",
        "stage": "Stage",
        "internship": "Stage",
        "intern": "Stage",
        "cdi": "CDI",
        "cdd": "CDD",
        "freelance": "Freelance",
        "contractor": "Freelance",
    }
    for needle, label in mapping.items():
        if needle in normalized:
            return label
    return None


def parse_workplace(text: str) -> str:
    normalized = (text or "").lower()
    if any(keyword in normalized for keyword in ("remote", "télétravail", "teletravail", "work from home")):
        return "remote"
    if any(keyword in normalized for keyword in ("hybrid", "hybride")):
        return "hybrid"
    return "onsite"


def extract_skills(text: str, aliases: dict[str, tuple[str, ...]]) -> list[str]:
    normalized = (text or "").lower()
    found: list[str] = []
    for canonical, variations in aliases.items():
        if any(variation.lower() in normalized for variation in variations):
            found.append(canonical)
    return sorted(found)


def intersect_skills(profile_skills: list[str], job_skills: list[str]) -> list[str]:
    profile_index = {skill.lower(): skill for skill in profile_skills}
    return sorted({profile_index[skill.lower()] for skill in job_skills if skill.lower() in profile_index})


def guess_company_size(text: str) -> str | None:
    normalized = (text or "").lower()
    if "10000+" in normalized or "10,000" in normalized:
        return "10000+"
    if "5000+" in normalized or "5,000" in normalized:
        return "5000+"
    if "1000+" in normalized or "1,000" in normalized:
        return "1000+"
    match = re.search(r"(\d{2,5})\s*\+?\s*(?:employees|collaborateurs|employés)", normalized)
    if match:
        return match.group(1)
    return None


def guess_industry(text: str) -> str | None:
    normalized = (text or "").lower()
    mapping = {
        "Education": ("school", "école", "education", "campus"),
        "Telecom": ("telecom", "orange", "inwi", "maroc telecom"),
        "Consulting": ("consulting", "conseil"),
        "Software": ("software", "saas", "platform", "product"),
        "Retail": ("retail", "e-commerce", "commerce"),
        "Energy": ("energy", "renewable", "mining", "phosphate"),
    }
    for label, keywords in mapping.items():
        if any(keyword in normalized for keyword in keywords):
            return label
    return None


def is_known_tech_company(company: str | None, profile: CandidateProfile) -> bool:
    if not company:
        return False
    normalized = company.lower()
    return any(name in normalized for name in profile.known_tech_companies | profile.startup_keywords)


def is_recent(date_posted: date | None, days: int) -> bool:
    if not date_posted:
        return False
    return (date.today() - date_posted).days <= days


def format_date(value: date | None) -> str:
    return value.isoformat() if value else "-"


def build_fit_statement(company: str, matching_skills: list[str], workplace: str, languages: list[str]) -> str:
    parts: list[str] = []
    if matching_skills:
        parts.append(f"skill overlap: {', '.join(matching_skills[:5])}")
    if workplace in {"remote", "hybrid"}:
        parts.append(f"{workplace} friendly")
    if languages:
        parts.append(f"multilingual: {', '.join(languages)}")
    if company:
        parts.append(f"good entry point at {company}")
    return "; ".join(parts)
