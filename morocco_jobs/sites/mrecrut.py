from .common import ConfiguredScraper


class MRecrutScraper(ConfiguredScraper):
    name = "mrecrut"
    category = "morocco"
    domain = "m-recrut.com"
    base_url = "https://m-recrut.com"
    search_templates = (
        "https://m-recrut.com/recherche?keywords={query}",
    )
