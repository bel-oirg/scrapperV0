from ..common import PortfolioNetworkScraper


class OutlierzScraper(PortfolioNetworkScraper):
    name = "outlierz"
    category = "companies"
    domain = "outlierz.com"
    base_url = "https://outlierz.com"
    start_urls = ("https://outlierz.com",)
