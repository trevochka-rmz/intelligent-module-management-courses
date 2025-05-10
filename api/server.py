from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud
from .database import SessionLocal, engine
from datetime import timedelta

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Интеллектуальный модуль образовательных программ",
    description="API для управления курсами и образовательными программами",
    version="1.0.0"
)

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====================== КУРСЫ ======================
@app.post("/courses/", 
          response_model=schemas.Course,
          status_code=status.HTTP_201_CREATED,
          summary="Создать новый курс",
          tags=["Курсы"])
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """
    Создает новый курс с указанными параметрами.
    
    - **title**: Название курса (обязательно)
    - **description**: Описание курса
    - **total_hours**: Общее количество часов (обязательно)
    - **lecture_hours**: Количество лекционных часов
    - **practice_hours**: Количество практических часов
    - **difficulty**: Уровень сложности (начальный/средний/продвинутый)
    - **has_online**: Доступна ли онлайн-версия
    """
    return crud.create_course(db=db, course=course)

@app.get("/courses/", 
         response_model=List[schemas.Course],
         summary="Получить список всех курсов",
         tags=["Курсы"])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список всех курсов с пагинацией.
    
    - **skip**: Сколько записей пропустить
    - **limit**: Максимальное количество возвращаемых записей
    """
    return crud.get_courses(db, skip=skip, limit=limit)

@app.get("/courses/{course_id}", 
         response_model=schemas.Course,
         summary="Получить курс по ID",
         tags=["Курсы"])
def read_course(course_id: int, db: Session = Depends(get_db)):
    """
    Возвращает полную информацию о курсе по его ID.
    
    - **course_id**: ID курса
    """
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return db_course

@app.put("/courses/{course_id}", 
         response_model=schemas.Course,
         summary="Обновить данные курса",
         tags=["Курсы"])
def update_course(
    course_id: int, 
    course: schemas.CourseCreate, 
    db: Session = Depends(get_db)
):
    """
    Обновляет данные курса по его ID.
    
    - **course_id**: ID обновляемого курса
    - Все поля курса (см. создание курса)
    """
    db_course = crud.update_course(db=db, course_id=course_id, course_update=course)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return db_course

@app.delete("/courses/{course_id}", 
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удалить курс",
            tags=["Курсы"])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Удаляет курс по его ID и все его упоминания в программах.
    
    - **course_id**: ID удаляемого курса
    """
    success = crud.delete_course(db=db, course_id=course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return {"ok": True}

@app.get("/courses/{course_id}/programs",
         response_model=List[schemas.Program],
         summary="Получить программы, содержащие курс",
         tags=["Курсы"])
def get_programs_with_course(course_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список всех программ, которые содержат указанный курс.
    
    - **course_id**: ID курса
    """
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return crud.get_programs_with_course(db, course_id=course_id)

# ====================== ПРОГРАММЫ ======================
@app.post("/programs/", 
          response_model=schemas.Program,
          status_code=status.HTTP_201_CREATED,
          summary="Создать новую программу",
          tags=["Программы"])
def create_program(program: schemas.ProgramCreate, db: Session = Depends(get_db)):
    """
    Создает новую образовательную программу.
    
    - **name**: Название программы (обязательно)
    - **description**: Описание программы
    - **total_duration_weeks**: Продолжительность в неделях
    - **course_ids**: Список ID курсов для включения в программу
    """
    return crud.create_program(db=db, program=program)

@app.get("/programs/", 
         response_model=List[schemas.Program],
         summary="Получить список всех программ",
         tags=["Программы"])
def read_programs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список всех образовательных программ с пагинацией.
    
    - **skip**: Сколько записей пропустить
    - **limit**: Максимальное количество возвращаемых записей
    """
    return crud.get_programs(db, skip=skip, limit=limit)

@app.get("/programs/{program_id}", 
         response_model=schemas.Program,
         summary="Получить программу по ID",
         tags=["Программы"])
def read_program(program_id: int, db: Session = Depends(get_db)):
    """
    Возвращает полную информацию о программе по ее ID, включая список курсов.
    
    - **program_id**: ID программы
    """
    db_program = crud.get_program(db, program_id=program_id)
    if db_program is None:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return db_program

@app.put("/programs/{program_id}", 
         response_model=schemas.Program,
         summary="Обновить данные программы",
         tags=["Программы"])
def update_program(
    program_id: int, 
    program: schemas.ProgramCreate, 
    db: Session = Depends(get_db)
):
    """
    Обновляет данные программы по ее ID.
    
    - **program_id**: ID обновляемой программы
    - Все поля программы (см. создание программы)
    """
    db_program = crud.update_program(db=db, program_id=program_id, program_update=program)
    if db_program is None:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return db_program

@app.delete("/programs/{program_id}", 
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удалить программу",
            tags=["Программы"])
def delete_program(program_id: int, db: Session = Depends(get_db)):
    """
    Удаляет программу по ее ID.
    
    - **program_id**: ID удаляемой программы
    """
    success = crud.delete_program(db=db, program_id=program_id)
    if not success:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return {"ok": True}

@app.post("/programs/{program_id}/courses/{course_id}",
          status_code=status.HTTP_200_OK,
          summary="Добавить курс в программу",
          tags=["Программы"])
def add_course_to_program(
    program_id: int, 
    course_id: int, 
    db: Session = Depends(get_db)
):
    """
    Добавляет курс в образовательную программу.
    
    - **program_id**: ID программы
    - **course_id**: ID добавляемого курса
    """
    success = crud.add_course_to_program(db=db, program_id=program_id, course_id=course_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Программа или курс не найдены, либо курс уже в программе"
        )
    return {"message": "Курс успешно добавлен в программу"}

@app.delete("/programs/{program_id}/courses/{course_id}",
            status_code=status.HTTP_200_OK,
            summary="Удалить курс из программы",
            tags=["Программы"])
def remove_course_from_program(
    program_id: int, 
    course_id: int, 
    db: Session = Depends(get_db)
):
    """
    Удаляет курс из образовательной программы.
    
    - **program_id**: ID программы
    - **course_id**: ID удаляемого курса
    """
    success = crud.remove_course_from_program(db=db, program_id=program_id, course_id=course_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Программа или курс не найдены, либо курс отсутствует в программе"
        )
    return {"message": "Курс успешно удален из программы"}

@app.get("/programs/{program_id}/available-courses",
         response_model=List[schemas.Course],
         summary="Получить курсы, не входящие в программу",
         tags=["Программы"])
def get_available_courses(program_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список курсов, которые еще не входят в указанную программу.
    
    - **program_id**: ID программы
    """
    db_program = crud.get_program(db, program_id=program_id)
    if db_program is None:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return crud.get_courses_not_in_program(db, program_id=program_id)

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok", "message": "Сервер работает нормально"}