from .common import ConfiguredScraper


class OptionCarriereScraper(ConfiguredScraper):
    name = "optioncarriere"
    category = "morocco"
    domain = "optioncarriere.ma"
    base_url = "https://www.optioncarriere.ma"
    search_templates = (
        "https://www.optioncarriere.ma/recherche/emploi?s={query}&l=Maroc",
    )
