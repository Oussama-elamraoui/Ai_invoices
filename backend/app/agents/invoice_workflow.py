from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from app.agents.extraction_agent import extract_invoice
from app.agents.validation_agent import validate_invoice
from app.agents.reconciliation_agent import reconcile_invoice
from app.agents.correction_agent import suggest_corrections


class InvoiceState(TypedDict, total=False):
    file_path: str
    invoice_data: dict[str, Any]
    validation_errors: list[str]
    reconciliation: dict[str, Any]
    correction_suggestions: dict[str, Any]


async def extraction_node(state: InvoiceState):
    data = await extract_invoice(state["file_path"])
    return {"invoice_data": data}


def validation_node(state: InvoiceState):
    errors = validate_invoice(state["invoice_data"])
    return {"validation_errors": errors}


def reconciliation_node(state: InvoiceState):
    result = reconcile_invoice(state["invoice_data"])
    return {"reconciliation": result}


def route_after_checks(state: InvoiceState):
    errors = state.get("validation_errors", [])
    errors += state.get("reconciliation", {}).get("errors", [])

    return "correct" if errors else "finish"


async def correction_node(state: InvoiceState):
    errors = state.get("validation_errors", [])
    errors += state.get("reconciliation", {}).get("errors", [])

    suggestions = await suggest_corrections(
        state["invoice_data"],
        errors,
    )

    return {"correction_suggestions": suggestions}


builder = StateGraph(InvoiceState)

builder.add_node("extract", extraction_node)
builder.add_node("validate", validation_node)
builder.add_node("reconcile", reconciliation_node)
builder.add_node("correct", correction_node)

builder.add_edge(START, "extract")
builder.add_edge("extract", "validate")
builder.add_edge("validate", "reconcile")

builder.add_conditional_edges(
    "reconcile",
    route_after_checks,
    {
        "correct": "correct",
        "finish": END,
    },
)

builder.add_edge("correct", END)

invoice_workflow = builder.compile()