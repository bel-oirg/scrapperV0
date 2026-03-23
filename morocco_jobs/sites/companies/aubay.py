from ..common import CareerPageScraper


class AubayScraper(CareerPageScraper):
    name = "aubay"
    category = "companies"
    domain = "aubay.ma"
    base_url = "https://www.aubay.ma"
    start_urls = ("https://www.aubay.ma",)
