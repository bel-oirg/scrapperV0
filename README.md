# Morocco Jobs Scraper

Professional Python CLI to scan Moroccan and remote-friendly junior software jobs tailored to this profile:

- Student at **1337 School (42 Network, Khouribga)**
- Ex-intern **Full Stack Engineer at UM6P**
- Based in **Morocco**, open to **remote**
- Level: **junior / intern / first job**
- Languages: **French, Arabic, English**
- Stack: **React, Node.js, Django, Python, JavaScript, TypeScript, Next.js, PostgreSQL, MongoDB, Docker, REST API, GraphQL, C++, Linux, Git**

## Features

- Scrapes Moroccan job boards, global boards, remote boards, and Moroccan company career pages
- Scores jobs out of 10 using the requested junior-fit scoring rules
- Filters low-signal results with `--min-score`
- Deduplicates jobs with SQLite using URL + title/company hashing
- Caches fetched responses for 2 hours to avoid hammering sites
- Rotates user agents, adds random delays, retries with exponential backoff, and checks `robots.txt`
- Uses Playwright for JS-heavy sources when available
- Exports to CSV, JSON, and Markdown
- Supports `--watch` mode for repeated scans
- Prints a pre-filled cover-letter draft with `--apply-template`

## Layout

```text
morocco_jobs/
├── scraper.py
├── config.py
├── cache.py
├── scorer.py
├── exporter.py
├── notifier.py
├── models.py
├── utils.py
└── sites/
    ├── base.py
    ├── common.py
    ├── rekrute.py
    ├── emploima.py
    ├── linkedin.py
    ├── indeed.py
    ├── remoteok.py
    ├── welcometothejungle.py
    └── companies/
        ├── um6p.py
        ├── capgemini.py
        ├── sqli.py
        └── ...
```

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
python3 scraper.py
python3 scraper.py --sites remote --days 14 --min-score 6
python3 scraper.py --sites linkedin,indeed,companies --keywords react,docker,python --export csv,json,md
python3 scraper.py --contract stage --notify --apply-template
python3 scraper.py --watch
```

## CLI options

```text
--sites all|rekrute|linkedin|remote|companies
--keywords "react,docker,python"
--contract stage|cdi|cdd|remote|all
--days 7|14|30|90
--min-score 4
--export csv|json|md
--notify
--watch
--apply-template
```

## Output

- Rich terminal tables grouped into `Hot matches`, `Good fits`, and `Worth checking`
- Summary dashboard with source count, workplace split, city split, and freshness split
- `jobs.csv` with full structured data
- `jobs.json` for future UI/API usage
- `jobs.md` with a readable report and a `Why you're a fit` column

## Notes

- Some sources are highly dynamic or protected, so Playwright-backed scrapers are included for LinkedIn, Glassdoor, Welcome to the Jungle, Talent.io, Arc.dev, and selected company pages.
- `GitHub Jobs` has been discontinued, so its adapter is retained as a no-op placeholder to preserve source coverage in the CLI registry.
- The query matrix is collapsed into site-friendly grouped boolean searches for most boards; this keeps coverage broad without sending a literal 1,650 search requests to every source.
- Real-world HTML structures change often. The scraper uses JSON-LD extraction first, then falls back to heuristic parsing so the adapters stay maintainable.
