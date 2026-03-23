from ..common import PlaywrightConfiguredScraper


class CapgeminiScraper(PlaywrightConfiguredScraper):
    name = "capgemini"
    category = "companies"
    domain = "capgemini.com"
    base_url = "https://www.capgemini.com"
    start_urls = ("https://www.capgemini.com/jobs/",)
    allowed_external_domains = ("jobs.capgemini.com", "wd3.myworkdayjobs.com")
    max_jobs = 20
