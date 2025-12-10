from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class IssueCreate(BaseModel):
    student_id: int 
    title: str
    description: str

class IssueOut(BaseModel):
    id: int
    title: str
    description: str
    student_id: Optional[int] 
    assigned_to: Optional[int]   
    verified_by: Optional[int]  
    verified_at: Optional[datetime] 
    forwarded_by: Optional[int]  
    department_id: Optional[int]  
    section_id: Optional[int]       
    category: Optional[str]
    priority: Optional[str]
    status: str
    created_at: Optional[datetime]
    class Config:
        orm_mode = True