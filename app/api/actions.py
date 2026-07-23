from fastapi import APIRouter
from app.models.action import ActionRequest, ActionDecisionResponse
from app.services.action_service import process_action

router = APIRouter()


@router.post("/actions", response_model=ActionDecisionResponse)
def receive_action(action: ActionRequest) -> ActionDecisionResponse:
    return process_action(action)
