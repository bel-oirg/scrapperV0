from .common import ConfiguredScraper


class MarocAnnoncesScraper(ConfiguredScraper):
    name = "marocannonces"
    category = "morocco"
    domain = "marocannonces.com"
    base_url = "https://www.marocannonces.com"
    search_templates = (
        "https://www.marocannonces.com/categorie/309/Emploi.html?q={query}",
    )
