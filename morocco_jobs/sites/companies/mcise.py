from ..common import PortfolioNetworkScraper


class MciseScraper(PortfolioNetworkScraper):
    name = "mcise"
    category = "companies"
    domain = "mcise.um6p.ma"
    base_url = "https://mcise.um6p.ma"
    start_urls = ("https://mcise.um6p.ma",)
