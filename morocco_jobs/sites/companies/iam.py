from ..common import CareerPageScraper


class IAMScraper(CareerPageScraper):
    name = "iam"
    category = "companies"
    domain = "iam.ma"
    base_url = "https://www.iam.ma"
    start_urls = ("https://www.iam.ma/carriere",)
