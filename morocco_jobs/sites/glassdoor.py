from .common import PlaywrightConfiguredScraper


class GlassdoorScraper(PlaywrightConfiguredScraper):
    name = "glassdoor"
    category = "global"
    domain = "glassdoor.com"
    base_url = "https://www.glassdoor.com"
    search_templates = (
        "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}&locT=N&locId=163",
    )
    max_jobs = 16
