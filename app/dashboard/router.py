from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.services.audit_service import read_audit_records

router = APIRouter()
_env = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
    autoescape=True,
)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    records = read_audit_records()
    html = _env.get_template("index.html").render(records=records)
    return HTMLResponse(content=html)
