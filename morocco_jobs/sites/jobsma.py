from .common import ConfiguredScraper


class JobsMaScraper(ConfiguredScraper):
    name = "jobsma"
    category = "morocco"
    domain = "jobs.ma"
    base_url = "https://www.jobs.ma"
    search_templates = (
        "https://www.jobs.ma/jobs?keywords={query}",
    )
