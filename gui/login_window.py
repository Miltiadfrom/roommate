"""
Окно входа и регистрации
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QStackedWidget,
                             QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import db

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Roommate Finder - Вход')
        self.setMinimumSize(450, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 14px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#secondary {
                background-color: #2196F3;
            }
            QPushButton#secondary:hover {
                background-color: #1976D2;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Заголовок
        title = QLabel('🏠 Roommate Finder')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 26, QFont.Bold))
        title.setStyleSheet('color: #4CAF50;')
        layout.addWidget(title)

        subtitle = QLabel('Найди идеального соседа')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont('Arial', 13))
        subtitle.setStyleSheet('color: #666;')
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Стек для переключения между входом и регистрацией
        self.stacked_widget = QStackedWidget()

        # Форма входа
        login_widget = self._create_login_form()
        self.stacked_widget.addWidget(login_widget)

        # Форма регистрации
        register_widget = self._create_register_form()
        self.stacked_widget.addWidget(register_widget)

        layout.addWidget(self.stacked_widget)

        # Кнопки переключения
        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignCenter)

        self.switch_btn = QPushButton('Нет аккаунта? Зарегистрироваться')
        self.switch_btn.setObjectName('secondary')
        self.switch_btn.setMaximumWidth(320)
        self.switch_btn.clicked.connect(self._toggle_form)
        switch_layout.addWidget(self.switch_btn)

        layout.addLayout(switch_layout)
        layout.addStretch()

        # Информация о тестовых данных
        info_label = QLabel('📝 Тест: admin/admin123 | user1@test.ru/123456')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont('Arial', 9))
        info_label.setStyleSheet('color: #999;')
        layout.addWidget(info_label)

        self.setLayout(layout)

    def _create_login_form(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)

        self.login_phone = QLineEdit()
        self.login_phone.setPlaceholderText('Логин (телефон, email или admin)')
        layout.addRow('Логин:', self.login_phone)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText('Пароль')
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addRow('Пароль:', self.login_password)

        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self._handle_login)
        layout.addRow(login_btn)

        widget.setLayout(layout)
        return widget

    def _create_register_form(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)

        self.register_phone = QLineEdit()
        self.register_phone.setPlaceholderText('+7 (___) ___-__-__')
        layout.addRow('Телефон:', self.register_phone)

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText('Пароль')
        self.register_password.setEchoMode(QLineEdit.Password)
        layout.addRow('Пароль:', self.register_password)

        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText('Подтвердите пароль')
        self.register_confirm.setEchoMode(QLineEdit.Password)
        layout.addRow('Подтверждение:', self.register_confirm)

        register_btn = QPushButton('Зарегистрироваться')
        register_btn.clicked.connect(self._handle_register)
        layout.addRow(register_btn)

        widget.setLayout(layout)
        return widget

    def _toggle_form(self):
        if self.stacked_widget.currentIndex() == 0:
            self.stacked_widget.setCurrentIndex(1)
            self.switch_btn.setText('Есть аккаунт? Войти')
        else:
            self.stacked_widget.setCurrentIndex(0)
            self.switch_btn.setText('Нет аккаунта? Зарегистрироваться')

    def _handle_login(self):
        login = self.login_phone.text().strip()
        password = self.login_password.text()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return

        user = db.authenticate_user(login, password)
        if user:
            self.current_user = user
            self.on_login_success(user)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def _handle_register(self):
        phone = self.register_phone.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()

        if not phone or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return

        if password != confirm:
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают')
            return

        if len(password) < 6:
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен быть не менее 6 символов')
            return

        user_id = db.create_user(phone, password)
        if user_id:
            QMessageBox.information(self, 'Успех', 'Регистрация успешна! Теперь войдите.')
            self.stacked_widget.setCurrentIndex(0)
            self.switch_btn.setText('Есть аккаунт? Войти')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь с таким логином уже существует')