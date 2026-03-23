from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha1
from typing import Any


@dataclass(slots=True)
class JobPosting:
    source: str
    source_category: str
    title: str
    company: str
    company_size: str | None = None
    industry: str | None = None
    location: str | None = None
    workplace: str = "onsite"
    contract_type: str | None = None
    salary_range: str | None = None
    date_posted: date | None = None
    description: str = ""
    required_skills: list[str] = field(default_factory=list)
    matching_skills: list[str] = field(default_factory=list)
    application_url: str = ""
    contact_email: str | None = None
    relevance_score: int = 0
    why_fit: str = ""
    experience_years: int | None = None
    is_known_tech: bool = False
    raw_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def dedup_key(self) -> str:
        material = f"{self.title}|{self.company}" if self.title and self.company else self.application_url
        return sha1(material.strip().lower().encode("utf-8")).hexdigest()

    def to_record(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_category": self.source_category,
            "title": self.title,
            "company": self.company,
            "company_size": self.company_size or "",
            "industry": self.industry or "",
            "location": self.location or "",
            "workplace": self.workplace,
            "contract_type": self.contract_type or "",
            "salary_range": self.salary_range or "",
            "date_posted": self.date_posted.isoformat() if self.date_posted else "",
            "required_skills": ", ".join(self.required_skills),
            "matching_skills": ", ".join(self.matching_skills),
            "application_url": self.application_url,
            "contact_email": self.contact_email or "",
            "relevance_score": self.relevance_score,
            "why_fit": self.why_fit,
            "experience_years": self.experience_years or "",
            "description": self.description,
        }


@dataclass(slots=True)
class SearchOptions:
    sites: list[str]
    keywords_override: list[str]
    contract: str
    days: int
    min_score: int
    export_formats: list[str]
    notify: bool = False
    watch: bool = False
    apply_template: bool = False
    deep_scan: bool = False
    source_timeout_seconds: int = 90


@dataclass(slots=True)
class ScanSummary:
    total_jobs: int
    total_sources: int
    remote_jobs: int
    hybrid_jobs: int
    onsite_jobs: int
    casablanca_jobs: int
    rabat_jobs: int
    other_jobs: int
    last_7_days: int
    last_30_days: int
