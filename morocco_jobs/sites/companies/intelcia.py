from ..common import CareerPageScraper


class IntelciaScraper(CareerPageScraper):
    name = "intelcia"
    category = "companies"
    domain = "intelcia.com"
    base_url = "https://www.intelcia.com"
    start_urls = ("https://www.intelcia.com/recrutement",)
