from fastapi import FastAPI

from app.routes.v1.auth import router as auth_router
from app.routes.v1.interview_session import router as interview_session_router
from app.routes.v1.questions import router as questions_router
from app.routes.v1.answer import router as answer_router
from app.routes.v1.subjects import router as subjects_router
from app.routes.v1.refresh import router as refresh_router
app=FastAPI()

app.include_router(auth_router)
app.include_router(interview_session_router)
app.include_router(questions_router)
app.include_router(answer_router)
app.include_router(subjects_router)
app.include_router(refresh_router)

@app.get("/")
def read_root():
    return {"message":"AI SERVICES WELCOMES YOU"}