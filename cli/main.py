import requests
import click
from typing import List
from enum import Enum

BASE_URL = "http://localhost:8000"

class DifficultyLevel(Enum):
    BEGINNER = "начальный"
    INTERMEDIATE = "средний"
    ADVANCED = "продвинутый"

def print_header(title):
    """Печатает заголовок с рамкой"""
    click.echo("╔" + "═" * (len(title) + 2) + "╗")
    click.echo(f"║ {title} ║")
    click.echo("╚" + "═" * (len(title) + 2) + "╝")

def show_error(message):
    """Печатает сообщение об ошибке"""
    click.echo(f"\n❌ Ошибка: {message}")
    click.pause("\nНажмите Enter чтобы продолжить...")

def show_success(message):
    """Печатает сообщение об успехе"""
    click.echo(f"\n✅ {message}")
    click.pause("\nНажмите Enter чтобы продолжить...")

def list_courses_short():
    """Показывает краткий список курсов"""
    try:
        response = requests.get(f"{BASE_URL}/courses")
        if response.status_code == 200:
            for course in response.json():
                click.echo(f"{course['id']}: {course['title']} ({course['total_hours']} часов)")
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")

def list_programs_short():
    """Показывает краткий список программ"""
    try:
        response = requests.get(f"{BASE_URL}/programs")
        if response.status_code == 200:
            for program in response.json():
                click.echo(f"{program['id']}: {program['name']}")
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")

def view_course_details():
    """Просмотр деталей курса"""
    click.clear()
    print_header("Просмотр курса")
    
    list_courses_short()
    course_id = click.prompt("\nВведите ID курса", type=int)
    
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}")
        if response.status_code == 200:
            course = response.json()
            
            click.echo("\n📚 " + click.style(course['title'], fg='green', bold=True))
            click.echo(f"\nОписание: {course['description']}")
            click.echo(f"Общее количество часов: {course['total_hours']}")
            click.echo(f"Лекционные часы: {course['lecture_hours']}")
            click.echo(f"Практические часы: {course['practice_hours']}")
            click.echo(f"Уровень сложности: {course['difficulty']}")
            click.echo(f"Доступен онлайн: {'Да' if course['has_online'] else 'Нет'}")
            
            programs_response = requests.get(f"{BASE_URL}/courses/{course_id}/programs")
            if programs_response.status_code == 200 and programs_response.json():
                click.echo("\nВходит в программы:")
                for program in programs_response.json():
                    click.echo(f"  - {program['name']} (ID: {program['id']})")
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")
    
    click.pause("\nНажмите Enter чтобы продолжить...")

def view_program_details():
    """Просмотр деталей программы"""
    click.clear()
    print_header("Просмотр программы")
    
    list_programs_short()
    program_id = click.prompt("\nВведите ID программы", type=int)
    
    try:
        response = requests.get(f"{BASE_URL}/programs/{program_id}")
        if response.status_code == 200:
            program = response.json()
            
            click.echo("\n🎓 " + click.style(program['name'], fg='blue', bold=True))
            click.echo(f"\nОписание: {program['description']}")
            click.echo(f"Продолжительность: {program['total_duration_weeks']} недель")
            
            if program['courses']:
                click.echo("\nКурсы в программе:")
                for course in program['courses']:
                    click.echo(f"  - {course['title']} (ID: {course['id']}, {course['total_hours']} часов)")
            else:
                click.echo("\nВ программе пока нет курсов")
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")
    
    click.pause("\nНажмите Enter чтобы продолжить...")

# Методы для Course
def add_course():
    """Добавление нового курса"""
    click.clear()
    print_header("Добавление нового курса")
    
    try:
        title = click.prompt("Название курса")
        description = click.prompt("Описание курса", default="")
        total_hours = click.prompt("Общее количество часов", type=int)
        lecture_hours = click.prompt("Количество лекционных часов", type=int, default=0)
        practice_hours = click.prompt("Количество практических часов", type=int, default=0)
        
        click.echo("\nУровень сложности:")
        for i, level in enumerate(DifficultyLevel, 1):
            click.echo(f"{i}. {level.value}")
        difficulty_choice = click.prompt("Выберите уровень", type=int, default=2)
        difficulty = list(DifficultyLevel)[difficulty_choice-1].value
        
        has_online = click.confirm("Доступен онлайн?")
        
        course_data = {
            "title": title,
            "description": description,
            "total_hours": total_hours,
            "lecture_hours": lecture_hours,
            "practice_hours": practice_hours,
            "difficulty": difficulty,
            "has_online": has_online
        }
        
        response = requests.post(f"{BASE_URL}/courses/", json=course_data)
        
        if response.status_code == 201:
            show_success("Курс успешно создан!")
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")
    except Exception as e:
        show_error(str(e))

def update_course():
    """Обновление данных курса"""
    click.clear()
    print_header("Обновление курса")
    
    list_courses_short()
    course_id = click.prompt("\nВведите ID курса для обновления", type=int)
    
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}")
        if response.status_code != 200:
            show_error(response.text)
            return
        
        current_course = response.json()
        
        title = click.prompt("Название курса", default=current_course['title'])
        description = click.prompt("Описание курса", default=current_course['description'])
        total_hours = click.prompt("Общее количество часов", type=int, default=current_course['total_hours'])
        lecture_hours = click.prompt("Лекционные часы", type=int, default=current_course['lecture_hours'])
        practice_hours = click.prompt("Практические часы", type=int, default=current_course['practice_hours'])
        
        click.echo("\nТекущий уровень сложности: " + current_course['difficulty'])
        click.echo("Выберите новый уровень:")
        for i, level in enumerate(DifficultyLevel, 1):
            click.echo(f"{i}. {level.value}")
        difficulty_choice = click.prompt("Выберите уровень", type=int, 
                                       default=list(DifficultyLevel).index(
                                           DifficultyLevel(current_course['difficulty'])) + 1)
        difficulty = list(DifficultyLevel)[difficulty_choice-1].value
        
        has_online = click.confirm("Доступен онлайн?", default=current_course['has_online'])
        
        course_data = {
            "title": title,
            "description": description,
            "total_hours": total_hours,
            "lecture_hours": lecture_hours,
            "practice_hours": practice_hours,
            "difficulty": difficulty,
            "has_online": has_online
        }
        
        update_response = requests.put(f"{BASE_URL}/courses/{course_id}", json=course_data)
        
        if update_response.status_code == 200:
            show_success("Курс успешно обновлен!")
        else:
            show_error(update_response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")
    except Exception as e:
        show_error(str(e))

def delete_course():
    """Удаление курса"""
    click.clear()
    print_header("Удаление курса")
    
    list_courses_short()
    course_id = click.prompt("\nВведите ID курса для удаления", type=int)
    
    try:
        programs_response = requests.get(f"{BASE_URL}/courses/{course_id}/programs")
        if programs_response.status_code == 200 and programs_response.json():
            click.echo("\nЭтот курс входит в следующие программы:")
            for program in programs_response.json():
                click.echo(f"  - {program['name']} (ID: {program['id']})")
            
            if not click.confirm("\nКурс будет удален из всех программ. Продолжить?"):
                return
        
        if click.confirm("Вы уверены, что хотите удалить этот курс?"):
            response = requests.delete(f"{BASE_URL}/courses/{course_id}")
            
            if response.status_code == 204:
                show_success("Курс успешно удален!")
            else:
                show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")

# Методы для Program
def add_program():
    """Добавление новой программы"""
    click.clear()
    print_header("Добавление новой программы")
    
    try:
        name = click.prompt("Название программы")
        description = click.prompt("Описание программы", default="")
        duration = click.prompt("Продолжительность (недель)", type=int, default=12)
        
        list_courses_short()
        course_ids = click.prompt(
            "\nВведите ID курсов через запятую (оставьте пустым, если без курсов)", 
            default=""
        )
        
        program_data = {
            "name": name,
            "description": description,
            "total_duration_weeks": duration,
            "course_ids": [int(cid.strip()) for cid in course_ids.split(",") if cid.strip()]
        }
        
        response = requests.post(f"{BASE_URL}/programs/", json=program_data)
        
        if response.status_code == 201:
            show_success("Программа успешно создана!")
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")
    except Exception as e:
        show_error(str(e))

def update_program():
    """Обновление данных программы"""
    click.clear()
    print_header("Обновление программы")
    
    list_programs_short()
    program_id = click.prompt("\nВведите ID программы для обновления", type=int)
    
    try:
        response = requests.get(f"{BASE_URL}/programs/{program_id}")
        if response.status_code != 200:
            show_error(response.text)
            return
        
        current_program = response.json()
        
        name = click.prompt("Название программы", default=current_program['name'])
        description = click.prompt("Описание программы", default=current_program['description'])
        duration = click.prompt("Продолжительность (недель)", type=int, default=current_program['total_duration_weeks'])
        
        click.echo("\nТекущие курсы в программе:")
        if current_program['courses']:
            for course in current_program['courses']:
                click.echo(f"  - {course['title']} (ID: {course['id']})")
        else:
            click.echo("  В программе пока нет курсов")
        
        available_response = requests.get(f"{BASE_URL}/programs/{program_id}/available-courses")
        if available_response.status_code == 200 and available_response.json():
            click.echo("\nДоступные курсы для добавления:")
            for course in available_response.json():
                click.echo(f"  - {course['title']} (ID: {course['id']})")
        
        course_ids = click.prompt(
            "\nВведите ID всех курсов через запятую (оставьте пустым, если не менять)", 
            default=""
        )
        
        program_data = {
            "name": name,
            "description": description,
            "total_duration_weeks": duration,
            "course_ids": [int(cid.strip()) for cid in course_ids.split(",") if cid.strip()]
        }
        
        update_response = requests.put(f"{BASE_URL}/programs/{program_id}", json=program_data)
        
        if update_response.status_code == 200:
            show_success("Программа успешно обновлена!")
        else:
            show_error(update_response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")
    except Exception as e:
        show_error(str(e))

def delete_program():
    """Удаление программы"""
    click.clear()
    print_header("Удаление программы")
    
    list_programs_short()
    program_id = click.prompt("\nВведите ID программы для удаления", type=int)
    
    try:
        if click.confirm("Вы уверены, что хотите удалить эту программу?"):
            response = requests.delete(f"{BASE_URL}/programs/{program_id}")
            
            if response.status_code == 204:
                show_success("Программа успешно удалена!")
            else:
                show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")

def add_course_to_program():
    """Добавление курса в программу"""
    click.clear()
    print_header("Добавление курса в программу")
    
    list_programs_short()
    program_id = click.prompt("\nВведите ID программы", type=int)
    
    try:
        response = requests.get(f"{BASE_URL}/programs/{program_id}/available-courses")
        if response.status_code == 200:
            if not response.json():
                show_error("Нет доступных курсов для добавления")
                return
            
            click.echo("\nДоступные курсы:")
            for course in response.json():
                click.echo(f"{course['id']}: {course['title']}")
            
            course_id = click.prompt("\nВведите ID курса для добавления", type=int)
            
            add_response = requests.post(
                f"{BASE_URL}/programs/{program_id}/courses/{course_id}"
            )
            
            if add_response.status_code == 200:
                show_success("Курс успешно добавлен в программу!")
            else:
                show_error(add_response.text)
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")

def remove_course_from_program():
    """Удаление курса из программы"""
    click.clear()
    print_header("Удаление курса из программы")
    
    list_programs_short()
    program_id = click.prompt("\nВведите ID программы", type=int)
    
    try:
        response = requests.get(f"{BASE_URL}/programs/{program_id}")
        if response.status_code == 200:
            program = response.json()
            
            if not program['courses']:
                show_error("В этой программе нет курсов")
                return
            
            click.echo("\nКурсы в программе:")
            for course in program['courses']:
                click.echo(f"{course['id']}: {course['title']}")
            
            course_id = click.prompt("\nВведите ID курса для удаления", type=int)
            
            remove_response = requests.delete(
                f"{BASE_URL}/programs/{program_id}/courses/{course_id}"
            )
            
            if remove_response.status_code == 200:
                show_success("Курс успешно удален из программы!")
            else:
                show_error(remove_response.text)
        else:
            show_error(response.text)
    except requests.exceptions.RequestException:
        show_error("Не удалось подключиться к серверу")

# Главное меню
def courses_menu():
    """Меню управления курсами"""
    while True:
        click.clear()
        print_header("Управление курсами")
        click.echo("1. Добавить курс")
        click.echo("2. Список всех курсов")
        click.echo("3. Просмотреть курс")
        click.echo("4. Обновить курс")
        click.echo("5. Удалить курс")
        click.echo("0. Назад")
        
        choice = click.prompt("\nВыберите действие", type=int)
        
        if choice == 1:
            add_course()
        elif choice == 2:
            click.clear()
            print_header("Список всех курсов")
            list_courses_short()
            click.pause("\nНажмите Enter чтобы продолжить...")
        elif choice == 3:
            view_course_details()
        elif choice == 4:
            update_course()
        elif choice == 5:
            delete_course()
        elif choice == 0:
            break
        else:
            show_error("Неверный выбор")

def programs_menu():
    """Меню управления программами"""
    while True:
        click.clear()
        print_header("Управление программами")
        click.echo("1. Добавить программу")
        click.echo("2. Список всех программ")
        click.echo("3. Просмотреть программу")
        click.echo("4. Обновить программу")
        click.echo("5. Удалить программу")
        click.echo("6. Добавить курс в программу")
        click.echo("7. Удалить курс из программы")
        click.echo("0. Назад")
        
        choice = click.prompt("\nВыберите действие", type=int)
        
        if choice == 1:
            add_program()
        elif choice == 2:
            click.clear()
            print_header("Список всех программ")
            list_programs_short()
            click.pause("\nНажмите Enter чтобы продолжить...")
        elif choice == 3:
            view_program_details()
        elif choice == 4:
            update_program()
        elif choice == 5:
            delete_program()
        elif choice == 6:
            add_course_to_program()
        elif choice == 7:
            remove_course_from_program()
        elif choice == 0:
            break
        else:
            show_error("Неверный выбор")

def main_menu():
    """Главное меню"""
    while True:
        click.clear()
        print_header("Интеллектуальный модуль образования")
        click.echo("1. Управление курсами")
        click.echo("2. Управление программами")
        click.echo("0. Выход")
        
        choice = click.prompt("\nВыберите действие", type=int)
        
        if choice == 1:
            courses_menu()
        elif choice == 2:
            programs_menu()
        elif choice == 0:
            click.clear()
            click.echo("До свидания!")
            break
        else:
            show_error("Неверный выбор")

if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            main_menu()
        else:
            click.echo("Сервер не доступен. Запустите сервер сначала.")
            click.pause("Нажмите Enter чтобы выйти...")
    except requests.exceptions.RequestException:
        click.echo("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        click.pause("Нажмите Enter чтобы выйти...")