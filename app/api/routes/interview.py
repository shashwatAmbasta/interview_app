import secrets
from datetime import datetime, timezone
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.dependencies import current_user
from app.schemas.interview import AnswerRequest, InterviewQuestion
from app.services.document_service import extract_text
from app.services.llm_service import generate_questions
from app.services.session_service import session_store

router = APIRouter(prefix="/api/interview", tags=["interviews"])


@router.post("/start")
def start_interview(file: UploadFile = File(...), user=Depends(current_user)) -> dict:
    data = file.file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Please keep files under 12 MB")
    text = extract_text(file.filename or "document", data).strip()
    if len(text) < 30:
        raise HTTPException(status_code=422, detail="We could not find enough text in that document")
    questions, mode = generate_questions(text)
    interview_id = secrets.token_urlsafe(12)
    payload = {
        "id": interview_id,
        "user_id": user["id"],
        "filename": file.filename,
        "questions": [question.model_dump() for question in questions],
        "answers": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    session_store.save_interview(interview_id, payload)
    return {"id": interview_id, "filename": file.filename, "questions": payload["questions"], "total": len(questions), "mode": mode}


@router.post("/{interview_id}/answer")
def save_answer(interview_id: str, request: AnswerRequest, user=Depends(current_user)) -> dict[str, bool]:
    interview = _get_owned_interview(interview_id, user["id"])
    interview["answers"].append({"answer": request.answer, "saved_at": time.time()})
    session_store.save_interview(interview_id, interview)
    return {"saved": True}


@router.get("/{interview_id}")
def get_interview(interview_id: str, user=Depends(current_user)) -> dict:
    return _get_owned_interview(interview_id, user["id"])


def _get_owned_interview(interview_id: str, user_id: int) -> dict:
    interview = session_store.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="This interview belongs to another user")
    return interview
