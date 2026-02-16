import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "UArizona Help Desk Bot")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    database_path: str = os.getenv("DATABASE_PATH", "helpdesk_tickets.db")
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "helpdesk_audit.log")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    mongo_uri: str = os.getenv("MONGO_URI", "")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "helpdesk")
    mongo_kb_collection: str = os.getenv("MONGO_KB_COLLECTION", "kb_documents")

    servicenow_instance_url: str = os.getenv("SERVICENOW_INSTANCE_URL", "")
    servicenow_username: str = os.getenv("SERVICENOW_USERNAME", "")
    servicenow_password: str = os.getenv("SERVICENOW_PASSWORD", "")
    servicenow_incident_table: str = os.getenv("SERVICENOW_INCIDENT_TABLE", "incident")


settings = Settings()
