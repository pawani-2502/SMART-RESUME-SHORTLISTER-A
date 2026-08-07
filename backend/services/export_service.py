"""Export System - PDF, CSV, Excel, JSON."""

import json
import io
import csv
from datetime import datetime
from typing import Any

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def export_json(rankings: list[dict], job: dict) -> bytes:
    data = {
        "exported_at": datetime.utcnow().isoformat(),
        "job": {"id": str(job.get("id")), "title": job.get("title")},
        "rankings": rankings,
    }
    return json.dumps(data, indent=2, default=str).encode("utf-8")


def export_csv(rankings: list[dict], job: dict) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate", "Final Score", "Confidence", "Eligibility",
        "Semantic Fit", "Skill Coverage", "Career Trajectory", "Must-Have Coverage",
        "Interview Readiness", "Human Review", "Strengths", "Weaknesses", "Explanation",
    ])
    for r in rankings:
        writer.writerow([
            r.get("rank", "N/A"),
            r.get("candidate_name", r.get("candidate_id", "")),
            r.get("final_score", 0),
            r.get("confidence_level", ""),
            r.get("eligibility_status", ""),
            r.get("semantic_fit", 0),
            r.get("skill_coverage", 0),
            r.get("career_trajectory", 0),
            r.get("must_have_coverage", 0),
            r.get("interview_readiness", 0),
            "Yes" if r.get("human_review_required") else "No",
            "; ".join(r.get("strengths", [])[:3]),
            "; ".join(r.get("weaknesses", [])[:3]),
            r.get("explanation", "")[:500],
        ])
    return output.getvalue().encode("utf-8")


def export_excel(rankings: list[dict], job: dict) -> bytes:
    if not HAS_PANDAS:
        return export_csv(rankings, job)

    rows = []
    for r in rankings:
        rows.append({
            "Rank": r.get("rank"),
            "Candidate": r.get("candidate_name", r.get("candidate_id")),
            "Final Score": r.get("final_score"),
            "Confidence": r.get("confidence_level"),
            "Eligibility": r.get("eligibility_status"),
            "Semantic Fit": r.get("semantic_fit"),
            "Skill Coverage": r.get("skill_coverage"),
            "Career Trajectory": r.get("career_trajectory"),
            "Must-Have Coverage": r.get("must_have_coverage"),
            "Interview Readiness": r.get("interview_readiness"),
            "Human Review": r.get("human_review_required"),
            "Explanation": r.get("explanation", ""),
        })

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Shortlist")
    return buffer.getvalue()


def export_pdf(rankings: list[dict], job: dict) -> bytes:
    if not HAS_REPORTLAB:
        return export_csv(rankings, job)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Shortlist Report: {job.get('title', 'Job')}", styles["Title"]))
    elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    table_data = [["Rank", "Candidate", "Score", "Confidence", "Status"]]
    for r in rankings[:50]:
        table_data.append([
            str(r.get("rank", "N/A")),
            str(r.get("candidate_name", ""))[:30],
            f"{r.get('final_score', 0):.0%}",
            r.get("confidence_level", ""),
            r.get("eligibility_status", ""),
        ])

    table = Table(table_data, colWidths=[40, 150, 60, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
    ]))
    elements.append(table)

    for r in rankings[:10]:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(
            f"#{r.get('rank')} {r.get('candidate_name', 'Candidate')} — {r.get('final_score', 0):.0%}",
            styles["Heading2"],
        ))
        if r.get("explanation"):
            elements.append(Paragraph(r["explanation"][:500], styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


def export_shortlist(rankings: list[dict], job: dict, format: str) -> tuple[bytes, str, str]:
    exporters = {
        "json": (export_json, "application/json", "shortlist.json"),
        "csv": (export_csv, "text/csv", "shortlist.csv"),
        "excel": (export_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "shortlist.xlsx"),
        "pdf": (export_pdf, "application/pdf", "shortlist.pdf"),
    }
    fn, mime, filename = exporters.get(format, exporters["json"])
    return fn(rankings, job), mime, filename
