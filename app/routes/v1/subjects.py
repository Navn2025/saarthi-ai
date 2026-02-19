from fastapi import APIRouter, HTTPException, status, Depends
from app.core.auth import get_current_user
from app.core.role import require_role
from app.database.models import Subject
from app.database.database import SessionLocal

router=APIRouter(
    prefix="/v1/subjects", 
    tags=["subjects"]
)

@router.get("/list")
def list_subject():
    db=SessionLocal()
    subjects=db.query(Subject).distinct(Subject.name).all()
    db.close()
    return {"subjects":[(s.name,s.id) for s in subjects if s.name]}

@router.post("/add")
def add_subject(subject:str, user=Depends(require_role("admin"))):
    db=SessionLocal()
    existing_subject=db.query(Subject).filter(Subject.name==subject).first()
    if existing_subject:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject already exists"
        )
    new_subject=Subject(name=subject)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    db.close()
    return {"message":"Subject added successfully"}

@router.delete("/delete")
def delete_subject(subject:str, user=Depends(require_role("admin"))):
    db=SessionLocal()
    existing_subject=db.query(Subject).filter(Subject.name==subject).first()
    if not existing_subject:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    db.delete(existing_subject)
    db.commit()
    db.close()
    return {"message":"Subject deleted successfully"}

@router.put("/update")
def update_subject(old_subject:str, new_subject:str, user=Depends(require_role("admin"))):
    db=SessionLocal()
    existing_subject=db.query(Subject).filter(Subject.name==old_subject).first()
    if not existing_subject:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    existing_subject.name=new_subject
    db.commit()
    db.refresh(existing_subject)
    db.close()
    return {"message":"Subject updated successfully"}
