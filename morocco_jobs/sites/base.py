from __future__ import annotations

import asyncio
import json
import random
import time
from abc import ABC
from datetime import date
from typing import Any
from urllib.parse import quote_plus, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from ..cache import SQLiteCache
from ..config import CandidateProfile, SearchPlanner, USER_AGENTS
from ..models import JobPosting, SearchOptions
from ..utils import (
    absolute_url,
    build_cache_key,
    extract_emails,
    extract_salary_range,
    extract_skills,
    guess_company_size,
    guess_industry,
    normalize_whitespace,
    parse_contract_type,
    parse_date,
    parse_experience_years,
    parse_workplace,
)


class BaseScraper(ABC):
    name = "base"
    category = "other"
    domain = ""
    base_url = ""
    start_urls: tuple[str, ...] = ()
    search_templates: tuple[str, ...] = ()
    query_mode = "compact"
    use_playwright = False
    max_listings_per_page = 12
    max_jobs = 40
    timeout = 25
    max_discovery_urls = 6
    allowed_external_domains: tuple[str, ...] = ()
    job_link_markers = (
        "job",
        "jobs",
        "career",
        "careers",
        "emploi",
        "offre",
        "recrut",
        "vacancy",
        "position",
        "talent",
        "join-us",
        "joinus",
    )

    def __init__(self, profile: CandidateProfile, cache: SQLiteCache) -> None:
        self.profile = profile
        self.cache = cache
        self.session = requests.Session()
        self.session.headers.update({"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"})
        self._robots: dict[str, RobotFileParser] = {}

    async def scrape(self, planner: SearchPlanner, options: SearchOptions) -> list[JobPosting]:
        deadline = time.monotonic() + max(1, options.source_timeout_seconds)
        if self.use_playwright:
            return await self.scrape_playwright(planner, options, deadline)
        return await asyncio.to_thread(self.scrape_sync, planner, options, deadline)

    def scrape_sync(
        self,
        planner: SearchPlanner,
        options: SearchOptions,
        deadline: float | None = None,
    ) -> list[JobPosting]:
        jobs: dict[str, JobPosting] = {}
        for url in self.discovery_urls(planner, options):
            if self._deadline_reached(deadline):
                break
            if len(jobs) >= self.job_limit(options):
                break
            html = self.fetch_text(url, deadline)
            if not html:
                continue
            for job in self.extract_jobs_from_listing(html, url, options, deadline):
                jobs.setdefault(job.dedup_key, job)
                if len(jobs) >= self.job_limit(options):
                    break
        return list(jobs.values())

    async def scrape_playwright(
        self,
        planner: SearchPlanner,
        options: SearchOptions,
        deadline: float | None = None,
    ) -> list[JobPosting]:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return await asyncio.to_thread(self.scrape_sync, planner, options, deadline)

        jobs: dict[str, JobPosting] = {}
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                locale="fr-FR",
                viewport={"width": 1440, "height": 900},
            )
            await context.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR', 'fr', 'en-US', 'en']});
                """
            )
            page = await context.new_page()
            for url in self.discovery_urls(planner, options):
                if self._deadline_reached(deadline):
                    break
                if len(jobs) >= self.job_limit(options):
                    break
                try:
                    remaining_ms = self._remaining_ms(deadline)
                    if remaining_ms is not None and remaining_ms <= 0:
                        break
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=min(self.timeout * 1000, remaining_ms) if remaining_ms else self.timeout * 1000,
                    )
                    wait_ms = random.randint(1500, 4000)
                    if remaining_ms is not None:
                        wait_ms = max(0, min(wait_ms, remaining_ms))
                    if wait_ms:
                        await page.wait_for_timeout(wait_ms)
                    html = await page.content()
                except Exception:
                    continue
                for job in self.extract_jobs_from_listing(html, url, options, deadline):
                    jobs.setdefault(job.dedup_key, job)
                    if len(jobs) >= self.job_limit(options):
                        break
            await context.close()
            await browser.close()
        return list(jobs.values())

    def discovery_urls(self, planner: SearchPlanner, options: SearchOptions | None = None) -> list[str]:
        urls = list(self.start_urls)
        query_mode = self.query_mode
        if options and options.deep_scan and self.search_templates:
            query_mode = "boolean"
        queries = planner.queries_for_mode(query_mode)
        limit = self.discovery_limit(options)
        if limit:
            queries = queries[:limit]
        for template in self.search_templates:
            for query in queries:
                encoded = quote_plus(query)
                urls.append(template.format(query=encoded, raw_query=query, location="Morocco", country="MA"))
        return urls

    def discovery_limit(self, options: SearchOptions | None) -> int:
        if options and options.deep_scan:
            return 0
        return self.max_discovery_urls

    def listings_limit(self, options: SearchOptions | None) -> int:
        if options and options.deep_scan:
            return max(self.max_listings_per_page, 30)
        return self.max_listings_per_page

    def job_limit(self, options: SearchOptions | None) -> int:
        if options and options.deep_scan:
            return max(self.max_jobs, 100)
        return self.max_jobs

    def fetch_text(self, url: str, deadline: float | None = None) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return None
        if self._deadline_reached(deadline):
            return None
        if not self.allowed_by_robots(url):
            return None

        cache_key = build_cache_key(url)
        cached = self.cache.get_response(cache_key)
        if cached is not None:
            return cached

        for attempt in range(3):
            try:
                if self._deadline_reached(deadline):
                    return None
                delay = random.uniform(1.5, 4.0)
                remaining_seconds = self._remaining_seconds(deadline)
                if remaining_seconds is not None:
                    delay = min(delay, max(0.0, remaining_seconds))
                if delay > 0:
                    time.sleep(delay)
                remaining_seconds = self._remaining_seconds(deadline)
                request_timeout = self.timeout
                if remaining_seconds is not None:
                    if remaining_seconds <= 0:
                        return None
                    request_timeout = max(1.0, min(float(self.timeout), remaining_seconds))
                response = self.session.get(
                    url,
                    headers={"User-Agent": random.choice(USER_AGENTS)},
                    timeout=request_timeout,
                )
                if response.status_code >= 400:
                    raise requests.HTTPError(f"{response.status_code} for {url}")
                response.encoding = response.encoding or "utf-8"
                self.cache.set_response(cache_key, url, response.text, response.status_code)
                return response.text
            except Exception:
                remaining_seconds = self._remaining_seconds(deadline)
                backoff = float(2**attempt)
                if remaining_seconds is not None:
                    backoff = min(backoff, max(0.0, remaining_seconds))
                if backoff > 0:
                    time.sleep(backoff)
        return None

    def allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robots:
            parser = RobotFileParser()
            parser.set_url(f"{base}/robots.txt")
            try:
                parser.read()
            except Exception:
                return True
            self._robots[base] = parser
        try:
            return self._robots[base].can_fetch(random.choice(USER_AGENTS), url)
        except Exception:
            return True

    def extract_jobs_from_listing(
        self,
        html: str,
        url: str,
        options: SearchOptions | None = None,
        deadline: float | None = None,
    ) -> list[JobPosting]:
        soup = BeautifulSoup(html, "html.parser")
        schema_jobs = self.extract_schema_jobs(soup, url)
        if schema_jobs:
            return schema_jobs

        jobs: list[JobPosting] = []
        candidates: list[tuple[str, str]] = []
        for anchor in soup.find_all("a", href=True):
            href = absolute_url(url, anchor.get("href"))
            link_text = normalize_whitespace(anchor.get_text(" ", strip=True))
            if not href or href == url:
                continue
            if not self.looks_like_job_link(href, link_text):
                continue
            candidates.append((href, link_text))
            if len(candidates) >= self.listings_limit(options):
                break

        for href, link_text in candidates:
            if self._deadline_reached(deadline):
                break
            job = self.parse_job_page(href, hint_title=link_text, deadline=deadline)
            if job:
                jobs.append(job)
            if len(jobs) >= self.job_limit(options):
                break
        return jobs

    def looks_like_job_link(self, href: str, link_text: str) -> bool:
        parsed = urlparse(href)
        domain = parsed.netloc.lower()
        allowed = self.domain in domain or any(extra in domain for extra in self.allowed_external_domains)
        if not allowed:
            return False
        haystack = f"{href.lower()} {link_text.lower()}"
        return any(marker in haystack for marker in self.job_link_markers)

    def parse_job_page(
        self,
        url: str,
        hint_title: str = "",
        deadline: float | None = None,
    ) -> JobPosting | None:
        html = self.fetch_text(url, deadline)
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        schema_jobs = self.extract_schema_jobs(soup, url)
        if schema_jobs:
            return schema_jobs[0]

        title = normalize_whitespace(self._pick_first_text(soup, ["h1", "title"])) or hint_title
        description = self._extract_description(soup)
        company = self.extract_company(soup) or self.company_from_domain()
        location = self.extract_location(soup, description)
        job = JobPosting(
            source=self.name,
            source_category=self.category,
            title=title or "Untitled role",
            company=company,
            company_size=guess_company_size(description),
            industry=guess_industry(description),
            location=location,
            workplace=parse_workplace(f"{location} {title} {description}"),
            contract_type=parse_contract_type(f"{title} {description}"),
            salary_range=extract_salary_range(description),
            date_posted=self.extract_date(soup, description),
            description=description,
            required_skills=extract_skills(description, self.profile.skill_aliases),
            application_url=self.extract_application_url(soup, url),
            contact_email=(extract_emails(description) or [None])[0],
            experience_years=parse_experience_years(description),
            raw_metadata={"url": url},
        )
        return job if job.title and job.company else None

    def extract_schema_jobs(self, soup: BeautifulSoup, url: str) -> list[JobPosting]:
        items: list[dict[str, Any]] = []
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            items.extend(self._flatten_schema(data))

        jobs: list[JobPosting] = []
        for item in items:
            if item.get("@type") != "JobPosting":
                continue
            company_block = item.get("hiringOrganization") or {}
            base_description = BeautifulSoup(item.get("description", ""), "html.parser").get_text(" ", strip=True)
            location_block = item.get("jobLocation") or {}
            address = location_block.get("address") if isinstance(location_block, dict) else {}
            location = normalize_whitespace(
                " ".join(
                    part
                    for part in [
                        address.get("addressLocality") if isinstance(address, dict) else "",
                        address.get("addressCountry") if isinstance(address, dict) else "",
                    ]
                    if part
                )
            )
            job = JobPosting(
                source=self.name,
                source_category=self.category,
                title=normalize_whitespace(item.get("title")) or "Untitled role",
                company=normalize_whitespace(company_block.get("name")) or self.company_from_domain(),
                company_size=guess_company_size(base_description),
                industry=guess_industry(base_description),
                location=location or self.extract_address_text(address),
                workplace=parse_workplace(f"{location} {base_description}"),
                contract_type=parse_contract_type(base_description),
                salary_range=extract_salary_range(base_description),
                date_posted=parse_date(item.get("datePosted")),
                description=normalize_whitespace(base_description),
                required_skills=extract_skills(base_description, self.profile.skill_aliases),
                application_url=item.get("url") or url,
                contact_email=(extract_emails(base_description) or [None])[0],
                experience_years=parse_experience_years(base_description),
                raw_metadata={"schema": item, "url": url},
            )
            jobs.append(job)
        return jobs

    def _flatten_schema(self, data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            result: list[dict[str, Any]] = []
            for item in data:
                result.extend(self._flatten_schema(item))
            return result
        if isinstance(data, dict) and "@graph" in data:
            return self._flatten_schema(data["@graph"])
        return [data] if isinstance(data, dict) else []

    def _pick_first_text(self, soup: BeautifulSoup, selectors: list[str]) -> str:
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                text = normalize_whitespace(node.get_text(" ", strip=True))
                if text:
                    return text
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        candidates = [
            soup.select_one("article"),
            soup.select_one("main"),
            soup.select_one("[class*=description]"),
            soup.select_one("[class*=content]"),
        ]
        texts = [normalize_whitespace(node.get_text(" ", strip=True)) for node in candidates if node]
        if texts:
            return max(texts, key=len)
        return normalize_whitespace(soup.get_text(" ", strip=True))

    def extract_company(self, soup: BeautifulSoup) -> str | None:
        selectors = [
            "[class*=company]",
            "[data-testid*=company]",
            "[itemprop=hiringOrganization]",
            "meta[property='og:site_name']",
        ]
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            text = normalize_whitespace(node.get("content") if node.name == "meta" else node.get_text(" ", strip=True))
            if text:
                return text
        return None

    def extract_location(self, soup: BeautifulSoup, description: str) -> str | None:
        selectors = ["[class*=location]", "[data-testid*=location]", "[itemprop=jobLocation]"]
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                text = normalize_whitespace(node.get_text(" ", strip=True))
                if text:
                    return text
        for city in ["Casablanca", "Rabat", "Morocco", "Maroc", "Remote", "Télétravail", "Hybrid"]:
            if city.lower() in description.lower():
                return city
        return None

    def extract_date(self, soup: BeautifulSoup, description: str) -> date | None:
        selectors = ["time", "[datetime]", "[class*=date]", "[data-testid*=date]"]
        for selector in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            value = node.get("datetime") or node.get_text(" ", strip=True)
            parsed = parse_date(value)
            if parsed:
                return parsed
        return parse_date(description)

    def extract_application_url(self, soup: BeautifulSoup, url: str) -> str:
        for anchor in soup.find_all("a", href=True):
            text = normalize_whitespace(anchor.get_text(" ", strip=True)).lower()
            href = absolute_url(url, anchor.get("href"))
            if any(marker in text for marker in ("apply", "postuler", "candidater", "submit")):
                return href
        return url

    def company_from_domain(self) -> str:
        parsed = urlparse(self.base_url or f"https://{self.domain}")
        host = parsed.netloc or self.domain
        labels = [label for label in host.split(".") if label]
        label = labels[0] if labels else host
        if label in {"www", "careers", "jobs"} and len(labels) > 1:
            label = labels[1]
        return label.replace("-", " ").title()

    @staticmethod
    def extract_address_text(address: Any) -> str:
        if not isinstance(address, dict):
            return ""
        return normalize_whitespace(
            " ".join(
                str(address.get(field, ""))
                for field in ("addressLocality", "addressRegion", "addressCountry")
                if address.get(field)
            )
        )

    @staticmethod
    def _remaining_seconds(deadline: float | None) -> float | None:
        if deadline is None:
            return None
        return deadline - time.monotonic()

    @classmethod
    def _remaining_ms(cls, deadline: float | None) -> int | None:
        remaining = cls._remaining_seconds(deadline)
        if remaining is None:
            return None
        return max(0, int(remaining * 1000))

    @classmethod
    def _deadline_reached(cls, deadline: float | None) -> bool:
        remaining = cls._remaining_seconds(deadline)
        return remaining is not None and remaining <= 0
