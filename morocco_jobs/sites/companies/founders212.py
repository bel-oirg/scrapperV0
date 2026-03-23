from ..common import PortfolioNetworkScraper


class Founders212Scraper(PortfolioNetworkScraper):
    name = "founders212"
    category = "companies"
    domain = "212founders.ma"
    base_url = "https://www.212founders.ma"
    start_urls = ("https://www.212founders.ma",)
