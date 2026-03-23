from ..common import CareerPageScraper


class AltenScraper(CareerPageScraper):
    name = "alten"
    category = "companies"
    domain = "alten.ma"
    base_url = "https://www.alten.ma"
    start_urls = ("https://www.alten.ma/offres",)
