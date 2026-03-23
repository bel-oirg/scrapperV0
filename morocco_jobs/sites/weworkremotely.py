from .common import ConfiguredScraper


class WeWorkRemotelyScraper(ConfiguredScraper):
    name = "weworkremotely"
    category = "remote"
    domain = "weworkremotely.com"
    base_url = "https://weworkremotely.com"
    search_templates = (
        "https://weworkremotely.com/remote-jobs/search?term={query}",
    )
