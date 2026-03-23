from .common import ConfiguredScraper


class NoDeskScraper(ConfiguredScraper):
    name = "nodesk"
    category = "remote"
    domain = "nodesk.co"
    base_url = "https://nodesk.co"
    search_templates = (
        "https://nodesk.co/remote-jobs/?search_keywords={query}",
    )
