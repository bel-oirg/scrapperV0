from ..common import PlaywrightConfiguredScraper


class CGIScraper(PlaywrightConfiguredScraper):
    name = "cgi"
    category = "companies"
    domain = "cgi.com"
    base_url = "https://www.cgi.com"
    start_urls = ("https://www.cgi.com/fr/fr/careers",)
    allowed_external_domains = ("cgi.njoyn.com",)
    max_jobs = 20
