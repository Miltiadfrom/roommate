"""
Главное окно приложения
"""
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import db
from .questionnaire_window import QuestionnaireWindow
from .swipe_search_window import SwipeSearchWindow
from .search_window import SearchWindow
from .chat_window import ChatWindow
from .admin_window import AdminWindow

class MainWindow(QMainWindow):
    def __init__(self, user, on_logout_callback):
        super().__init__()
        self.user = user
        self.on_logout_callback = on_logout_callback
        self.child_windows = []  # Список для отслеживания окон
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Roommate Finder - Главная')
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                min-width: 200px;
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
            QPushButton#swipe {
                background-color: #FF9800;
            }
            QPushButton#swipe:hover {
                background-color: #F57C00;
            }
            QPushButton#danger {
                background-color: #F44336;
            }
            QPushButton#danger:hover {
                background-color: #D32F2F;
            }
            QPushButton#admin {
                background-color: #9C27B0;
            }
            QPushButton#admin:hover {
                background-color: #7B1FA2;
            }
        """)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)

        # Заголовок
        if self.user.is_admin:
            title = QLabel('👑 Панель администратора')
            title.setStyleSheet('color: #9C27B0;')
        else:
            title = QLabel(f'Добро пожаловать, {self.user.phone}!')
            title.setStyleSheet('color: #4CAF50;')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel('Найди идеального соседа для совместной аренды жилья')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont('Arial', 14))
        subtitle.setStyleSheet('color: #666;')
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # Если админ - показываем админ панель
        if self.user.is_admin:
            self.admin_window = AdminWindow(self.user, self._logout)
            admin_layout = QVBoxLayout()
            admin_layout.addWidget(self.admin_window)
            layout.addLayout(admin_layout)
        else:
            # Кнопки действий
            btn_layout = QVBoxLayout()
            btn_layout.setSpacing(15)
            btn_layout.setAlignment(Qt.AlignCenter)

            self.questionnaire_btn = QPushButton('📝 Заполнить анкету')
            self.questionnaire_btn.clicked.connect(self._open_questionnaire)
            btn_layout.addWidget(self.questionnaire_btn)

            self.swipe_btn = QPushButton('🔥 Поиск (Свайп)')
            self.swipe_btn.setObjectName('swipe')
            self.swipe_btn.clicked.connect(self._open_swipe_search)
            btn_layout.addWidget(self.swipe_btn)

            self.search_btn = QPushButton('🔍 Поиск (Таблица)')
            self.search_btn.setObjectName('secondary')
            self.search_btn.clicked.connect(self._open_search)
            btn_layout.addWidget(self.search_btn)

            self.chat_btn = QPushButton('💬 Сообщения')
            self.chat_btn.setObjectName('secondary')
            self.chat_btn.clicked.connect(self._open_chat)
            btn_layout.addWidget(self.chat_btn)

            # Кнопка выхода
            logout_btn = QPushButton('🚪 Выйти из аккаунта')
            logout_btn.setObjectName('danger')
            logout_btn.clicked.connect(self._logout)
            btn_layout.addWidget(logout_btn)

            layout.addLayout(btn_layout)
            layout.addStretch()

        central_widget.setLayout(layout)

    def _open_questionnaire(self):
        """Открытие окна анкеты"""
        window = QuestionnaireWindow(self.user, self._on_questionnaire_complete)
        window.setWindowModality(Qt.ApplicationModal)  # Модальное окно
        self.child_windows.append(window)
        window.show()

    def _on_questionnaire_complete(self):
        """Обработка завершения анкеты"""
        QMessageBox.information(self, 'Успех', 'Анкета успешно сохранена!')

    def _open_swipe_search(self):
        """Открытие окна свайп-поиска"""
        profile = db.get_profile(self.user.id)
        if not profile:
            QMessageBox.warning(self, 'Предупреждение',
                              'Сначала заполните анкету для поиска соседей')
            return

        window = SwipeSearchWindow(self.user, self._on_match)
        window.setWindowModality(Qt.NonModal)  # Немодальное окно
        self.child_windows.append(window)
        window.show()

    def _open_search(self):
        """Открытие окна поиска"""
        profile = db.get_profile(self.user.id)
        if not profile:
            QMessageBox.warning(self, 'Предупреждение',
                              'Сначала заполните анкету для поиска соседей')
            return

        window = SearchWindow(self.user, self._on_chat_requested)
        window.setWindowModality(Qt.NonModal)  # Немодальное окно
        self.child_windows.append(window)
        window.show()

    def _open_chat(self):
        """Открытие окна чата"""
        window = ChatWindow(self.user)
        window.setWindowModality(Qt.NonModal)  # Немодальное окно
        self.child_windows.append(window)
        window.show()

    def _on_chat_requested(self, partner_id):
        """Запрос на начало чата"""
        window = ChatWindow(self.user, partner_id)
        window.setWindowModality(Qt.NonModal)  # Немодальное окно
        self.child_windows.append(window)
        window.show()

    def _on_match(self, candidate):
        """Обработка матча"""
        QMessageBox.information(self, '💕 Матч!',
                               f'У вас взаимная симпатия с {candidate.full_name}!\n'
                               f'Можете начать общение в чате.')
        self._open_chat()

    def _logout(self):
        """Выход из аккаунта"""
        # Закрываем все дочерние окна
        for window in self.child_windows[:]:
            try:
                window.close()
            except:
                pass
        self.child_windows.clear()

        self.on_logout_callback()

    def closeEvent(self, event):
        """Закрытие главного окна"""
        # Закрываем все дочерние окна
        for window in self.child_windows[:]:
            try:
                window.close()
            except:
                pass
        self.child_windows.clear()

        self._logout()
        event.accept()
