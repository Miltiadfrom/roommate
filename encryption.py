"""
Модуль шифрования данных
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from config import ENCRYPTION_KEY_FILE


class EncryptionManager:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)

    def _load_or_create_key(self):
        """Загрузка или создание ключа шифрования"""
        if os.path.exists(ENCRYPTION_KEY_FILE):
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(ENCRYPTION_KEY_FILE, 'wb') as f:
                f.write(key)
            return key

    def encrypt(self, data: str) -> str:
        """Шифрование строки"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """Расшифровка строки"""
        return self.cipher.decrypt(data.encode()).decode()

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return f"{salt.hex()}:{key.decode()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Проверка пароля"""
        try:
            salt_hex, key = hashed.split(':')
            salt = bytes.fromhex(salt_hex)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            computed_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return computed_key.decode() == key
        except:
            return False


# Глобальный экземпляр
encryption_manager = EncryptionManager()