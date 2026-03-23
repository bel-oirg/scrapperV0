from ..common import CareerPageScraper


class InwiScraper(CareerPageScraper):
    name = "inwi"
    category = "companies"
    domain = "inwi.ma"
    base_url = "https://www.inwi.ma"
    start_urls = ("https://www.inwi.ma/recrutement",)
