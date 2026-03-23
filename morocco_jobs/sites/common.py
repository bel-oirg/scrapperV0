from __future__ import annotations

import asyncio
import json
from urllib.parse import urljoin

from .base import BaseScraper
from ..models import JobPosting, SearchOptions
from ..utils import normalize_whitespace, parse_date, parse_workplace


class ConfiguredScraper(BaseScraper):
    """Generic HTML scraper configured by URL templates and heuristics."""


class CareerPageScraper(ConfiguredScraper):
    query_mode = "boolean"
    max_jobs = 25

    def discovery_urls(self, planner, options=None) -> list[str]:
        return list(self.start_urls)


class PlaywrightConfiguredScraper(ConfiguredScraper):
    use_playwright = True
    max_jobs = 25
    max_discovery_urls = 4


class RemoteOKApiScraper(BaseScraper):
    name = "remoteok"
    category = "remote"
    domain = "remoteok.com"
    base_url = "https://remoteok.com"
    api_url = "https://remoteok.com/api"

    def scrape_sync(self, planner, options: SearchOptions) -> list[JobPosting]:
        html = self.fetch_text(self.api_url)
        if not html:
            return []
        try:
            payload = json.loads(html)
        except json.JSONDecodeError:
            return []
        jobs: list[JobPosting] = []
        desired_stack = {skill.lower() for skill in planner.tech}
        for item in payload:
            if not isinstance(item, dict) or "position" not in item:
                continue
            tags = [normalize_whitespace(tag) for tag in item.get("tags", [])]
            description = " ".join(tags + [item.get("description", ""), item.get("position", "")])
            lowered_title = item.get("position", "").lower()
            if "dev" not in lowered_title and "engineer" not in lowered_title and "developer" not in lowered_title:
                continue
            if "senior" in lowered_title:
                continue
            tag_pool = {tag.lower() for tag in tags}
            if desired_stack and not (tag_pool & desired_stack):
                continue
            jobs.append(
                JobPosting(
                    source=self.name,
                    source_category=self.category,
                    title=item.get("position", "Untitled role"),
                    company=item.get("company", "Unknown company"),
                    industry="Software",
                    location=item.get("location") or "Remote",
                    workplace="remote",
                    contract_type=item.get("employment_type"),
                    salary_range=item.get("salary_min"),
                    date_posted=parse_date(item.get("date")),
                    description=normalize_whitespace(description),
                    required_skills=tags,
                    application_url=item.get("url") or urljoin(self.base_url, item.get("slug", "")),
                    raw_metadata=item,
                )
            )
            if len(jobs) >= self.max_jobs:
                break
        return jobs


class PortfolioNetworkScraper(CareerPageScraper):
    company_limit = 4
    candidate_paths = ("/careers", "/jobs", "/join-us")

    def extract_jobs_from_listing(
        self,
        html: str,
        url: str,
        options: SearchOptions | None = None,
    ) -> list[JobPosting]:
        jobs = super().extract_jobs_from_listing(html, url, options)
        if jobs:
            return jobs
        soup = self._soup(html)
        company_links: list[str] = []
        seen_links: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            if href.startswith("mailto:"):
                continue
            absolute = urljoin(url, href)
            if absolute.startswith("http") and absolute not in seen_links:
                company_links.append(absolute)
                seen_links.add(absolute)
            if len(company_links) >= self.company_limit:
                break
        discovered: list[JobPosting] = []
        for company_url in company_links:
            for path in self.candidate_paths:
                candidate = urljoin(company_url, path)
                job_page = self.fetch_text(candidate)
                if not job_page:
                    continue
                discovered.extend(super().extract_jobs_from_listing(job_page, candidate, options))
                if len(discovered) >= self.max_jobs:
                    return discovered
        return discovered

    @staticmethod
    def _soup(html: str):
        from bs4 import BeautifulSoup

        return BeautifulSoup(html, "html.parser")


class RetiredSourceScraper(BaseScraper):
    retired_reason = "This source is no longer publicly available."

    async def scrape(self, planner, options: SearchOptions) -> list[JobPosting]:
        await asyncio.sleep(0)
        return []
