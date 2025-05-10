from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models
from . import schemas

# Методы Course

def get_course(db: Session, course_id: int) -> models.DBCourse | None:
    """Получить курс по ID из базы данных"""
    return db.query(models.DBCourse).filter(models.DBCourse.id == course_id).first()

def get_courses(db: Session, skip: int = 0, limit: int = 100) -> list[models.DBCourse]:
    """Получить список курсов с пагинацией"""
    return db.query(models.DBCourse).offset(skip).limit(limit).all()

def create_course(db: Session, course: schemas.CourseCreate) -> models.DBCourse:
    """Создать новый курс в базе данных"""
    db_course = models.DBCourse(
        title=course.title,
        description=course.description,
        total_hours=course.total_hours,
        lecture_hours=course.lecture_hours,
        practice_hours=course.practice_hours,
        difficulty=course.difficulty,
        has_online=course.has_online
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(db: Session, course_id: int, course_update: schemas.CourseCreate) -> models.DBCourse | None:
    """Обновить данные курса"""
    db_course = get_course(db, course_id)
    if db_course:
        for field, value in course_update.dict().items():
            setattr(db_course, field, value)
        db.commit()
        db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int) -> bool:
    """Удалить курс из базы данных и всех программ"""
    db_course = get_course(db, course_id)
    if db_course:
        programs_with_course = db.query(models.DBProgram).filter(
            models.DBProgram.courses.any(id=course_id)
        ).all()
        
        for program in programs_with_course:
            program.courses.remove(db_course)
        
        db.delete(db_course)
        db.commit()
        return True
    return False

# Методы Program

def get_program(db: Session, program_id: int) -> models.DBProgram | None:
    """Получить программу по ID с курсами"""
    return db.query(models.DBProgram).filter(models.DBProgram.id == program_id).first()

def get_programs(db: Session, skip: int = 0, limit: int = 100) -> list[models.DBProgram]:
    """Получить список программ с пагинацией"""
    return db.query(models.DBProgram).offset(skip).limit(limit).all()

def create_program(db: Session, program: schemas.ProgramCreate) -> models.DBProgram:
    """Создать новую образовательную программу"""
    db_program = models.DBProgram(
        name=program.name,
        description=program.description,
        total_duration_weeks=program.total_duration_weeks
    )
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    
    if program.course_ids:
        courses = db.query(models.DBCourse).filter(
            models.DBCourse.id.in_(program.course_ids)
        ).all()
        db_program.courses.extend(courses)
        db.commit()
        db.refresh(db_program)
    
    return db_program

def update_program(db: Session, program_id: int, program_update: schemas.ProgramCreate) -> models.DBProgram | None:
    """Обновить данные программы"""
    db_program = get_program(db, program_id)
    if db_program:
        for field, value in program_update.dict(exclude={"course_ids"}).items():
            setattr(db_program, field, value)
        
        if program_update.course_ids is not None:
            current_course_ids = {c.id for c in db_program.courses}
            new_course_ids = set(program_update.course_ids)
            courses_to_add = db.query(models.DBCourse).filter(
                models.DBCourse.id.in_(new_course_ids - current_course_ids)
            ).all()
            
            courses_to_remove = [c for c in db_program.courses if c.id in (current_course_ids - new_course_ids)]
            
            db_program.courses.extend(courses_to_add)
            for course in courses_to_remove:
                db_program.courses.remove(course)
        
        db.commit()
        db.refresh(db_program)
    return db_program

def delete_program(db: Session, program_id: int) -> bool:
    """Удалить программу"""
    db_program = get_program(db, program_id)
    if db_program:
        db.delete(db_program)
        db.commit()
        return True
    return False

def add_course_to_program(db: Session, program_id: int, course_id: int) -> bool:
    """Добавить курс в программу"""
    db_program = get_program(db, program_id)
    db_course = get_course(db, course_id)
    
    if not db_program or not db_course:
        return False
    
    if db_course not in db_program.courses:
        db_program.courses.append(db_course)
        db.commit()
        return True
    return False

def remove_course_from_program(db: Session, program_id: int, course_id: int) -> bool:
    """Удалить курс из программы"""
    db_program = get_program(db, program_id)
    db_course = get_course(db, course_id)
    
    if not db_program or not db_course:
        return False
    
    if db_course in db_program.courses:
        db_program.courses.remove(db_course)
        db.commit()
        return True
    return False

# Другие методы
def get_programs_with_course(db: Session, course_id: int) -> list[models.DBProgram]:
    """Получить все программы, содержащие указанный курс"""
    return db.query(models.DBProgram).filter(
        models.DBProgram.courses.any(id=course_id)
    ).all()

def get_courses_not_in_program(db: Session, program_id: int) -> list[models.DBCourse]:
    """Получить курсы, не входящие в указанную программу"""
    program = get_program(db, program_id)
    if not program:
        return []
    
    current_course_ids = [c.id for c in program.courses]
    if current_course_ids:
        return db.query(models.DBCourse).filter(
            models.DBCourse.id.notin_(current_course_ids)
        ).all()
    return db.query(models.DBCourse).all()