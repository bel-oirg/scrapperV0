from .common import PlaywrightConfiguredScraper


class ArcDevScraper(PlaywrightConfiguredScraper):
    name = "arcdev"
    category = "remote"
    domain = "arc.dev"
    base_url = "https://arc.dev"
    search_templates = (
        "https://arc.dev/remote-jobs?search={query}",
    )
    max_jobs = 15
