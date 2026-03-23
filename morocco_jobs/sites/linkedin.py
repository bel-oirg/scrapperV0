from .common import PlaywrightConfiguredScraper


class LinkedInScraper(PlaywrightConfiguredScraper):
    name = "linkedin"
    category = "global"
    domain = "linkedin.com"
    base_url = "https://www.linkedin.com"
    search_templates = (
        "https://www.linkedin.com/jobs/search/?keywords={query}&location=Morocco&f_WT=2",
    )
    max_jobs = 20

    def looks_like_job_link(self, href: str, link_text: str) -> bool:
        lowered = href.lower()
        if "/jobs/view/" not in lowered:
            return False
        return super().looks_like_job_link(href, link_text)
