"""
CampusMind FastAPI backend - consolidated, cleaned endpoints.

Features:
- Basic auth: POST /auth/login (email + password) -> user metadata
- Issue creation: POST /issues (auto-classify + assign to student's manager if present)
- Role-aware listing: GET /issues/for_user/{user_id}?show_resolved=false
- Generic issue list: GET /issues (with filters)
- Active / Resolved shortcuts: GET /issues/active, GET /issues/resolved
- Get single issue: GET /issues/{issue_id}
- Re-classify: POST /issues/{issue_id}/classify
- Forward / escalate: POST /issues/{issue_id}/forward?by_user_id=
- Verify / resolve: POST /issues/{issue_id}/verify?verifier_id=&resolved=true
- Manual assign: POST /users/{user_id}/assign_issue/{issue_id}?assigner_id=
- Search issues by title: GET /issues/search?title=
- User list & get: GET /users, GET /users/{user_id}
- Admin endpoints:
    - GET /admin/issues (all issues, with optional filters)
    - GET /admin/stats (counts overall + per-department breakdown)
Notes:
- Uses your models.py and schemas.py (IssueOut expects created_at present).
- Classifier is optional; if missing, falls back to "other"/low priority.
"""

import os
from typing import Optional, List, Dict
from datetime import datetime

import joblib
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker, Session

from models import Base, User, Issue, Department, Section
from schemas import IssueCreate, IssueOut

DB_DIR = "data"
DB_FILE = "issue_manager.db"
DB_URI = f"sqlite:///{os.path.join(os.getcwd(), DB_DIR, DB_FILE)}"
MODEL_PATH = os.path.join(os.getcwd(), "category_pipe.pkl")

engine = create_engine(DB_URI, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="CampusMind Backend (main.py)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = None
classifier_loaded = False
if os.path.exists(MODEL_PATH):
    try:
        classifier = joblib.load(MODEL_PATH)
        classifier_loaded = True
    except Exception:
        classifier = None
        classifier_loaded = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def predict_category_and_priority(text: str) -> Dict:
    """
    Returns dict: {category, confidence, priority}
    Heuristic-based priority + classifier confidence.
    """
    if not classifier_loaded or classifier is None:
        return {"category": "other", "confidence": 0.0, "priority": "low"}
    try:
        pred = classifier.predict([text])[0]
        prob = float(classifier.predict_proba([text])[0].max())
    except Exception:
        pred = "other"
        prob = 0.0

    text_low = text.lower()
    if any(k in text_low for k in ["fire", "sparking", "danger", "broken", "injury", "accident"]):
        priority = "critical"
    elif any(k in text_low for k in ["urgent", "asap", "soon", "today"]):
        priority = "high"
    elif prob < 0.45:
        priority = "medium"
    else:
        priority = "low"

    return {"category": pred, "confidence": prob, "priority": priority}

def find_next_assignee(db: Session, current_user_id: Optional[int]) -> Optional[User]:
    """Return the manager of current_user (reports_to) or VC fallback."""
    if not current_user_id:
        return None
    cur = db.query(User).filter(User.id == current_user_id).first()
    if not cur:
        return None
    next_id = cur.reports_to
    if not next_id:
        vc = db.query(User).filter(User.role == "vc").first()
        return vc
    return db.query(User).filter(User.id == next_id).first()

def escalate_issue_to_next(db: Session, issue: Issue, by_user_id: int) -> Issue:
    """
    Escalate an issue up the reports_to chain.
    If issue.assigned_to is None -> assign to student's reports_to (proctor) or VC fallback.
    """
    if issue.assigned_to is None:
        student = db.query(User).filter(User.id == issue.student_id).first()
        if not student:
            raise HTTPException(status_code=400, detail="Issue has invalid student_id")
        if not student.reports_to:
            next_user = db.query(User).filter(User.role == "vc").first()
        else:
            next_user = db.query(User).filter(User.id == student.reports_to).first()
    else:
        next_user = find_next_assignee(db, issue.assigned_to)

    if not next_user:
        raise HTTPException(status_code=400, detail="No higher authority found to escalate to")

    issue.forwarded_by = by_user_id
    issue.assigned_to = next_user.id
    issue.status = "forwarded"
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@app.on_event("startup")
def startup():
    # Ensure data directory exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    Base.metadata.create_all(bind=engine)

@app.post("/auth/login")
def login(email: str = Query(...), password: str = Query(...), db: Session = Depends(get_db)):
    """
    Basic login. Returns user metadata (no password).
    Uses query parameters for email and password.
    """
    user = db.query(User).filter(User.email == email, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department_id": user.department_id,
        "section_id": user.section_id,
        "reports_to": user.reports_to,
    }

@app.post("/issues", response_model=IssueOut, status_code=201)
def create_issue(payload: IssueCreate, db: Session = Depends(get_db)):
    """
    Create an issue. Auto-classify and set priority using ML if available.
    Assign to student's direct manager (reports_to) if present; otherwise unassigned.
    """
    student = db.query(User).filter(User.id == payload.student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    pred = predict_category_and_priority(payload.description)
    category = pred["category"]
    priority = pred["priority"]

    assignee_id = student.reports_to if student.reports_to else None

    issue = Issue(
        title=payload.title,
        description=payload.description,
        student_id=payload.student_id,
        department_id=student.department_id,
        section_id=student.section_id,
        category=category,
        priority=priority,
        status="open",
        assigned_to=assignee_id,
        created_at=datetime.utcnow()
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@app.get("/issues", response_model=List[IssueOut])
def list_issues(skip: int = 0, limit: int = 500, show_resolved: bool = True, db: Session = Depends(get_db)):
    """
    Generic list of issues. By default includes resolved unless show_resolved=False.
    """
    q = db.query(Issue)
    if not show_resolved:
        q = q.filter(Issue.status != "closed")
    issues = q.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
    return issues

@app.get("/issues/active", response_model=List[IssueOut])
def list_active_issues(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    return db.query(Issue).filter(Issue.status != "closed").order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()

@app.get("/issues/resolved", response_model=List[IssueOut])
def list_resolved_issues(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    return db.query(Issue).filter(Issue.status == "closed").order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()

@app.get("/issues/{issue_id}", response_model=IssueOut)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@app.post("/issues/{issue_id}/classify", response_model=IssueOut)
def classify_issue(issue_id: int, db: Session = Depends(get_db)):
    """
    Re-classify an existing issue using the ML model and update priority.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    pred = predict_category_and_priority(issue.description)
    issue.category = pred["category"]
    issue.priority = pred["priority"]
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@app.post("/issues/{issue_id}/forward", response_model=IssueOut)
def forward_issue(issue_id: int, by_user_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Forward/escalate the issue. `by_user_id` is the id of the user performing the forward.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    user = db.query(User).filter(User.id == by_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Forwarding user not found")
    updated = escalate_issue_to_next(db, issue, by_user_id=by_user_id)
    return updated

@app.post("/issues/{issue_id}/verify", response_model=IssueOut)
def verify_issue(issue_id: int, verifier_id: int = Query(...), resolved: bool = Query(True), db: Session = Depends(get_db)):
    """
    Mark issue as verified by verifier (proctor/HOD/VC).
    If resolved=True -> status becomes 'closed', set verified_by and verified_at.
    If resolved=False -> escalate automatically.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    verifier = db.query(User).filter(User.id == verifier_id).first()
    if not verifier:
        raise HTTPException(status_code=404, detail="Verifier not found")

    issue.verified_by = verifier_id
    issue.verified_at = datetime.utcnow()

    if resolved:
        issue.status = "closed"
    else:
        try:
            issue = escalate_issue_to_next(db, issue, by_user_id=verifier_id)
            return issue
        except HTTPException:
            issue.status = "open"

    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@app.post("/users/{user_id}/assign_issue/{issue_id}", response_model=IssueOut)
def assign_issue_to_user(user_id: int, issue_id: int, assigner_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.assigned_to = user_id
    issue.status = "assigned"
    if assigner_id:
        issue.forwarded_by = assigner_id
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

@app.get("/issues/for_user/{user_id}", response_model=List[IssueOut])
def issues_for_user(user_id: int, show_resolved: bool = Query(False), skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    """
    Returns issues visible to the user depending on role.
    Default: hide resolved issues (show_resolved=False).
    Rules:
      - student: sees their own issues
      - proctor: sees issues assigned to them OR issues in their section
      - hod: sees issues in their department
      - vc: sees issues assigned to VC (escalated to VC)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    q = db.query(Issue)
    if user.role == "student":
        q = q.filter(Issue.student_id == user_id)
    elif user.role == "proctor":
        # proctor sees assigned to them OR issues from their section
        if user.section_id:
            q = q.filter(or_(Issue.assigned_to == user_id, Issue.section_id == user.section_id))
        else:
            q = q.filter(Issue.assigned_to == user_id)
    elif user.role == "hod":
        if user.department_id:
            q = q.filter(Issue.department_id == user.department_id)
        else:
            q = q.filter(False)  # no dept -> nothing
    elif user.role == "vc":
        q = q.filter(Issue.assigned_to == user_id)
    else:
        q = q.filter(False)

    if not show_resolved:
        q = q.filter(Issue.status != "closed")

    issues = q.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
    return issues

@app.get("/issues/search", response_model=List[IssueOut])
def search_issues(title: Optional[str] = Query(None), department_id: Optional[int] = Query(None), db: Session = Depends(get_db), skip: int = 0, limit: int = 500):
    q = db.query(Issue)
    if title:
        # simple case-insensitive partial match
        pattern = f"%{title}%"
        q = q.filter(Issue.title.ilike(pattern))
    if department_id:
        q = q.filter(Issue.department_id == department_id)
    return q.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "department_id": u.department_id,
            "section_id": u.section_id,
            "reports_to": u.reports_to,
        }
        for u in users
    ]

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "department_id": u.department_id,
        "section_id": u.section_id,
        "reports_to": u.reports_to,
    }

@app.get("/departments/{dept_id}")
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"id": dept.id, "name": dept.name}

@app.get("/sections/{section_id}")
def get_section(section_id: int, db: Session = Depends(get_db)):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return {"id": section.id, "name": section.name}

@app.get("/admin/issues", response_model=List[IssueOut])
def admin_list_issues(skip: int = 0, limit: int = 1000, status: Optional[str] = Query(None), department_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Admin: list all issues with optional filters.
    """
    q = db.query(Issue)
    if status:
        q = q.filter(Issue.status == status)
    if department_id:
        q = q.filter(Issue.department_id == department_id)
    return q.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()

@app.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    """
    Return overall counts and per-department breakdown:
    {
      total: n,
      active: n,
      resolved: n,
      by_department: [{department_id, department_name, total, active, resolved}]
    }
    """
    total = db.query(func.count(Issue.id)).scalar() or 0
    active = db.query(func.count(Issue.id)).filter(Issue.status != "closed").scalar() or 0
    resolved = db.query(func.count(Issue.id)).filter(Issue.status == "closed").scalar() or 0

    # per-dept breakdown
    depts = db.query(Department).all()
    by_department = []
    for d in depts:
        dept_total = db.query(func.count(Issue.id)).filter(Issue.department_id == d.id).scalar() or 0
        dept_active = db.query(func.count(Issue.id)).filter(Issue.department_id == d.id, Issue.status != "closed").scalar() or 0
        dept_resolved = db.query(func.count(Issue.id)).filter(Issue.department_id == d.id, Issue.status == "closed").scalar() or 0
        by_department.append({
            "department_id": d.id,
            "department_name": d.name,
            "total": dept_total,
            "active": dept_active,
            "resolved": dept_resolved
        })

    return {
        "total": total,
        "active": active,
        "resolved": resolved,
        "by_department": by_department
    }