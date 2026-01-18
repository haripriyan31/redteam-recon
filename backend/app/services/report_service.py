from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import io
from typing import Dict, Any

class ReportService:
    @staticmethod
    def generate_pdf_report(scan_data: Dict[str, Any]) -> bytes:
        """
        Generates a PDF Executive Summary report.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = styles["Title"]
        story.append(Paragraph(f"Red Team Recon Report: {scan_data.get('domain', 'Unknown')}", title_style))
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        score = scan_data.get("attack_score", 0)
        risk_level = "Low"
        if score > 20: risk_level = "Medium"
        if score > 50: risk_level = "High"
        if score > 80: risk_level = "Critical"
        
        summary_text = f"""
        <b>Target:</b> {scan_data.get('domain')} <br/>
        <b>Scan Date:</b> {scan_data.get('timestamp')} <br/>
        <b>Attack Surface Score:</b> {score} / 100 <br/>
        <b>Risk Level:</b> {risk_level}
        """
        story.append(Paragraph(summary_text, styles["Normal"]))
        story.append(Spacer(1, 24))

        # Findings Summary Table
        story.append(Paragraph("Findings Overview", styles["Heading3"]))
        data = [
            ["Category", "Count"],
            ["Subdomains", len(scan_data.get("subdomains", {}).get("subdomains", []))],
            ["Open Ports", sum(len(p.get("ports", [])) for p in scan_data.get("ports", []))],
            ["OSINT Artifacts", len(scan_data.get("osint_data", []))],
            ["Vulnerabilities", len(scan_data.get("vulnerabilities", []))],
        ]
        t = Table(data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(t)
        story.append(Spacer(1, 24))

        # Vulnerabilities
        if scan_data.get("vulnerabilities"):
            story.append(Paragraph("Identified Vulnerabilities", styles["Heading3"]))
            for vuln in scan_data.get("vulnerabilities", []):
                story.append(Paragraph(f"• {vuln}", styles["Normal"]))
                story.append(Spacer(1, 6))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()
