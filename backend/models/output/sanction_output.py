from typing import List, Literal
from pydantic import BaseModel, Field


class SanctionLetter(BaseModel):
    letter_number: str

    generated_date: str

    content: str

    format: Literal[
        "text",
        "markdown",
        "html"
    ]

    sections_included: List[str] = Field(default_factory=list)

    missing_optional_fields: List[str] = Field(default_factory=list)


class SanctionLetterOutput(BaseModel):
    task_id: str

    agent: Literal["sanction_letter_agent"]

    status: Literal[
        "success",
        "failed",
        "missing_fields"
    ]

    sanction_letter: SanctionLetter

    pdf_ready: bool

    reasoning: str

    errors: List[str] = Field(default_factory=list)