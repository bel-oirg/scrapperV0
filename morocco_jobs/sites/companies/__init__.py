from .alten import AltenScraper
from .aubay import AubayScraper
from .capgemini import CapgeminiScraper
from .cgi import CGIScraper
from .decathlon import DecathlonScraper
from .founders212 import Founders212Scraper
from .iam import IAMScraper
from .intelcia import IntelciaScraper
from .inwi import InwiScraper
from .manpower import ManpowerScraper
from .mcise import MciseScraper
from .ocpgroup import OCPGroupScraper
from .orange import OrangeScraper
from .sofrecom import SofrecomScraper
from .sqli import SQLIScraper
from .startupmaroc import StartupMarocScraper
from .outlierz import OutlierzScraper
from .um6p import UM6PScraper


def build_company_registry() -> dict[str, type]:
    return {
        "um6p": UM6PScraper,
        "ocpgroup": OCPGroupScraper,
        "capgemini": CapgeminiScraper,
        "cgi": CGIScraper,
        "sqli": SQLIScraper,
        "sofrecom": SofrecomScraper,
        "intelcia": IntelciaScraper,
        "manpower": ManpowerScraper,
        "alten": AltenScraper,
        "aubay": AubayScraper,
        "decathlon": DecathlonScraper,
        "orange": OrangeScraper,
        "inwi": InwiScraper,
        "iam": IAMScraper,
        "mcise": MciseScraper,
        "startupmaroc": StartupMarocScraper,
        "outlierz": OutlierzScraper,
        "founders212": Founders212Scraper,
    }
