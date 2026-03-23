from ..common import CareerPageScraper


class UM6PScraper(CareerPageScraper):
    name = "um6p"
    category = "companies"
    domain = "careers.um6p.ma"
    base_url = "https://careers.um6p.ma"
    start_urls = ("https://careers.um6p.ma",)
