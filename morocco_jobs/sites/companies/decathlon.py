from ..common import PlaywrightConfiguredScraper


class DecathlonScraper(PlaywrightConfiguredScraper):
    name = "decathlon"
    category = "companies"
    domain = "decathlon.ma"
    base_url = "https://www.decathlon.ma"
    start_urls = ("https://www.decathlon.ma/careers",)
    allowed_external_domains = ("jobs.decathlon.net", "decathlon-recrute.talent-soft.com")
    max_jobs = 20
