from ..common import PortfolioNetworkScraper


class StartupMarocScraper(PortfolioNetworkScraper):
    name = "startupmaroc"
    category = "companies"
    domain = "startupmaroc.ma"
    base_url = "https://startupmaroc.ma"
    start_urls = ("https://startupmaroc.ma",)
