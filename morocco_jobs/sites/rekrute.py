from .common import ConfiguredScraper


class RekruteScraper(ConfiguredScraper):
    name = "rekrute"
    category = "morocco"
    domain = "rekrute.com"
    base_url = "https://www.rekrute.com"
    search_templates = (
        "https://www.rekrute.com/offres.html?s=1&keyword={query}",
    )
