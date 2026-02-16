import json
from typing import Dict

from openai import OpenAI

from .config import settings
from .kb import KEYWORD_TO_CATEGORY, TROUBLESHOOTING_PLAYBOOK
from .retrieval import retrieve_context


def classify_category(issue_text: str) -> str:
    normalized = issue_text.lower()
    for keyword, category in KEYWORD_TO_CATEGORY.items():
        if keyword in normalized:
            return category
    return "general"


def infer_priority(issue_text: str) -> str:
    normalized = issue_text.lower()
    high_signals = ["cannot access", "locked out", "security", "breach", "deadline", "exam", "outage"]
    medium_signals = ["slow", "intermittent", "error", "failed"]

    if any(signal in normalized for signal in high_signals):
        return "high"
    if any(signal in normalized for signal in medium_signals):
        return "medium"
    return "low"


def build_system_prompt() -> str:
    return (
        "You are a university IT help desk assistant for UArizona. "
        "Provide concise, practical troubleshooting guidance for common student/faculty issues "
        "(login, MFA, VPN/firewall, wifi, email, LMS). "
        "Never claim to have performed actions. "
        "If uncertain, say what to verify next and when to escalate. "
        "Output strict JSON with keys: "
        "response_text (string), solved (boolean), confidence (number 0 to 1), "
        "recommended_steps (array of strings)."
    )


def build_user_prompt(
    user_id: str,
    issue_text: str,
    category: str,
    retrieved_docs: list[dict],
    context: str | None = None,
) -> str:
    playbook_steps = TROUBLESHOOTING_PLAYBOOK.get(category, TROUBLESHOOTING_PLAYBOOK["general"])
    payload = {
        "user_id": user_id,
        "category": category,
        "issue_text": issue_text,
        "context": context or "",
        "known_best_steps": playbook_steps,
        "grounding_docs": retrieved_docs,
        "task": "Give immediate troubleshooting instructions and decide if likely solved.",
    }
    return json.dumps(payload)


def generate_help_response(user_id: str, issue_text: str, context: str | None = None) -> Dict:
    category = classify_category(issue_text)
    priority = infer_priority(issue_text)
    retrieved_docs = retrieve_context(issue_text, limit=3)

    if not settings.openai_api_key:
        fallback_steps = TROUBLESHOOTING_PLAYBOOK.get(category, TROUBLESHOOTING_PLAYBOOK["general"])
        confidence = 0.35
        escalated_to_human = confidence < settings.confidence_threshold
        return {
            "category": category,
            "priority": priority,
            "response_text": (
                "OpenAI API key is not configured. Here are recommended manual troubleshooting steps "
                f"for {category.replace('_', ' ')}."
            ),
            "solved": False if escalated_to_human else True,
            "confidence": confidence,
            "escalated_to_human": escalated_to_human,
            "retrieved_docs": retrieved_docs,
            "recommended_steps": fallback_steps[:4],
        }

    client = OpenAI(api_key=settings.openai_api_key)
    completion = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {
                "role": "user",
                "content": build_user_prompt(user_id, issue_text, category, retrieved_docs, context),
            },
        ],
    )

    raw = completion.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {}

    confidence = float(parsed.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))
    escalated_to_human = confidence < settings.confidence_threshold

    return {
        "category": category,
        "priority": priority,
        "response_text": parsed.get("response_text", "No response generated.") + (
            "\n\nEscalation note: Confidence is below threshold; routing to human support."
            if escalated_to_human
            else ""
        ),
        "solved": bool(parsed.get("solved", False)) and (not escalated_to_human),
        "confidence": confidence,
        "escalated_to_human": escalated_to_human,
        "retrieved_docs": retrieved_docs,
        "recommended_steps": parsed.get("recommended_steps", []),
    }
