from sqlalchemy import Column, Integer, String, Boolean, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum as PyEnum

class DifficultyLevel(str, PyEnum):
    BEGINNER = "начальный"
    INTERMEDIATE = "средний"
    ADVANCED = "продвинутый"

class DBCourse(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    total_hours = Column(Integer)
    lecture_hours = Column(Integer)
    practice_hours = Column(Integer)
    difficulty = Column(Enum(DifficultyLevel))
    has_online = Column(Boolean, default=False)

    programs = relationship("DBProgram", secondary="program_courses", back_populates="courses")

class DBProgram(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    total_duration_weeks = Column(Integer)
    courses = relationship("DBCourse", secondary="program_courses", back_populates="programs")

program_courses = Table(
    "program_courses",
    Base.metadata,
    Column("program_id", Integer, ForeignKey("programs.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)