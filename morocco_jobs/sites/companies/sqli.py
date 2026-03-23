from ..common import CareerPageScraper


class SQLIScraper(CareerPageScraper):
    name = "sqli"
    category = "companies"
    domain = "sqli.com"
    base_url = "https://www.sqli.com"
    start_urls = ("https://www.sqli.com/int-en/talents/jobs",)
