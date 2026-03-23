from .common import PlaywrightConfiguredScraper


class WelcomeToTheJungleScraper(PlaywrightConfiguredScraper):
    name = "welcometothejungle"
    category = "global"
    domain = "welcometothejungle.com"
    base_url = "https://www.welcometothejungle.com"
    search_templates = (
        "https://www.welcometothejungle.com/en/jobs?query={query}&aroundQuery=Morocco",
    )
    max_jobs = 20
