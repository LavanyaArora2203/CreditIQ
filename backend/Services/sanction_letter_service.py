import os
from datetime import datetime

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Table,
    TableStyle,
)
from pathlib import Path
from reportlab.lib import colors

# OUTPUT_FOLDER = "GeneratedLetters"
OUTPUT_FOLDER = Path(__file__).resolve().parent.parent / "GeneratedLetters"


def generate_sanction_letter(
    customer_name: str,
    customer_id: str,
    loan_amount: float,
    tenure_months: int,
    interest_rate: float,
    emi: float,
    decision_date: str | None = None,
):
    """
    Generates a loan sanction letter PDF.

    Returns
    -------
    dict
        {
            "status": "success",
            "pdf_path": "GeneratedLetters/CUST001_LoanSanction.pdf"
        }
    """

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if decision_date is None:
        decision_date = datetime.now().strftime("%d-%m-%Y")

    pdf_path = os.path.join(
        OUTPUT_FOLDER,
        f"{customer_id}_LoanSanction.pdf"
    )

    doc = SimpleDocTemplate(
        pdf_path,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    reference_number = f"REF-{customer_id}-{datetime.now().strftime('%Y%m%d')}"

    formatted_date = datetime.now().strftime("%d %B %Y")

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = HexColor("#003366")

    heading_style = styles["Heading2"]
    heading_style.textColor = HexColor("#003366")

    normal_style = styles["BodyText"]

    story = []

    # -------------------------------------------------
    # Bank Header
    # -------------------------------------------------

    story.append(
        Paragraph(
            "<font size=22 color='#003366'><b>ABC BANK</b></font>",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "<font size=10>Your Trusted Banking Partner</font>",
            normal_style,
        )
    )

    story.append(Spacer(1, 0.15 * inch))

    story.append(
        Paragraph(
            f"<b>Reference No:</b> {reference_number}",
            normal_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> {formatted_date}",
            normal_style,
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------
    # Letter Title
    # -------------------------------------------------

    story.append(
        Paragraph(
            "<b>LOAN SANCTION LETTER</b>",
            title_style
        )
    )

    story.append(Spacer(1, 0.35 * inch))

    # -------------------------------------------------
    # Customer Details
    # -------------------------------------------------
    loan_table_data = [
        ["Customer Name", customer_name],
        ["Customer ID", customer_id],
        ["Loan Amount", f"₹ {loan_amount:,.2f}"],
        ["Interest Rate", f"{interest_rate}%"],
        ["Loan Tenure", f"{tenure_months} Months"],
        ["Monthly EMI", f"₹ {emi:,.2f}"],
        ["Approval Date", decision_date],
    ]
    loan_table = Table(
        loan_table_data,
        colWidths=[180, 260],
    )

    loan_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D6EAF8")),
            ]
        )
    )

    story.append(loan_table)
    story.append(Spacer(1, 0.30 * inch))



    # -------------------------------------------------
    # Approval Statement
    # -------------------------------------------------

    story.append(
        Paragraph(
            """
            Dear Customer,

            <br/><br/>

            Congratulations!

            <br/><br/>

            Based on the assessment of your application and successful completion
            of our credit evaluation process, ABC Bank is pleased to sanction
            your requested personal loan under the terms mentioned below.

            <br/><br/>

            Kindly review the details carefully before accepting the loan offer.
            """,
            normal_style,
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------
    # Terms & Conditions
    # -------------------------------------------------

    story.append(
        Paragraph(
            "<font color='#003366'><b>Terms & Conditions</b></font>",
            heading_style,
        )
    )

    terms = [
        "• EMI must be paid on or before the due date every month.",
        "• Delay in payment may attract penal interest as per bank policy.",
        "• Loan may be recalled in case of fraud or document mismatch.",
        "• Foreclosure charges may apply as per prevailing banking norms.",
        "• Bank reserves the right to revise applicable policies.",
    ]

    for term in terms:
        story.append(Paragraph(term, normal_style))

    story.append(Spacer(1, 0.60 * inch))

    # -------------------------------------------------
    # Signature
    # -------------------------------------------------
    story.append(Spacer(1, 0.55 * inch))

    story.append(
        Paragraph(
            "<b>For ABC BANK</b>",
            normal_style,
        )
    )

    story.append(Spacer(1, 0.35 * inch))

    story.append(
        Paragraph(
            "<b>Authorized Signatory</b>",
            normal_style,
        )
    )

    story.append(
        Paragraph(
            "Retail Loan Department",
            normal_style,
        )
    )

# Optional footer
    story.append(Spacer(1, 0.5 * inch))

    story.append(
        Paragraph(
            "<font size=8 color='grey'>"
            "This is a system-generated sanction letter and does not require a physical signature."
            "</font>",
            normal_style,
        )
    )

# Build PDF
    doc.build(story)

# Return result
    return {
        "status": "success",
        "pdf_path": pdf_path,
    }



##before doccbuild(story)
# story.append(Spacer(1, 0.5 * inch))

# story.append(
#     Paragraph(
#         "<font size=8 color='grey'>"
#         "This is a system-generated sanction letter and does not require a physical signature."
#         "</font>",
#         normal_style,
#     )
# )
