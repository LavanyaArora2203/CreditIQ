from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
from pathlib import Path
import uuid


class SanctionLetterInput(BaseModel):
    approved_data: Dict[str, Any] = Field(
        ...,
        description="Approved loan information received from the Master Agent."
    )


class SanctionLetterTool(BaseTool):
    name: str = "Personal Loan Sanction Letter Generator"

    description: str = (
        "Generates a professional Personal Loan Sanction Letter PDF "
        "using approved customer and loan information."
    )

    args_schema = SanctionLetterInput
    def _run(self, approved_data: Dict[str, Any]) -> str:

        sanction_number = (
        f"PL-{datetime.now().strftime('%Y%m%d')}-"
        f"{uuid.uuid4().hex[:6].upper()}"
    )

        output_dir = Path("generated_letters")
        output_dir.mkdir(exist_ok=True)

        pdf_path = output_dir / f"{sanction_number}.pdf"

        doc = SimpleDocTemplate(str(pdf_path))

        styles = getSampleStyleSheet()

        story = []

        story.append(
        Paragraph(
            "<b>PERSONAL LOAN SANCTION LETTER</b>",
            styles["Title"]
        )
    )

        story.append(Spacer(1, 0.3 * inch))

        story.append(
        Paragraph(
            f"<b>Sanction Number:</b> {sanction_number}",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d-%b-%Y')}",
            styles["Normal"]
        )
    )

        story.append(Spacer(1, 0.2 * inch))

        customer = approved_data["customer"]
        loan = approved_data["loan"]
        approval = approved_data["approval_summary"]
        credit = approved_data["credit_summary"]
        company = approved_data["company"]

        story.append(
        Paragraph(
            f"<b>Customer Name:</b> {customer.get('name','')}",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Customer ID:</b> {customer.get('customer_id','')}",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Loan Amount:</b> ₹ {loan.get('loan_amount','')}",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Interest Rate:</b> {loan.get('interest_rate','')} %",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Tenure:</b> {loan.get('tenure','')} Months",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Monthly EMI:</b> ₹ {approval.get('emi','')}",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Credit Score:</b> {credit.get('credit_score','')}",
            styles["Normal"]
        )
    )

        story.append(
        Paragraph(
            f"<b>Status:</b> {approval.get('decision','Approved')}",
            styles["Normal"]
        )
    )

        story.append(Spacer(1, 0.3 * inch))

        story.append(
        Paragraph(
            "Congratulations! Your Personal Loan has been approved.",
            styles["Heading2"]
        )
    )

        story.append(Spacer(1, 0.2 * inch))

        story.append(
        Paragraph(
            f"Thank you for choosing {company.get('name','Our Bank')}. "
            "Kindly sign the loan agreement to complete the disbursement process.",
            styles["Normal"]
        )
    )

        story.append(Spacer(1, 0.5 * inch))

        story.append(
        Paragraph(
            "<b>Authorized Signatory</b>",
            styles["Normal"]
        )
    )

        doc.build(story)

        return str(pdf_path)

    