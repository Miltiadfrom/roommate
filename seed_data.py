from database import db
from models import Profile
import random

def create_test_users():
    """Создание тестовых пользователей"""
    test_users = [
        {"phone": "user1@test.ru", "password": "123456", "name": "Александр Иванов", "age": 23, "gender": "Мужской"},
        {"phone": "user2@test.ru", "password": "123456", "name": "Мария Петрова", "age": 21, "gender": "Женский"},
        {"phone": "user3@test.ru", "password": "123456", "name": "Дмитрий Сидоров", "age": 25, "gender": "Мужской"},
        {"phone": "user4@test.ru", "password": "123456", "name": "Елена Козлова", "age": 22, "gender": "Женский"},
        {"phone": "user5@test.ru", "password": "123456", "name": "Алексей Морозов", "age": 24, "gender": "Мужской"},
        {"phone": "user6@test.ru", "password": "123456", "name": "Анна Новикова", "age": 20, "gender": "Женский"},
        {"phone": "user7@test.ru", "password": "123456", "name": "Иван Волков", "age": 26, "gender": "Мужской"},
        {"phone": "user8@test.ru", "password": "123456", "name": "Ольга Соколова", "age": 23, "gender": "Женский"},
    ]

    created_users = []
    for user_data in test_users:
        user_id = db.create_user(user_data["phone"], user_data["password"])
        if user_id:
            created_users.append(user_id)
            print(f"✅ Создан пользователь: {user_data['name']} (ID: {user_id})")
        else:
            print(f"⚠️ Пользователь {user_data['phone']} уже существует")

    return created_users

def create_test_profiles(user_ids):
    """Создание тестовых профилей"""
    profiles_data = [
        {
            "full_name": "Александр Иванов",
            "age": 23,
            "gender": "Мужской",
            "occupation": "Студент",
            "budget_min": 8000,
            "budget_max": 15000,
            "districts": ['Центральный', 'Советский'],
            "schedule": 'День (12:00-18:00)',
            "cleanliness": 7,
            "noise": 6,
            "smoking": False,
            "alcohol": True,
            "personality": 7,
            "hobbies": ['Спорт', 'Игры'],
            "pets": False
        },
        {
            "full_name": "Мария Петрова",
            "age": 21,
            "gender": "Женский",
            "occupation": "Студент",
            "budget_min": 7000,
            "budget_max": 12000,
            "districts": ['Центральный', 'Кировский'],
            "schedule": 'Утро (до 12:00)',
            "cleanliness": 9,
            "noise": 4,
            "smoking": False,
            "alcohol": False,
            "personality": 5,
            "hobbies": ['Чтение', 'Музыка'],
            "pets": True
        },
        {
            "full_name": "Дмитрий Сидоров",
            "age": 25,
            "gender": "Мужской",
            "occupation": "Программист",
            "budget_min": 10000,
            "budget_max": 20000,
            "districts": ['Советский', 'Промышленный'],
            "schedule": 'Ночь (после 18:00)',
            "cleanliness": 5,
            "noise": 8,
            "smoking": True,
            "alcohol": True,
            "personality": 8,
            "hobbies": ['Игры', 'Технологии'],
            "pets": False
        },
        {
            "full_name": "Елена Козлова",
            "age": 22,
            "gender": "Женский",
            "occupation": "Дизайнер",
            "budget_min": 9000,
            "budget_max": 18000,
            "districts": ['Центральный', 'Самарский'],
            "schedule": 'День (12:00-18:00)',
            "cleanliness": 8,
            "noise": 5,
            "smoking": False,
            "alcohol": True,
            "personality": 6,
            "hobbies": ['Искусство', 'Путешествия'],
            "pets": True
        },
        {
            "full_name": "Алексей Морозов",
            "age": 24,
            "gender": "Мужской",
            "occupation": "Инженер",
            "budget_min": 12000,
            "budget_max": 25000,
            "districts": ['Кировский', 'Промышленный'],
            "schedule": 'Утро (до 12:00)',
            "cleanliness": 6,
            "noise": 7,
            "smoking": False,
            "alcohol": False,
            "personality": 4,
            "hobbies": ['Спорт', 'Технологии'],
            "pets": False
        },
        {
            "full_name": "Анна Новикова",
            "age": 20,
            "gender": "Женский",
            "occupation": "Студент",
            "budget_min": 6000,
            "budget_max": 10000,
            "districts": ['Советский', 'Самарский'],
            "schedule": 'День (12:00-18:00)',
            "cleanliness": 7,
            "noise": 6,
            "smoking": False,
            "alcohol": False,
            "personality": 8,
            "hobbies": ['Музыка', 'Путешествия'],
            "pets": False
        },
        {
            "full_name": "Иван Волков",
            "age": 26,
            "gender": "Мужской",
            "occupation": "Менеджер",
            "budget_min": 15000,
            "budget_max": 30000,
            "districts": ['Центральный'],
            "schedule": 'День (12:00-18:00)',
            "cleanliness": 8,
            "noise": 5,
            "smoking": False,
            "alcohol": True,
            "personality": 7,
            "hobbies": ['Спорт', 'Чтение'],
            "pets": True
        },
        {
            "full_name": "Ольга Соколова",
            "age": 23,
            "gender": "Женский",
            "occupation": "Маркетолог",
            "budget_min": 10000,
            "budget_max": 20000,
            "districts": ['Кировский', 'Самарский'],
            "schedule": 'Утро (до 12:00)',
            "cleanliness": 9,
            "noise": 4,
            "smoking": False,
            "alcohol": False,
            "personality": 6,
            "hobbies": ['Готовка', 'Путешествия'],
            "pets": False
        },
    ]

    for i, user_id in enumerate(user_ids):
        if i < len(profiles_data):
            data = profiles_data[i]
            profile = Profile(
                user_id=user_id,
                full_name=data["full_name"],
                age=data["age"],
                gender=data["gender"],
                occupation=data["occupation"],
                contact_info=f"+7 (999) {1000000 + i:07d}",
                photo_path="",
                budget_min=data["budget_min"],
                budget_max=data["budget_max"],
                preferred_districts=data["districts"],
                housing_type="Квартира",
                rental_period="От 6 месяцев",
                daily_schedule=data["schedule"],
                cleanliness_level=data["cleanliness"],
                noise_tolerance=data["noise"],
                smoking=data["smoking"],
                alcohol=data["alcohol"],
                personality_type=data["personality"],
                hobbies=data["hobbies"],
                has_pets=data["pets"],
                preferred_neighbor_gender="Любой",
                neighbor_age_min=18,
                neighbor_age_max=35,
                important_criteria=["Чистоплотный"]
            )

            if db.save_profile(profile):
                print(f"✅ Создан профиль для {data['full_name']}")
            else:
                print(f"❌ Ошибка создания профиля для {data['full_name']}")

if __name__ == "__main__":
    print("=" * 50)
    print("Roommate Finder - Генерация тестовых данных")
    print("=" * 50)
    print()

    user_ids = create_test_users()
    print()
    create_test_profiles(user_ids)

    print()
    print("=" * 50)
    print(f"Создано {len(user_ids)} тестовых пользователей")
    print()
    print("Данные для входа:")
    print(" Администратор: login=admin, password=admin123")
    print(" Пользователи: login=user1@test.ru ... user8@test.ru")
    print("                  password=123456")
    print("=" * 50)