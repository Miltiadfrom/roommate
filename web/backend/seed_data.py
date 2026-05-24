import sqlite3
from datetime import datetime, timedelta
from passlib.context import CryptContext
import random

# Настройки
DB_PATH = "roommate.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_tables():
    """Создает все необходимые таблицы в базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица профилей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            full_name TEXT,
            occupation TEXT,
            budget REAL,
            preferred_district TEXT,
            cleanliness INTEGER,
            noise_level INTEGER,
            schedule_type INTEGER,
            social_habits INTEGER,
            about TEXT,
            personality TEXT,
            smoking_habits TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Таблица свайпов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_user_id INTEGER NOT NULL,
            is_like BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, target_user_id)
        )
    """)
    
    # Таблица мэтчей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Таблица сообщений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    print("Таблицы созданы.")

def seed_database():
    # Сначала создаем все таблицы, если их нет
    create_tables()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Очистка существующих данных (опционально, можно закомментировать если нужно сохранять данные)
    # cursor.execute("DELETE FROM messages")
    # cursor.execute("DELETE FROM swipes")
    # cursor.execute("DELETE FROM matches")
    # cursor.execute("DELETE FROM profiles")
    # cursor.execute("DELETE FROM users")

    # 1. Создаем пользователей
    users_data = [
        ("alice", "alice@example.com", hash_password("123456"), "active"),
        ("bob", "bob@example.com", hash_password("123456"), "active"),
        ("charlie", "charlie@example.com", hash_password("123456"), "active"),
        ("diana", "diana@example.com", hash_password("123456"), "active"),
        ("eve", "eve@example.com", hash_password("123456"), "active"),
        ("frank", "frank@example.com", hash_password("123456"), "active"),
    ]

    user_ids = {}
    for username, email, pwd_hash, status in users_data:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, status) VALUES (?, ?, ?, ?)",
            (username, email, pwd_hash, status)
        )
        user_ids[username] = cursor.lastrowid

    print(f"Создано пользователей: {len(user_ids)}")

    # 2. Создаем профили с разными характеристиками для проверки алгоритмов
    profiles_data = [
        # Alice: Чистюля, ранний подъем, бюджет 50к, Центр
        (user_ids["alice"], "Алиса, 23", "Студентка", 50000, "Центральный", 5, 5, 1, 1, "Люблю порядок и тишину. Ложусь в 22:00.", "introvert", "non-smoker"),
        # Bob: Спокойный, бюджет 50к, Центр (Мэтч с Алисой)
        (user_ids["bob"], "Борис, 24", "Разработчик", 55000, "Центральный", 4, 4, 2, 2, "Работаю из дома, ценю уют.", "ambivert", "non-smoker"),
        # Charlie: Тусовщик, шумный, бюджет 30к, Север (Не мэтч с Алисой)
        (user_ids["charlie"], "Чарли, 22", "Музыкант", 30000, "Северный", 2, 1, 5, 5, "Люблю вечеринки и гостей. Ложусь под утро.", "extrovert", "smoker"),
        # Diana: Умеренная, бюджет 40к, Юг
        (user_ids["diana"], "Диана, 25", "Дизайнер", 40000, "Южный", 3, 3, 3, 3, "Ищу спокойных соседей.", "ambivert", "non-smoker"),
        # Eve: Чистюля, бюджет 60к, Запад (Потенциальный мэтч с Алисой)
        (user_ids["eve"], "Ева, 23", "Маркетолог", 60000, "Западный", 5, 4, 2, 2, "Чистота - залог здоровья.", "introvert", "non-smoker"),
        # Frank: Бюджетник, любой район
        (user_ids["frank"], "Франк, 21", "Студент", 25000, "Любой", 2, 2, 4, 4, "Неприхотливый в быту.", "extrovert", "social-smoker"),
    ]

    profile_ids = {}
    for data in profiles_data:
        uid = data[0]
        cursor.execute("""
            INSERT INTO profiles (user_id, full_name, occupation, budget, preferred_district, 
            cleanliness, noise_level, schedule_type, social_habits, about, personality, smoking_habits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        profile_ids[uid] = cursor.lastrowid

    print(f"Создано профилей: {len(profile_ids)}")

    # 3. Создаем свайпы и мэтчи
    now = datetime.now()
    
    # Мэтч между Alice и Bob (взаимные лайки)
    # Alice likes Bob
    cursor.execute("INSERT INTO swipes (user_id, target_user_id, is_like, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["alice"], user_ids["bob"], 1, now))
    # Bob likes Alice
    cursor.execute("INSERT INTO swipes (user_id, target_user_id, is_like, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["bob"], user_ids["alice"], 1, now - timedelta(hours=1)))
    # Создаем мэтч
    cursor.execute("INSERT INTO matches (user1_id, user2_id, created_at) VALUES (?, ?, ?)",
                   (user_ids["alice"], user_ids["bob"], now))
    
    # Мэтч между Alice и Eve (взаимные лайки)
    cursor.execute("INSERT INTO swipes (user_id, target_user_id, is_like, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["alice"], user_ids["eve"], 1, now - timedelta(days=1)))
    cursor.execute("INSERT INTO swipes (user_id, target_user_id, is_like, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["eve"], user_ids["alice"], 1, now - timedelta(days=1, hours=2)))
    cursor.execute("INSERT INTO matches (user1_id, user2_id, created_at) VALUES (?, ?, ?)",
                   (user_ids["alice"], user_ids["eve"], now - timedelta(days=1)))

    # Charlie лайкает Diana, но без ответа (нет мэтча)
    cursor.execute("INSERT INTO swipes (user_id, target_user_id, is_like, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["charlie"], user_ids["diana"], 1, now))
    
    # Frank лайкает всех, но ему никто не лайкнул в ответ
    for uid in [user_ids["alice"], user_ids["bob"], user_ids["diana"]]:
        cursor.execute("INSERT INTO swipes (user_id, target_user_id, is_like, created_at) VALUES (?, ?, ?, ?)",
                       (user_ids["frank"], uid, 1, now))

    print("Свайпы и мэтчи созданы.")

    # 4. Добавляем сообщения в чат между Alice и Bob
    messages = [
        (user_ids["alice"], user_ids["bob"], "Привет! Я увидела твой профиль, нам нравится один район.", now - timedelta(minutes=30)),
        (user_ids["bob"], user_ids["alice"], "Привет, Алиса! Да, Центр очень удобен для работы. Ты давно ищешь соседа?", now - timedelta(minutes=25)),
        (user_ids["alice"], user_ids["bob"], "Пару дней. Важно, чтобы человек был аккуратным. Как у тебя с этим?", now - timedelta(minutes=20)),
        (user_ids["bob"], user_ids["alice"], "Я довольно чистоплотен, убираюсь по выходным. А ты любишь гостей?", now - timedelta(minutes=15)),
        (user_ids["alice"], user_ids["bob"], "Редко, в основном тихие вечера. Может встретимся посмотреть квартиру?", now - timedelta(minutes=10)),
        (user_ids["bob"], user_ids["alice"], "Отличная идея! Я свободен завтра после 18:00.", now - timedelta(minutes=5)),
    ]

    for sender_id, receiver_id, text, timestamp in messages:
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, created_at, is_read)
            VALUES (?, ?, ?, ?, ?)
        """, (sender_id, receiver_id, text, timestamp, 1 if timestamp < now - timedelta(minutes=10) else 0))

    print("Сообщения добавлены.")

    conn.commit()
    conn.close()
    print("\n✅ База данных успешно наполнена тестовыми данными!")
    print("\nЛогин для теста: alice / 123456")
    print("У вас есть 2 мэтча: с Boris и Eva.")
    print("В чате с Boris есть переписка.")

if __name__ == "__main__":
    seed_database()
