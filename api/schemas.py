from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "начальный"
    INTERMEDIATE = "средний"
    ADVANCED = "продвинутый"

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    total_hours: int
    lecture_hours: int
    practice_hours: int
    difficulty: DifficultyLevel
    has_online: bool

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    
    class Config:
        from_attributes = True  

class ProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    total_duration_weeks: int

class ProgramCreate(ProgramBase):
    course_ids: List[int] = []

class Program(ProgramBase):
    id: int
    courses: List[Course] = []
    
    class Config:
        from_attributes = True  