from .common import RetiredSourceScraper


class GitHubJobsScraper(RetiredSourceScraper):
    name = "github_jobs"
    category = "remote"
    domain = "github.com"
    base_url = "https://github.com"
    retired_reason = "GitHub Jobs was sunset, so the scraper keeps the source slot but returns no listings."
