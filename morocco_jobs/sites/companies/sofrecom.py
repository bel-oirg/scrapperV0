from ..common import CareerPageScraper


class SofrecomScraper(CareerPageScraper):
    name = "sofrecom"
    category = "companies"
    domain = "sofrecom.com"
    base_url = "https://www.sofrecom.com"
    start_urls = ("https://www.sofrecom.com/en/careers",)
