from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from .models import JobPosting
from .notifier import build_summary


def export_jobs(jobs: list[JobPosting], formats: list[str], output_dir: str | Path = ".") -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if "csv" in formats:
        csv_path = output_path / "jobs.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(jobs[0].to_record().keys()) if jobs else ["title"])
            writer.writeheader()
            for job in jobs:
                writer.writerow(job.to_record())
        written.append(csv_path)

    if "json" in formats:
        json_path = output_path / "jobs.json"
        json_path.write_text(
            json.dumps([job.to_record() for job in jobs], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written.append(json_path)

    if "md" in formats:
        md_path = output_path / "jobs.md"
        groups: dict[str, list[JobPosting]] = defaultdict(list)
        for job in jobs:
            if job.relevance_score >= 8:
                groups["Hot matches"].append(job)
            elif job.relevance_score >= 6:
                groups["Good fits"].append(job)
            else:
                groups["Worth checking"].append(job)

        summary = build_summary(jobs)
        lines = [
            "# Morocco Jobs Report",
            "",
            f"- Jobs found: **{summary.total_jobs}** across **{summary.total_sources}** sources",
            f"- Remote / Hybrid / Onsite: **{summary.remote_jobs} / {summary.hybrid_jobs} / {summary.onsite_jobs}**",
            f"- Casablanca / Rabat / Other: **{summary.casablanca_jobs} / {summary.rabat_jobs} / {summary.other_jobs}**",
            f"- Last 7 days / Last 30 days: **{summary.last_7_days} / {summary.last_30_days}**",
            "",
        ]
        for label in ("Hot matches", "Good fits", "Worth checking"):
            items = groups.get(label, [])
            if not items:
                continue
            lines.extend([f"## {label}", "", "| Score | Title | Company | Location | Contract | Matching skills | Why you're a fit | Apply |", "| --- | --- | --- | --- | --- | --- | --- | --- |"])
            for job in items:
                lines.append(
                    "| {score} | {title} | {company} | {location} | {contract} | {skills} | {fit} | [Apply]({url}) |".format(
                        score=job.relevance_score,
                        title=job.title.replace("|", "/"),
                        company=job.company.replace("|", "/"),
                        location=(job.location or job.workplace).replace("|", "/"),
                        contract=(job.contract_type or "-").replace("|", "/"),
                        skills=", ".join(job.matching_skills) or "-",
                        fit=job.why_fit.replace("|", "/") if job.why_fit else "-",
                        url=job.application_url,
                    )
                )
            lines.extend(["", ""])
        md_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        written.append(md_path)

    return written
