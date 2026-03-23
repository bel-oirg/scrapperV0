from .common import ConfiguredScraper


class EmploiMaScraper(ConfiguredScraper):
    name = "emploima"
    category = "morocco"
    domain = "emploi.ma"
    base_url = "https://www.emploi.ma"
    search_templates = (
        "https://www.emploi.ma/recherche-jobs-maroc/{query}",
    )
