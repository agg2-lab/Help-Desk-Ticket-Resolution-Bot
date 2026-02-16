from typing import Any

import httpx

from .config import settings


def service_now_enabled() -> bool:
    return bool(
        settings.servicenow_instance_url
        and settings.servicenow_username
        and settings.servicenow_password
    )


def create_servicenow_incident(
    short_description: str,
    description: str,
    category: str,
    priority: str,
    caller_id: str,
) -> dict[str, Any]:
    if not service_now_enabled():
        return {"created": False, "reason": "ServiceNow credentials are not configured"}

    url = (
        f"{settings.servicenow_instance_url.rstrip('/')}/api/now/table/"
        f"{settings.servicenow_incident_table}"
    )
    body = {
        "short_description": short_description,
        "description": description,
        "category": category,
        "priority": priority,
        "caller_id": caller_id,
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                url,
                auth=(settings.servicenow_username, settings.servicenow_password),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json=body,
            )
            response.raise_for_status()
            data = response.json().get("result", {})
            return {
                "created": True,
                "incident_number": data.get("number"),
                "sys_id": data.get("sys_id"),
            }
    except Exception as exc:
        return {"created": False, "reason": str(exc)}
