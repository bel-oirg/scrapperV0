from . import companies
from .arcdev import ArcDevScraper
from .emploima import EmploiMaScraper
from .glassdoor import GlassdoorScraper
from .github_jobs import GitHubJobsScraper
from .himalayas import HimalayasScraper
from .indeed import IndeedScraper
from .jobsma import JobsMaScraper
from .linkedin import LinkedInScraper
from .marocannonces import MarocAnnoncesScraper
from .mrecrut import MRecrutScraper
from .nodesk import NoDeskScraper
from .optioncarriere import OptionCarriereScraper
from .rekrute import RekruteScraper
from .remoteok import RemoteOkScraper
from .talentio import TalentIOScraper
from .weworkremotely import WeWorkRemotelyScraper
from .welcometothejungle import WelcomeToTheJungleScraper


def build_registry() -> dict[str, type]:
    company_scrapers = companies.build_company_registry()
    registry = {
        "rekrute": RekruteScraper,
        "emploima": EmploiMaScraper,
        "marocannonces": MarocAnnoncesScraper,
        "mrecrut": MRecrutScraper,
        "jobsma": JobsMaScraper,
        "optioncarriere": OptionCarriereScraper,
        "linkedin": LinkedInScraper,
        "indeed": IndeedScraper,
        "glassdoor": GlassdoorScraper,
        "welcometothejungle": WelcomeToTheJungleScraper,
        "talentio": TalentIOScraper,
        "remoteok": RemoteOkScraper,
        "weworkremotely": WeWorkRemotelyScraper,
        "himalayas": HimalayasScraper,
        "arcdev": ArcDevScraper,
        "nodesk": NoDeskScraper,
        "github_jobs": GitHubJobsScraper,
    }
    registry.update(company_scrapers)
    return registry


def category_map() -> dict[str, set[str]]:
    company_names = set(companies.build_company_registry())
    return {
        "morocco": {"rekrute", "emploima", "marocannonces", "mrecrut", "jobsma", "optioncarriere"},
        "global": {"linkedin", "indeed", "glassdoor", "welcometothejungle", "talentio"},
        "remote": {"remoteok", "weworkremotely", "himalayas", "arcdev", "nodesk", "github_jobs"},
        "companies": company_names,
        "all": set(build_registry()),
    }
