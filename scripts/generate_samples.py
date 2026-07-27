import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_email_sample():
    email_content = """From: dr.sarah.jenkins@stjudehospital.org
To: quality.complaints@pharma-corp.com
Subject: URGENT: Product Quality Defect & Adverse Event Report - CardioShield 10mg (Lot LOT-9921A)
Date: Mon, 27 Jul 2026 14:15:00 -0400

Dear Quality Assurance & Regulatory Affairs Director,

I am writing to log an urgent product quality complaint and adverse event notification regarding CardioShield (Enalapril Maleate) 10mg Oral Tablets, Finished Dosage Form (FDF), NDC 0006-0074-31, Lot Number LOT-9921A, Expiration Date 2027-11-30.

BACKGROUND & DEFECT DESCRIPTION:
During routine unit-dose dispensing today at St. Jude Hospital Pharmacy, clinical pharmacy staff discovered visible black specks and dark particulate discoloration embedded inside sealed blister foil cavities. 

ADVERSE EVENT REPORT:
One hospitalized patient in Ward 4B reported acute nausea shortly after consuming a 10mg dose from this lot earlier today before pharmacy staff identified the batch defect.

FACILITY & COMPLAINANT INFORMATION:
- Complainant Name: Dr. Sarah Jenkins, PharmD
- Role: Clinical Director of Pharmacy Services
- Facility: St. Jude Hospital Pharmacy, Chicago, IL
- Direct Line: +1-555-019-2831
- Email: dr.sarah.jenkins@stjudehospital.org

ACTION TAKEN:
We have placed all remaining inventory of Lot LOT-9921A (15 bottles / 1,500 tablets) into quarantined cold storage under physical lock and key. Retained samples are prepared for your laboratory analytical testing upon request.

Please acknowledge receipt of this complaint and provide instructions for submitting FDA 15-day alert documentation.

Sincerely,
Dr. Sarah Jenkins, PharmD
Clinical Director of Pharmacy Services
St. Jude Hospital
"""
    output_path = os.path.join(os.path.dirname(__file__), "../samples/complaint_email_1.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(email_content)
    print(f"Generated text email sample: {output_path}")


def generate_pdf_sample():
    pdf_path = os.path.join(os.path.dirname(__file__), "../samples/complaint_letter_1.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0f2b48'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=10
    )
    bold_style = ParagraphStyle(
        'DocBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = [
        Paragraph("METROPOLITAN HEALTH SYSTEM - FORMAL DRUG DEFECT REPORT", title_style),
        Paragraph("Department of Quality Assurance & Sterile Compounding Inspection", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0ea5e9'), spaceAfter=15),
        
        Paragraph("<b>DATE:</b> July 27, 2026", body_style),
        Paragraph("<b>TO:</b> Global Regulatory Affairs & Quality Compliance Division", body_style),
        Paragraph("<b>SUBJECT:</b> Formal Product Quality Complaint - NeuroCalm Injectable Solution USP", body_style),
        Spacer(1, 10),
        
        Paragraph("<b>1. PRODUCT IDENTIFICATION DETAILS</b>", bold_style),
        Paragraph("<b>Product Name:</b> NeuroCalm Injection (Diazepam Injection USP)<br/>"
                  "<b>Dosage Form & Strength:</b> Parenteral Solution, 5mg/mL<br/>"
                  "<b>Batch / Lot Number:</b> BATCH-88402X<br/>"
                  "<b>National Drug Code (NDC):</b> 55150-123-10<br/>"
                  "<b>Manufacture Date:</b> 2025-06-10 | <b>Expiration Date:</b> 2026-12-31<br/>"
                  "<b>Affected Quantity:</b> 2 cartons / 10 glass ampoules", body_style),
        Spacer(1, 10),

        Paragraph("<b>2. DEFECT NARRATIVE & QUALITY DEVIATION</b>", bold_style),
        Paragraph("Upon opening outer corrugated shipment packaging at Metropolitan Central Hospital Pharmacy, "
                  "inspection personnel identified hairline glass cracks along the neck constriction of two intact 5mg/mL ampoules. "
                  "Fluid leakage was observed inside the plastic tray liner, compromising container closure integrity and sterile assurance.", body_style),
        Spacer(1, 10),

        Paragraph("<b>3. COMPLAINANT METADATA</b>", bold_style),
        Paragraph("<b>Reporting Official:</b> Mark Stevens, Lead Quality Inspector<br/>"
                  "<b>Facility:</b> Metropolitan Central Hospital Pharmacy<br/>"
                  "<b>Contact Email:</b> m.stevens@metrohealth.org | <b>Phone:</b> (555) 234-5678", body_style),
        Spacer(1, 10),

        Paragraph("<b>4. SAFETY RISK EVALUATION</b>", bold_style),
        Paragraph("Sterility breach in parenteral injectable preparations constitutes a Class I FDA Recall hazard due to potential microbial proliferation or glass particulate injection risks. Physical samples have been isolated in protective secondary container.", body_style),
        Spacer(1, 15),

        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=10),
        Paragraph("<i>Report Generated via AIVOA Pharmaceutical Complaint Intake System</i>", subtitle_style)
    ]

    doc.build(story)
    print(f"Generated PDF sample: {pdf_path}")


if __name__ == "__main__":
    generate_email_sample()
    generate_pdf_sample()
