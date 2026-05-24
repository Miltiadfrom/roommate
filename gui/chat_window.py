"""
Окно чата
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QLineEdit, QMessageBox, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from database import db
from datetime import datetime

class MessageBubble(QFrame):
    """Виджет сообщения (пузырь)"""
    def __init__(self, content, timestamp, is_mine):
        super().__init__()
        self.is_mine = is_mine
        self.init_ui(content, timestamp)

    def init_ui(self, content, timestamp):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        if self.is_mine:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2196F3;
                    border-radius: 15px;
                    padding: 10px;
                    max-width: 400px;
                }
            """)
            text_color = "white"
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #E0E0E0;
                    border-radius: 15px;
                    padding: 10px;
                    max-width: 400px;
                }
            """)
            text_color = "#333"

        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f'color: {text_color}; font-size: 14px;')
        layout.addWidget(content_label)

        time_label = QLabel(timestamp)
        time_label.setStyleSheet(f'color: {text_color}; font-size: 11px;')
        time_label.setAlignment(Qt.AlignRight)
        layout.addWidget(time_label)

        self.setLayout(layout)

class ChatWindow(QWidget):
    def __init__(self, user, partner_id=None):
        super().__init__()
        self.user = user
        self.partner_id = partner_id
        self.current_chat = None
        self.init_ui()
        self._load_contacts()

        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_messages)
        self.timer.start(5000)

    def init_ui(self):
        self.setWindowTitle('Чат')
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 20px;
                font-size: 13px;
                background-color: #f5f5f5;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setStyleSheet("QFrame { background-color: #f5f5f5; border-bottom: 1px solid #ddd; }")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        title = QLabel('💬 Сообщения')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        header.setLayout(header_layout)
        layout.addWidget(header)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)

        contacts_panel = QFrame()
        contacts_panel.setStyleSheet("QFrame { border-right: 1px solid #ddd; background-color: #ffffff; }")
        contacts_layout = QVBoxLayout()
        contacts_layout.setSpacing(0)
        contacts_layout.setContentsMargins(0, 0, 0, 0)

        contacts_label = QLabel('📋 Контакты')
        contacts_label.setStyleSheet("QLabel { padding: 15px; font-size: 14px; font-weight: bold; border-bottom: 1px solid #eee; }")
        contacts_layout.addWidget(contacts_label)

        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self._on_contact_selected)
        self.contacts_list.setStyleSheet("QListWidget { border: none; outline: none; }")
        contacts_layout.addWidget(self.contacts_list)

        contacts_panel.setLayout(contacts_layout)
        contacts_panel.setMaximumWidth(250)
        main_layout.addWidget(contacts_panel)

        chat_panel = QFrame()
        chat_panel.setStyleSheet("QFrame { background-color: #ffffff; }")
        chat_layout = QVBoxLayout()
        chat_layout.setSpacing(0)
        chat_layout.setContentsMargins(0, 0, 0, 0)

        self.chat_header = QFrame()
        self.chat_header.setStyleSheet("QFrame { background-color: #f5f5f5; border-bottom: 1px solid #ddd; }")
        chat_header_layout = QHBoxLayout()
        chat_header_layout.setContentsMargins(20, 15, 20, 15)
        self.chat_partner_label = QLabel('Выберите контакт для начала чата')
        self.chat_partner_label.setStyleSheet('color: #666; font-size: 14px;')
        chat_header_layout.addWidget(self.chat_partner_label)
        chat_header_layout.addStretch()
        self.chat_header.setLayout(chat_header_layout)
        chat_layout.addWidget(self.chat_header)

        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setStyleSheet("QScrollArea { border: none; background-color: #ffffff; }")

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setSpacing(10)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.addStretch()
        self.messages_container.setLayout(self.messages_layout)
        self.messages_scroll.setWidget(self.messages_container)

        chat_layout.addWidget(self.messages_scroll, stretch=1)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet('background-color: #ddd;')
        separator.setFixedHeight(1)
        chat_layout.addWidget(separator)

        input_panel = QFrame()
        input_panel.setStyleSheet("QFrame { background-color: #f5f5f5; border-top: 1px solid #ddd; }")
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText('Введите сообщение...')
        self.message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.message_input, stretch=1)

        send_btn = QPushButton('➤ Отправить')
        send_btn.setFixedWidth(120)
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        input_panel.setLayout(input_layout)
        chat_layout.addWidget(input_panel)

        chat_panel.setLayout(chat_layout)
        main_layout.addWidget(chat_panel, stretch=1)

        layout.addLayout(main_layout)
        self.setLayout(layout)

    def _load_contacts(self):
        self.contacts_list.clear()
        contacts = db.get_user_contacts(self.user.id)

        if not contacts:
            item = QListWidgetItem('😕 Нет контактов')
            item.setFlags(Qt.NoItemFlags)
            self.contacts_list.addItem(item)
            return

        for contact_id, name in contacts:
            item = QListWidgetItem(f'👤 {name}')
            item.setData(Qt.UserRole, contact_id)
            self.contacts_list.addItem(item)

        if self.partner_id:
            for i in range(self.contacts_list.count()):
                item = self.contacts_list.item(i)
                if item.data(Qt.UserRole) == self.partner_id:
                    self.contacts_list.setCurrentItem(item)
                    break

    def _on_contact_selected(self, item):
        partner_id = item.data(Qt.UserRole)
        if not partner_id:
            return
        self.current_chat = partner_id
        partner_name = item.text().replace('👤 ', '')
        self.chat_partner_label.setText(f'💬 Чат с: {partner_name}')
        self._load_messages()

    def _load_messages(self):
        if not self.current_chat:
            return

        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.messages_layout.addStretch()

        messages = db.get_conversation(self.user.id, self.current_chat)

        for msg in messages:
            is_mine = msg.sender_id == self.user.id
            timestamp = datetime.fromisoformat(msg.timestamp).strftime('%d.%m.%Y %H:%M')
            bubble = MessageBubble(msg.content, timestamp, is_mine)
            if is_mine:
                self.messages_layout.addWidget(bubble, alignment=Qt.AlignRight)
            else:
                self.messages_layout.addWidget(bubble, alignment=Qt.AlignLeft)

        QTimer.singleShot(100, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _send_message(self):
        if not self.current_chat:
            QMessageBox.warning(self, 'Ошибка', 'Выберите контакт для чата')
            return

        content = self.message_input.text().strip()
        if not content:
            return

        db.send_message(self.user.id, self.current_chat, content)
        self.message_input.clear()
        self._load_messages()

    def _refresh_messages(self):
        if self.current_chat:
            self._load_messages()

    def closeEvent(self, event):
        """Обработка закрытия окна чата"""
        # Удаляем из списка родительского окна если есть
        parent = self.parent()
        if parent and hasattr(parent, 'child_windows'):
            if self in parent.child_windows:
                parent.child_windows.remove(self)
        event.accept()