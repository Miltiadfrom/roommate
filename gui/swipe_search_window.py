"""
Окно поиска со свайпами (Tinder-style)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QGroupBox, QFormLayout,
                             QMessageBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from database import db
from algorithms import compatibility_calculator
from models import Profile

class SwipeCard(QFrame):
    def __init__(self, profile, compatibility_score):
        super().__init__()
        self.profile = profile
        self.compatibility_score = compatibility_score
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 550)
        self.setStyleSheet("QFrame { background-color: white; border-radius: 15px; border: 1px solid #ddd; }")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        photo_frame = QFrame()
        photo_frame.setFixedHeight(200)
        photo_frame.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
            }
        """)
        photo_layout = QVBoxLayout()
        photo_layout.setAlignment(Qt.AlignCenter)

        initials = "".join([name[0] for name in self.profile.full_name.split()[:2]])
        photo_label = QLabel(initials)
        photo_label.setFont(QFont('Arial', 60, QFont.Bold))
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet('color: white;')
        photo_layout.addWidget(photo_label)

        photo_frame.setLayout(photo_layout)
        layout.addWidget(photo_frame)

        name_label = QLabel(f"{self.profile.full_name}, {self.profile.age}")
        name_label.setFont(QFont('Arial', 20, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        compat_label = QLabel(f"💕 Совместимость: {self.compatibility_score}%")
        compat_label.setFont(QFont('Arial', 14, QFont.Bold))
        compat_label.setAlignment(Qt.AlignCenter)
        if self.compatibility_score >= 80:
            compat_label.setStyleSheet('color: #4CAF50;')
        elif self.compatibility_score >= 60:
            compat_label.setStyleSheet('color: #FF9800;')
        else:
            compat_label.setStyleSheet('color: #F44336;')
        layout.addWidget(compat_label)

        info_group = QGroupBox('📋 Информация')
        info_layout = QFormLayout()
        info_layout.addRow('📍 Район:', QLabel(', '.join(self.profile.preferred_districts[:2]) or 'Не указано'))
        info_layout.addRow('💰 Бюджет:', QLabel(f"{self.profile.budget_min}-{self.profile.budget_max} руб."))
        info_layout.addRow('🏠 Тип:', QLabel(self.profile.housing_type or 'Не указано'))
        info_layout.addRow('🕐 Распорядок:', QLabel(self.profile.daily_schedule or 'Не указано'))
        info_layout.addRow('🧹 Чистота:', QLabel(f"{self.profile.cleanliness_level}/10"))
        info_layout.addRow('🔇 Шум:', QLabel(f"{self.profile.noise_tolerance}/10"))

        habits = []
        if self.profile.smoking:
            habits.append('🚬 Курит')
        if self.profile.alcohol:
            habits.append('🍷 Алкоголь')
        if self.profile.has_pets:
            habits.append('🐾 Животные')
        info_layout.addRow('⚠️ Привычки:', QLabel(', '.join(habits) if habits else 'Нет вредных'))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        if self.profile.hobbies:
            hobbies_label = QLabel('🎯 Хобби: ' + ', '.join(self.profile.hobbies[:3]))
            hobbies_label.setWordWrap(True)
            hobbies_label.setStyleSheet('color: #666;')
            layout.addWidget(hobbies_label)

        if self.profile.occupation:
            job_label = QLabel(f'💼 {self.profile.occupation}')
            job_label.setStyleSheet('color: #666; font-style: italic;')
            layout.addWidget(job_label)

        self.setLayout(layout)

class SwipeSearchWindow(QWidget):
    def __init__(self, user, on_match):
        super().__init__()
        self.user = user
        self.on_match = on_match
        self.user_profile = db.get_profile(user.id)
        self.current_candidate = None
        self.init_ui()
        self._load_candidate()

    def init_ui(self):
        self.setWindowTitle('Поиск соседей (Свайп)')
        self.setMinimumSize(500, 700)
        self.setStyleSheet("QWidget { background-color: #f5f5f5; }")

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel('🔍 Найди идеального соседа')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: #666; font-size: 12px;')
        layout.addWidget(self.status_label)

        self.card_container = QFrame()
        self.card_container.setMinimumHeight(550)
        self.card_container.setStyleSheet('background-color: transparent;')
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)
        self.card_container.setLayout(card_layout)
        layout.addWidget(self.card_container)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(25)

        self.dislike_btn = QPushButton('✕')
        self.dislike_btn.setObjectName('dislike')
        self.dislike_btn.setFixedSize(80, 80)
        self.dislike_btn.setStyleSheet("""
            QPushButton#dislike {
                background-color: #F44336;
                border-radius: 40px;
                font-size: 42px;
                font-weight: bold;
                color: white;
                border: 3px solid white;
            }
            QPushButton#dislike:hover { background-color: #D32F2F; }
        """)
        self.dislike_btn.clicked.connect(self._swipe_left)
        btn_layout.addWidget(self.dislike_btn)

        self.super_btn = QPushButton('❤')
        self.super_btn.setObjectName('super')
        self.super_btn.setFixedSize(70, 70)
        self.super_btn.setStyleSheet("""
            QPushButton#super {
                background-color: #2196F3;
                border-radius: 35px;
                font-size: 36px;
                font-weight: bold;
                color: white;
                border: 3px solid white;
            }
            QPushButton#super:hover { background-color: #1976D2; }
        """)
        self.super_btn.clicked.connect(self._swipe_up)
        btn_layout.addWidget(self.super_btn)

        self.like_btn = QPushButton('✓')
        self.like_btn.setObjectName('like')
        self.like_btn.setFixedSize(80, 80)
        self.like_btn.setStyleSheet("""
            QPushButton#like {
                background-color: #4CAF50;
                border-radius: 40px;
                font-size: 42px;
                font-weight: bold;
                color: white;
                border: 3px solid white;
            }
            QPushButton#like:hover { background-color: #43A047; }
        """)
        self.like_btn.clicked.connect(self._swipe_right)
        btn_layout.addWidget(self.like_btn)

        layout.addLayout(btn_layout)

        labels_layout = QHBoxLayout()
        labels_layout.setAlignment(Qt.AlignCenter)
        labels_layout.setSpacing(25)

        dislike_label = QLabel('Не подходит')
        dislike_label.setStyleSheet('color: #F44336; font-size: 11px;')
        dislike_label.setMinimumWidth(80)
        dislike_label.setAlignment(Qt.AlignCenter)
        labels_layout.addWidget(dislike_label)

        super_label = QLabel('Супер-лайк')
        super_label.setStyleSheet('color: #2196F3; font-size: 11px;')
        super_label.setMinimumWidth(70)
        super_label.setAlignment(Qt.AlignCenter)
        labels_layout.addWidget(super_label)

        like_label = QLabel('Подходит')
        like_label.setStyleSheet('color: #4CAF50; font-size: 11px;')
        like_label.setMinimumWidth(80)
        like_label.setAlignment(Qt.AlignCenter)
        labels_layout.addWidget(like_label)

        layout.addLayout(labels_layout)

        refresh_btn = QPushButton('🔄 Обновить кандидатов')
        refresh_btn.setStyleSheet('background-color: #9E9E9E; color: white; padding: 10px; border-radius: 5px;')
        refresh_btn.clicked.connect(self._load_candidate)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _load_candidate(self):
        if not self.user_profile:
            self.status_label.setText('⚠️ Сначала заполните анкету')
            QMessageBox.warning(self, 'Предупреждение', 'Сначала заполните анкету для поиска соседей')
            return

        all_profiles = db.get_all_profiles(exclude_user_id=self.user.id)
        candidate = db.get_next_candidate(self.user.id)

        if candidate:
            self.current_candidate = candidate
            score, _ = compatibility_calculator.calculate_compatibility(self.user_profile, candidate)

            while self.card_container.layout().count():
                item = self.card_container.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            card = SwipeCard(candidate, score)
            self.card_container.layout().addWidget(card)

            swiped_count = self._count_swiped()
            remaining = len(all_profiles) - swiped_count
            self.status_label.setText(f'📊 Осталось кандидатов: {remaining} из {len(all_profiles)}')
        else:
            self.status_label.setText('✅ Все кандидаты просмотрены!')
            self.current_candidate = None

    def _count_swiped(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM swipes WHERE user_id = ?', (self.user.id,))
            return cursor.fetchone()[0]

    def _swipe_left(self):
        if self.current_candidate:
            db.add_swipe(self.user.id, self.current_candidate.user_id, 'left')
            self._load_candidate()

    def _swipe_right(self):
        if self.current_candidate:
            db.add_swipe(self.user.id, self.current_candidate.user_id, 'right')
            matches = db.get_matches(self.user.id)
            for match_id, name in matches:
                if match_id == self.current_candidate.user_id:
                    self.on_match(self.current_candidate)
                    break
            self._load_candidate()

    def _swipe_up(self):
        if self.current_candidate:
            db.add_swipe(self.user.id, self.current_candidate.user_id, 'up')
            self._load_candidate()

    def closeEvent(self, event):
        """Обработка закрытия окна свайп-поиска"""
        # Удаляем из списка родительского окна если есть
        parent = self.parent()
        if parent and hasattr(parent, 'child_windows'):
            if self in parent.child_windows:
                parent.child_windows.remove(self)
        event.accept()