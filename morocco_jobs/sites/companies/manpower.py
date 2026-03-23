from ..common import CareerPageScraper


class ManpowerScraper(CareerPageScraper):
    name = "manpower"
    category = "companies"
    domain = "manpower.ma"
    base_url = "https://www.manpower.ma"
    start_urls = ("https://www.manpower.ma",)
