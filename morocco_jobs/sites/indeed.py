from .common import ConfiguredScraper


class IndeedScraper(ConfiguredScraper):
    name = "indeed"
    category = "global"
    domain = "indeed.com"
    base_url = "https://ma.indeed.com"
    search_templates = (
        "https://ma.indeed.com/jobs?q={query}&l=Maroc",
    )
