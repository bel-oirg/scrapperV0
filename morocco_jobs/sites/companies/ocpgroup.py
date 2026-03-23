from ..common import CareerPageScraper


class OCPGroupScraper(CareerPageScraper):
    name = "ocpgroup"
    category = "companies"
    domain = "ocpgroup.ma"
    base_url = "https://www.ocpgroup.ma"
    start_urls = ("https://www.ocpgroup.ma/careers",)
