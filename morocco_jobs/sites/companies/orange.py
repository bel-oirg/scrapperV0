from ..common import CareerPageScraper


class OrangeScraper(CareerPageScraper):
    name = "orange"
    category = "companies"
    domain = "orange.ma"
    base_url = "https://www.orange.ma"
    start_urls = ("https://www.orange.ma/carrieres",)
