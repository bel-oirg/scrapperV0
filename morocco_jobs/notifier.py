from __future__ import annotations

from collections import Counter
from datetime import date

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:  # pragma: no cover - used before dependencies are installed.
    Console = object  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]

from .models import JobPosting, ScanSummary


def build_summary(jobs: list[JobPosting]) -> ScanSummary:
    location_counts = Counter()
    workplace_counts = Counter(job.workplace for job in jobs)
    for job in jobs:
        location = (job.location or "").lower()
        if "casablanca" in location:
            location_counts["casablanca"] += 1
        elif "rabat" in location:
            location_counts["rabat"] += 1
        else:
            location_counts["other"] += 1

    today = date.today()
    last_7_days = sum(1 for job in jobs if job.date_posted and (today - job.date_posted).days <= 7)
    last_30_days = sum(1 for job in jobs if job.date_posted and (today - job.date_posted).days <= 30)
    sources = {job.source for job in jobs}

    return ScanSummary(
        total_jobs=len(jobs),
        total_sources=len(sources),
        remote_jobs=workplace_counts.get("remote", 0),
        hybrid_jobs=workplace_counts.get("hybrid", 0),
        onsite_jobs=workplace_counts.get("onsite", 0),
        casablanca_jobs=location_counts.get("casablanca", 0),
        rabat_jobs=location_counts.get("rabat", 0),
        other_jobs=location_counts.get("other", 0),
        last_7_days=last_7_days,
        last_30_days=last_30_days,
    )


def render_summary(console: Console, jobs: list[JobPosting]) -> None:
    summary = build_summary(jobs)
    if Table is None or Panel is None:
        console.print(f"✅ Jobs found: {summary.total_jobs} across {summary.total_sources} sources")
        console.print(
            f"🌍 Remote / Hybrid / Onsite: {summary.remote_jobs} / {summary.hybrid_jobs} / {summary.onsite_jobs}"
        )
        console.print(
            f"📍 Casablanca / Rabat / Other: {summary.casablanca_jobs} / {summary.rabat_jobs} / {summary.other_jobs}"
        )
        console.print(f"📅 Last 7 days / Last 30 days: {summary.last_7_days} / {summary.last_30_days}")
        return
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_row("✅ Jobs found", f"{summary.total_jobs} across {summary.total_sources} sources")
    table.add_row("🌍 Remote / Hybrid / Onsite", f"{summary.remote_jobs} / {summary.hybrid_jobs} / {summary.onsite_jobs}")
    table.add_row("📍 Casablanca / Rabat / Other", f"{summary.casablanca_jobs} / {summary.rabat_jobs} / {summary.other_jobs}")
    table.add_row("📅 Last 7 days / Last 30 days", f"{summary.last_7_days} / {summary.last_30_days}")
    console.print(Panel(table, title="Scan Summary", border_style="cyan"))


def notify(console: Console, jobs: list[JobPosting]) -> None:
    print("\a", end="")
