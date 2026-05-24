"""
Окно администратора
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QGroupBox, QFormLayout, QMessageBox, QHeaderView,
                             QTabWidget, QTextEdit, QListWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from database import db
from datetime import datetime
import os

class AdminWindow(QWidget):
    def __init__(self, user, on_logout):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.init_ui()
        self._load_statistics()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton#danger {
                background-color: #F44336;
            }
            QPushButton#danger:hover {
                background-color: #D32F2F;
            }
            QPushButton#success {
                background-color: #4CAF50;
            }
            QPushButton#success:hover {
                background-color: #45a049;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #eee;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9C27B0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #9C27B0;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel('🔐 Панель администратора')
        title.setFont(QFont('Arial', 22, QFont.Bold))
        title.setStyleSheet('color: #9C27B0;')
        layout.addWidget(title)

        # Табы
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_statistics_tab(), '📊 Статистика')
        self.tabs.addTab(self._create_users_tab(), '👥 Пользователи')
        self.tabs.addTab(self._create_backup_tab(), '💾 Резервные копии')
        self.tabs.addTab(self._create_logs_tab(), '📋 Логи')

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def _create_statistics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Статистика
        stats_group = QGroupBox('Статистика системы')
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.stats = db.get_statistics()

        stats_cards = [
            ('👥 Пользователей', self.stats['total_users']),
            ('📝 Профилей', self.stats['total_profiles']),
            ('💕 Матчей', self.stats['total_matches']),
            ('👆 Свайпов', self.stats['total_swipes']),
            ('💬 Сообщений', self.stats['total_messages'])
        ]

        for title, value in stats_cards:
            card = QGroupBox(title)
            card_layout = QVBoxLayout()
            card_layout.setAlignment(Qt.AlignCenter)
            value_label = QLabel(str(value))
            value_label.setFont(QFont('Arial', 28, QFont.Bold))
            value_label.setStyleSheet('color: #9C27B0;')
            card_layout.addWidget(value_label)
            card.setLayout(card_layout)
            card.setMaximumWidth(150)
            stats_layout.addWidget(card)

        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Кнопки действий
        actions_group = QGroupBox('Действия')
        actions_layout = QHBoxLayout()

        backup_btn = QPushButton('💾 Создать резервную копию')
        backup_btn.setObjectName('success')
        backup_btn.clicked.connect(self._create_backup)
        actions_layout.addWidget(backup_btn)

        seed_btn = QPushButton('📝 Загрузить тестовые данные')
        seed_btn.clicked.connect(self._load_test_data)
        actions_layout.addWidget(seed_btn)

        actions_layout.addStretch()
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Логин', 'Роль', 'Дата регистрации', 'Действия'])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self._load_users_table()

        layout.addWidget(self.users_table)

        # Кнопки
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton('🔄 Обновить')
        refresh_btn.clicked.connect(self._load_users_table)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_backup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Список резервных копий
        backup_group = QGroupBox('Резервные копии базы данных')
        backup_layout = QVBoxLayout()

        self.backup_list = QListWidget()
        self._load_backup_list()
        backup_layout.addWidget(self.backup_list)

        # Кнопки
        btn_layout = QHBoxLayout()

        create_backup_btn = QPushButton('💾 Создать копию')
        create_backup_btn.setObjectName('success')
        create_backup_btn.clicked.connect(self._create_backup)
        btn_layout.addWidget(create_backup_btn)

        restore_btn = QPushButton('⬆️ Восстановить')
        restore_btn.clicked.connect(self._restore_backup)
        btn_layout.addWidget(restore_btn)

        delete_btn = QPushButton('🗑️ Удалить')
        delete_btn.setObjectName('danger')
        delete_btn.clicked.connect(self._delete_backup)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()
        backup_layout.addLayout(btn_layout)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # Информация
        info_label = QLabel('ℹ️ Резервные копии хранятся в папке: data/backups/')
        info_label.setStyleSheet('color: #666;')
        layout.addWidget(info_label)

        widget.setLayout(layout)
        return widget

    def _create_logs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Логи
        logs_group = QGroupBox('Системные логи')
        logs_layout = QVBoxLayout()

        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self._load_logs()
        logs_layout.addWidget(self.logs_display)

        # Кнопки
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton('🔄 Обновить')
        refresh_btn.clicked.connect(self._load_logs)
        btn_layout.addWidget(refresh_btn)

        clear_btn = QPushButton('🗑️ Очистить')
        clear_btn.setObjectName('danger')
        clear_btn.clicked.connect(self._clear_logs)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()
        logs_layout.addLayout(btn_layout)

        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

        widget.setLayout(layout)
        return widget

    def _load_statistics(self):
        """Загрузка статистики"""
        self.stats = db.get_statistics()

    def _load_users_table(self):
        """Загрузка таблицы пользователей"""
        users = db.get_all_users()
        self.users_table.setRowCount(len(users))

        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(i, 1, QTableWidgetItem(user.phone))

            role_item = QTableWidgetItem('👑 Админ' if user.is_admin else '👤 Пользователь')
            if user.is_admin:
                role_item.setForeground(QColor('#9C27B0'))
            self.users_table.setItem(i, 2, role_item)

            date = datetime.fromisoformat(user.created_at).strftime('%d.%m.%Y %H:%M')
            self.users_table.setItem(i, 3, QTableWidgetItem(date))

            # Кнопка удаления (не для админа)
            if not user.is_admin:
                delete_btn = QPushButton('🗑️')
                delete_btn.setStyleSheet('background-color: #F44336; padding: 5px;')
                delete_btn.clicked.connect(lambda checked, uid=user.id: self._delete_user(uid))
                self.users_table.setCellWidget(i, 4, delete_btn)
            else:
                self.users_table.setCellWidget(i, 4, QLabel('—'))

    def _load_backup_list(self):
        """Загрузка списка резервных копий"""
        self.backup_list.clear()
        backups = db.get_backup_list()
        for backup in backups:
            filename = backup.split('/')[-1]
            size = os.path.getsize(backup) / 1024  # KB
            self.backup_list.addItem(f"📁 {filename} ({size:.1f} KB)")

    def _load_logs(self):
        """Загрузка логов"""
        logs = db.get_system_logs(50)
        self.logs_display.clear()

        for log in logs:
            timestamp = datetime.fromisoformat(log.timestamp).strftime('%d.%m.%Y %H:%M:%S')
            self.logs_display.append(f"[{timestamp}] User {log.user_id}: {log.action} - {log.details}")

    def _create_backup(self):
        """Создание резервной копии"""
        backup_path = db.create_backup()
        QMessageBox.information(self, 'Успех', f'Резервная копия создана:\n{backup_path}')
        self._load_backup_list()

    def _restore_backup(self):
        """Восстановление из резервной копии"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите резервную копию')
            return

        reply = QMessageBox.question(self, 'Подтверждение',
                                    'Восстановление заменит текущую базу данных.\nПродолжить?',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            filename = current_item.text().replace('📁 ', '').split(' ')[0]
            backup_path = os.path.join(db.BACKUP_DIR, filename)
            if db.restore_backup(backup_path):
                QMessageBox.information(self, 'Успех', 'База данных восстановлена')
                self._load_statistics()
                self._load_users_table()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось восстановить базу данных')

    def _delete_backup(self):
        """Удаление резервной копии"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Выберите резервную копию')
            return

        reply = QMessageBox.question(self, 'Подтверждение',
                                    'Удалить выбранную резервную копию?',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            filename = current_item.text().replace('📁 ', '').split(' ')[0]
            backup_path = os.path.join(db.BACKUP_DIR, filename)
            try:
                os.remove(backup_path)
                QMessageBox.information(self, 'Успех', 'Резервная копия удалена')
                self._load_backup_list()
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Не удалось удалить: {e}')

    def _delete_user(self, user_id):
        """Удаление пользователя"""
        reply = QMessageBox.question(self, 'Подтверждение',
                                    f'Удалить пользователя ID {user_id}?',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if db.delete_user(user_id):
                QMessageBox.information(self, 'Успех', 'Пользователь удален')
                self._load_users_table()
                self._load_statistics()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить пользователя')

    def _load_test_data(self):
        """Загрузка тестовых данных"""
        reply = QMessageBox.question(self, 'Подтверждение',
                                    'Загрузить тестовые данные?\nЭто создаст 8 тестовых пользователей.',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                import seed_data
                user_ids = seed_data.create_test_users()
                seed_data.create_test_profiles(user_ids)
                QMessageBox.information(self, 'Успех', 'Тестовые данные загружены')
                self._load_statistics()
                self._load_users_table()
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка: {e}')

    def _clear_logs(self):
        """Очистка логов"""
        reply = QMessageBox.question(self, 'Подтверждение',
                                    'Очистить все логи?',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM system_logs')
            QMessageBox.information(self, 'Успех', 'Логи очищены')
            self._load_logs()