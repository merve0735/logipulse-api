from io import BytesIO
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.models.dashboard import RouteSummary
from app.models.report import SustainabilityReport


def _route_summary_text(route_summary: Optional[RouteSummary]) -> str:
    if route_summary is None:
        return "N/A"
    return f"{route_summary.name} ({route_summary.vehicle_plate_number}) — {route_summary.estimated_profit} TL"


def build_sustainability_report_pdf(report: SustainabilityReport) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(report.report_title, styles["Title"]))
    elements.append(Paragraph(f"Generated at: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Executive Summary", styles["Heading2"]))
    elements.append(Paragraph(report.executive_summary, styles["Normal"]))
    elements.append(Spacer(1, 14))

    fin = report.financial_summary
    elements.append(Paragraph("Financial Summary", styles["Heading2"]))
    elements.append(Paragraph(f"Total Expected Revenue: {fin.total_expected_revenue} TL", styles["Normal"]))
    elements.append(Paragraph(f"Total Estimated Cost: {fin.total_estimated_cost} TL", styles["Normal"]))
    elements.append(Paragraph(f"Total Estimated Profit: {fin.total_estimated_profit} TL", styles["Normal"]))
    elements.append(Paragraph(f"Average Profit Per Route: {fin.average_profit_per_route} TL", styles["Normal"]))
    elements.append(Paragraph(f"Most Profitable Route: {_route_summary_text(fin.most_profitable_route)}", styles["Normal"]))
    elements.append(Paragraph(f"Least Profitable Route: {_route_summary_text(fin.least_profitable_route)}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    carbon = report.carbon_summary
    elements.append(Paragraph("Carbon Summary", styles["Heading2"]))
    elements.append(Paragraph(f"Total Estimated Carbon KG: {carbon.total_estimated_carbon_kg}", styles["Normal"]))
    elements.append(Paragraph(f"Average Carbon Per Route: {carbon.average_carbon_per_route}", styles["Normal"]))
    elements.append(Paragraph(f"Electric Route Count: {carbon.electric_route_count}", styles["Normal"]))
    elements.append(Paragraph(f"Diesel Route Count: {carbon.diesel_route_count}", styles["Normal"]))
    elements.append(Paragraph(f"Motorcycle Route Count: {carbon.motorcycle_route_count}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    risk = report.risk_summary
    elements.append(Paragraph("Risk Summary", styles["Heading2"]))
    elements.append(Paragraph(f"Total Alert Count: {risk.total_alert_count}", styles["Normal"]))
    elements.append(Paragraph(f"High Alert Count: {risk.high_alert_count}", styles["Normal"]))
    elements.append(Paragraph(f"Medium Alert Count: {risk.medium_alert_count}", styles["Normal"]))
    elements.append(Paragraph(f"Low Alert Count: {risk.low_alert_count}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    rec = report.recommendation_summary
    elements.append(Paragraph("Recommendation Summary", styles["Heading2"]))
    elements.append(Paragraph(f"Total Recommendation Count: {rec.total_recommendation_count}", styles["Normal"]))
    elements.append(Paragraph(f"High Priority Count: {rec.high_priority_count}", styles["Normal"]))
    elements.append(Paragraph(f"Medium Priority Count: {rec.medium_priority_count}", styles["Normal"]))
    elements.append(Paragraph(f"Low Priority Count: {rec.low_priority_count}", styles["Normal"]))
    if rec.recommendations:
        for item in rec.recommendations:
            elements.append(Paragraph(f"• {item.title}", styles["Normal"]))
    else:
        elements.append(Paragraph("No active recommendations.", styles["Normal"]))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Business Comment", styles["Heading2"]))
    elements.append(Paragraph(report.business_comment, styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()
