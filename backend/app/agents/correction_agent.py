from app.core.config import settings
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class CorrectionResult(BaseModel):
    corrected_data: dict = Field(
        description="Invoice data with only safe corrections applied"
    )
    unresolved_issues: list[str] = Field(default_factory=list)


async def suggest_corrections(
    invoice_data: dict,
    errors: list[str],
) -> dict:
    if (
        settings.OPENAI_API_KEY is None
        or not settings.OPENAI_API_KEY.get_secret_value().strip()
    ):
        raise RuntimeError(
            "Set OPENAI_API_KEY in .env before requesting corrections."
        )

    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        model=settings.OPENAI_MODEL,
        temperature=0,
    ).with_structured_output(CorrectionResult)

    result = await llm.ainvoke([
        {
            "role": "system",
            "content": """
You are an invoice data correction agent.

Rules:
- Never invent missing information.
- Never guess quantities, prices, taxes, dates, or invoice numbers.
- Preserve original values unless a correction is clearly supported
  by the provided data.
- Do not change supplier or client IDs.
- List uncertain issues in unresolved_issues.
- Return corrected_data and unresolved_issues.
"""
        },
        {
            "role": "user",
            "content": (
                f"Invoice data: {invoice_data}\n"
                f"Validation errors: {errors}"
            ),
        },
    ])

    return result.model_dump()