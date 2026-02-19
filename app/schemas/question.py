from pydantic import BaseModel
from typing import Optional,Dict

class QuestionCreate(BaseModel):
    subject: str
    mode: str
    bloom_level: Optional[str] = None
    difficulty: str
    num_questions: int
    language: str = "en"
    bloom_strategy: Optional[str] = "fixed"
    constraints: Optional[Dict] = None
