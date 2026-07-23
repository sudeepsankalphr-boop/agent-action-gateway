from fastapi import APIRouter
from app.models.audit import AuditRecord
from app.services.audit_service import read_audit_records

router = APIRouter()


@router.get("/audit", response_model=list[AuditRecord])
def list_audit_records() -> list[AuditRecord]:
    return read_audit_records()
