from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "jobs_cache.sqlite3"
DEFAULT_CACHE_TTL_SECONDS = 2 * 60 * 60
DEFAULT_WATCH_HOURS = 6


@dataclass(slots=True)
class CandidateProfile:
    school: str
    network: str
    campus: str
    experience: str
    base_location: str
    open_to_remote: bool
    level: str
    stack: list[str]
    languages: list[str]
    role_keywords: list[str]
    tech_keywords: list[str]
    culture_keywords: list[str]
    preferred_cities: list[str]
    target_countries: list[str]
    known_tech_companies: set[str]
    startup_keywords: set[str]
    skill_aliases: dict[str, tuple[str, ...]]

    def build_stack(self, override_keywords: Iterable[str] | None = None) -> list[str]:
        if override_keywords:
            return [keyword.strip() for keyword in override_keywords if keyword.strip()]
        return list(self.stack)


DEFAULT_PROFILE = CandidateProfile(
    school="1337 School",
    network="42 Network",
    campus="Khouribga",
    experience="Ex-intern Full Stack Engineer at UM6P",
    base_location="Morocco",
    open_to_remote=True,
    level="junior / intern / first job",
    stack=[
        "React",
        "Node.js",
        "Django",
        "Python",
        "JavaScript",
        "TypeScript",
        "Next.js",
        "PostgreSQL",
        "MongoDB",
        "Docker",
        "REST API",
        "GraphQL",
        "C++",
        "Linux",
        "Git",
    ],
    languages=["French", "Arabic", "English"],
    role_keywords=[
        "full stack",
        "developpeur web",
        "développeur web",
        "software engineer",
        "frontend developer",
        "backend developer",
        "web developer",
        "stagiaire développeur",
        "junior developer",
        "ingénieur logiciel",
        "développeur junior",
        "alternance développeur",
    ],
    tech_keywords=[
        "React",
        "Node.js",
        "Django",
        "Python",
        "JavaScript",
        "TypeScript",
        "Next.js",
        "PostgreSQL",
        "MongoDB",
        "Docker",
        "REST API",
        "GraphQL",
        "C++",
        "Linux",
        "Git",
    ],
    culture_keywords=[
        "42",
        "1337",
        "école 42",
        "ecole 42",
        "42 network",
        "UM6P",
        "bootcamp",
        "self-taught",
        "remote",
        "télétravail",
        "teletravail",
        "hybrid",
    ],
    preferred_cities=["Casablanca", "Rabat"],
    target_countries=["Morocco", "Maroc"],
    known_tech_companies={
        "um6p",
        "ocp",
        "capgemini",
        "cgi",
        "sqli",
        "sofrecom",
        "intelcia",
        "manpower",
        "alten",
        "aubay",
        "decathlon",
        "orange",
        "inwi",
        "maroc telecom",
        "iam",
        "outlierz",
        "212founders",
        "startupmaroc",
        "talent.io",
        "remote ok",
        "himalayas",
        "arc",
        "welcome to the jungle",
    },
    startup_keywords={
        "startup",
        "ventures",
        "studio",
        "lab",
        "innovation",
        "saas",
        "fintech",
        "healthtech",
        "edtech",
        "outlierz",
        "212founders",
        "mcise",
    },
    skill_aliases={
        "React": ("react", "react.js", "reactjs"),
        "Node.js": ("node", "node.js", "nodejs"),
        "Django": ("django",),
        "Python": ("python",),
        "JavaScript": ("javascript", "js", "ecmascript"),
        "TypeScript": ("typescript", "ts"),
        "Next.js": ("next", "next.js", "nextjs"),
        "PostgreSQL": ("postgresql", "postgres", "psql"),
        "MongoDB": ("mongodb", "mongo"),
        "Docker": ("docker", "containerisation", "containerization"),
        "REST API": ("rest", "rest api", "restful api", "api rest"),
        "GraphQL": ("graphql",),
        "C++": ("c++", "cpp"),
        "Linux": ("linux", "unix"),
        "Git": ("git", "github", "gitlab"),
    },
)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.4; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.63.162 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]


class SearchPlanner:
    """Builds site-friendly search queries from the user's keyword matrix."""

    def __init__(self, profile: CandidateProfile, override_keywords: list[str] | None = None) -> None:
        self.profile = profile
        self.override_keywords = [item.strip() for item in (override_keywords or []) if item.strip()]
        self.roles = list(profile.role_keywords)
        self.tech = self.override_keywords or list(profile.tech_keywords)
        self.culture = list(profile.culture_keywords)

    @staticmethod
    def _chunks(values: list[str], size: int) -> list[list[str]]:
        return [values[index : index + size] for index in range(0, len(values), size)]

    @staticmethod
    def _or_group(values: list[str]) -> str:
        quoted = [f'"{value}"' if " " in value else value for value in values]
        return "(" + " OR ".join(quoted) + ")"

    def iter_boolean_queries(self, chunk_size: int = 4) -> list[str]:
        queries: list[str] = []
        for role_group in self._chunks(self.roles, chunk_size):
            for tech_group in self._chunks(self.tech, chunk_size):
                for culture_group in self._chunks(self.culture, chunk_size):
                    queries.append(
                        " ".join(
                            [
                                self._or_group(role_group),
                                self._or_group(tech_group),
                                self._or_group(culture_group),
                            ]
                        )
                    )
        return queries

    def iter_compact_queries(self) -> list[str]:
        queries: list[str] = []
        tech_groups = self._chunks(self.tech, 8) or [self.tech]
        culture_group = self.culture[:6] if self.culture else []
        for role_group in self._chunks(self.roles, 4):
            for tech_group in tech_groups:
                parts = [self._or_group(role_group), self._or_group(tech_group)]
                if culture_group:
                    parts.append(self._or_group(culture_group))
                queries.append(" ".join(parts))
        return queries

    def iter_role_queries(self) -> list[str]:
        return list(self.roles)

    def iter_stack_queries(self) -> list[str]:
        return list(self.tech)

    def iter_cartesian_queries(self) -> list[str]:
        return [f"{role} {tech} {culture}" for role in self.roles for tech in self.tech for culture in self.culture]

    def queries_for_mode(self, mode: str) -> list[str]:
        if mode == "compact":
            return self.iter_compact_queries()
        if mode == "cartesian":
            return self.iter_cartesian_queries()
        if mode == "roles":
            return self.iter_role_queries()
        if mode == "tech":
            return self.iter_stack_queries()
        return self.iter_boolean_queries()
