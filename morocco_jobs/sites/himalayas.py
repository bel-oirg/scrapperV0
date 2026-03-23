from .common import ConfiguredScraper


class HimalayasScraper(ConfiguredScraper):
    name = "himalayas"
    category = "remote"
    domain = "himalayas.app"
    base_url = "https://himalayas.app"
    search_templates = (
        "https://himalayas.app/jobs?query={query}",
    )
