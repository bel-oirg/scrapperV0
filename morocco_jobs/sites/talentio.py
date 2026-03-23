from .common import PlaywrightConfiguredScraper


class TalentIOScraper(PlaywrightConfiguredScraper):
    name = "talentio"
    category = "global"
    domain = "talent.io"
    base_url = "https://www.talent.io"
    search_templates = (
        "https://www.talent.io/en/jobs?query={query}&location=morocco",
    )
    max_jobs = 20
