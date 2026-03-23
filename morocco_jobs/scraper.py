from __future__ import annotations

import argparse
import asyncio
import sys
import time
from typing import TYPE_CHECKING, Iterable, Any

if TYPE_CHECKING:
    from .models import JobPosting, SearchOptions


class PlainConsole:
    def print(self, *args: Any, **kwargs: Any) -> None:
        print(*args)


def get_console():
    try:
        from rich.console import Console

        return Console()
    except ImportError:  # pragma: no cover - used before dependencies are installed.
        return PlainConsole()


console = get_console()
SOURCE_TIMEOUT_SECONDS = 90


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Professional Morocco-focused job scraper CLI.")
    parser.add_argument("--sites", default="all", help="all|rekrute|linkedin|remote|companies or comma-separated values")
    parser.add_argument("--keywords", default="", help="Override stack keywords, e.g. react,docker,python")
    parser.add_argument("--contract", default="all", choices=["stage", "cdi", "cdd", "remote", "all", "freelance", "alternance"])
    parser.add_argument("--days", type=int, default=30, choices=[7, 14, 30, 90])
    parser.add_argument("--min-score", type=int, default=4)
    parser.add_argument("--export", default="", help="csv|json|md or comma-separated")
    parser.add_argument("--notify", action="store_true", help="Print summary and play beep.")
    parser.add_argument("--watch", action="store_true", help="Re-run every 6h and notify only new jobs.")
    parser.add_argument("--apply-template", action="store_true", help="Print a pre-filled cover letter template for the best match.")
    parser.add_argument("--deep-scan", action="store_true", help="Run a much larger scan across more queries and listings per source.")
    return parser.parse_args(argv)


def resolve_sites(selection: str) -> list[str]:
    from .sites import build_registry, category_map

    requested = [item.strip().lower() for item in selection.split(",") if item.strip()]
    registry = build_registry()
    groups = category_map()
    resolved: set[str] = set()
    for item in requested or ["all"]:
        if item in groups:
            resolved.update(groups[item])
            continue
        if item in registry:
            resolved.add(item)
    return sorted(resolved or groups["all"])


def build_options(args: argparse.Namespace):
    from .models import SearchOptions

    return SearchOptions(
        sites=resolve_sites(args.sites),
        keywords_override=[item.strip() for item in args.keywords.split(",") if item.strip()],
        contract=args.contract,
        days=args.days,
        min_score=args.min_score,
        export_formats=[item.strip().lower() for item in args.export.split(",") if item.strip()],
        notify=args.notify,
        watch=args.watch,
        apply_template=args.apply_template,
        deep_scan=args.deep_scan,
    )


def passes_filters(job, options) -> bool:
    from .utils import is_recent

    if job.relevance_score < options.min_score:
        return False
    if options.contract != "all":
        if options.contract == "remote":
            if job.workplace != "remote":
                return False
        elif (job.contract_type or "").lower() != options.contract:
            return False
    if options.days and job.date_posted and not is_recent(job.date_posted, options.days):
        return False
    return True


def score_and_filter(jobs: Iterable["JobPosting"], options) -> list["JobPosting"]:
    from .config import DEFAULT_PROFILE
    from .scorer import annotate_job
    from .utils import intersect_skills

    desired_stack = DEFAULT_PROFILE.build_stack(options.keywords_override)
    seen: dict[str, "JobPosting"] = {}
    for job in jobs:
        job.matching_skills = intersect_skills(desired_stack, job.required_skills)
        annotate_job(job, DEFAULT_PROFILE)
        if passes_filters(job, options):
            seen.setdefault(job.dedup_key, job)
    return sorted(
        seen.values(),
        key=lambda item: (
            item.relevance_score,
            item.date_posted.toordinal() if item.date_posted else 0,
            item.title.lower(),
        ),
        reverse=True,
    )


def render_jobs(jobs: list["JobPosting"], min_score: int = 4) -> None:
    try:
        from rich.table import Table
    except ImportError:  # pragma: no cover - used before dependencies are installed.
        Table = None  # type: ignore[assignment]

    groups = [
        ("🔥 Hot matches", [job for job in jobs if job.relevance_score >= 8]),
        ("💼 Good fits", [job for job in jobs if 6 <= job.relevance_score <= 7]),
        ("👀 Worth checking", [job for job in jobs if 4 <= job.relevance_score <= 5]),
    ]
    if min_score < 4:
        groups.append(("🧪 Low-signal but scraped", [job for job in jobs if 0 <= job.relevance_score <= 3]))
    if not any(items for _, items in groups):
        console.print("No matches above the current filters yet.")
        return
    for label, items in groups:
        if not items:
            continue
        if Table is None:
            console.print(label)
            for job in items:
                console.print(
                    f"- [{job.relevance_score}] {job.title} | {job.company} | {job.location or job.workplace} | "
                    f"{job.contract_type or '-'} | {job.application_url}"
                )
            continue
        table = Table(title=label, show_lines=False)
        table.add_column("Score", justify="center")
        table.add_column("Title", overflow="fold")
        table.add_column("Company")
        table.add_column("Location")
        table.add_column("Contract")
        table.add_column("Skills", overflow="fold")
        table.add_column("Posted")
        table.add_column("Apply", overflow="fold")
        for job in items:
            if job.relevance_score >= 8:
                badge = "[green]🟢 {0}[/green]".format(job.relevance_score)
            elif job.relevance_score >= 6:
                badge = "[yellow]🟡 {0}[/yellow]".format(job.relevance_score)
            else:
                badge = "[red]🔴 {0}[/red]".format(job.relevance_score)
            table.add_row(
                badge,
                _truncate(job.title, 45),
                _truncate(job.company, 22),
                _truncate(job.location or job.workplace, 24),
                job.contract_type or "-",
                _truncate(", ".join(job.matching_skills) or ", ".join(job.required_skills) or "-", 35),
                _format_date(job.date_posted),
                _truncate(job.application_url, 42),
            )
        console.print(table)


def render_template(job) -> None:
    template = f"""
Cover Letter Template

Subject: Application for {job.title} at {job.company}

Dear Hiring Team,

I am applying for the {job.title} role at {job.company}. I am a student at 1337 School (42 Network, Khouribga) and a former Full Stack Engineering intern at UM6P. My background aligns especially well with the technologies mentioned in your role, including {", ".join(job.matching_skills or job.required_skills[:5] or ['modern web development'])}.

I am comfortable working in French, Arabic, and English, and I am particularly motivated by roles that value practical problem-solving, autonomy, and continuous learning. Your opportunity stands out because it combines {job.workplace} collaboration with hands-on software development that matches my junior profile.

I would be glad to discuss how I can contribute quickly and keep learning with your team.

Best regards,
[Your Name]
"""
    console.print(template.strip())


async def run_scan(options, cache) -> list["JobPosting"]:
    from .config import DEFAULT_PROFILE, SearchPlanner
    from .sites import build_registry

    planner = SearchPlanner(DEFAULT_PROFILE, options.keywords_override)
    registry = build_registry()
    scrapers = [registry[name](DEFAULT_PROFILE, cache) for name in options.sites if name in registry]
    scan_mode = "deep scan" if options.deep_scan else "standard scan"
    console.print(f"Scanning {len(scrapers)} sources with {scan_mode}...")

    async def run_one(scraper):
        started_at = time.perf_counter()
        try:
            result = await asyncio.wait_for(scraper.scrape(planner, options), timeout=SOURCE_TIMEOUT_SECONDS)
            elapsed = time.perf_counter() - started_at
            return scraper.name, result, elapsed, None
        except Exception as exc:
            elapsed = time.perf_counter() - started_at
            return scraper.name, [], elapsed, exc

    tasks = [asyncio.create_task(run_one(scraper)) for scraper in scrapers]

    collected: list["JobPosting"] = []
    completed = 0
    for task in asyncio.as_completed(tasks):
        source_name, result, elapsed, exc = await task
        completed += 1
        if exc is not None:
            console.print(
                f"[{completed}/{len(scrapers)}] {source_name}: skipped after {elapsed:.1f}s "
                f"({_format_exception(exc)})"
            )
            continue
        console.print(f"[{completed}/{len(scrapers)}] {source_name}: {len(result)} jobs in {elapsed:.1f}s")
        collected.extend(result)

    filtered = score_and_filter(collected, options)
    return filtered


def export_if_needed(jobs: list["JobPosting"], options) -> None:
    from .exporter import export_jobs

    if not options.export_formats:
        return
    written = export_jobs(jobs, options.export_formats)
    if written:
        console.print("Exports:", ", ".join(str(path) for path in written))


def mark_new_jobs(cache, jobs: list["JobPosting"]) -> list["JobPosting"]:
    new_jobs: list["JobPosting"] = []
    for job in jobs:
        if cache.mark_job_seen(job):
            new_jobs.append(job)
    return new_jobs


def run_once(options: SearchOptions) -> list[JobPosting]:
    from .cache import SQLiteCache
    from .notifier import notify, render_summary

    cache = SQLiteCache()
    console.print("Starting job scan...")
    jobs = asyncio.run(run_scan(options, cache))
    render_jobs(jobs, options.min_score)
    render_summary(console, jobs)
    export_if_needed(jobs, options)
    if options.notify:
        notify(console, jobs)
    if options.apply_template and jobs:
        render_template(jobs[0])
    return mark_new_jobs(cache, jobs)


def watch_mode(options: SearchOptions) -> None:
    from .config import DEFAULT_WATCH_HOURS

    try:
        import schedule
    except ImportError:  # pragma: no cover - fallback if deps are not installed yet.
        console.print("`schedule` is not installed, falling back to a simple 6h loop.")
        while True:
            new_jobs = run_once(options)
            if new_jobs:
                console.print(f"New jobs found: {len(new_jobs)}")
            time.sleep(DEFAULT_WATCH_HOURS * 60 * 60)

    def job() -> None:
        new_jobs = run_once(options)
        if new_jobs:
            console.print(f"New jobs found: {len(new_jobs)}")

    job()
    schedule.every(DEFAULT_WATCH_HOURS).hours.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    missing = _missing_core_dependencies()
    if missing:
        console.print(
            "Missing runtime dependencies: {deps}\nInstall them with: pip install -r requirements.txt".format(
                deps=", ".join(missing)
            )
        )
        return 1
    options = build_options(args)
    if options.watch:
        watch_mode(options)
        return 0
    run_once(options)
    return 0


def _truncate(value: str, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _format_date(value) -> str:
    return value.isoformat() if value else "-"


def _missing_core_dependencies() -> list[str]:
    missing: list[str] = []
    for package_name, import_name in (("requests", "requests"), ("beautifulsoup4", "bs4")):
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    return missing


def _format_exception(exc: Exception) -> str:
    message = " ".join(str(exc).split())
    if "Executable doesn't exist" in message and "playwright" in message.lower():
        return "Playwright browser missing; run '.venv/bin/python -m playwright install chromium'"
    if message:
        return f"{type(exc).__name__}: {_truncate(message, 120)}"
    return type(exc).__name__


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
