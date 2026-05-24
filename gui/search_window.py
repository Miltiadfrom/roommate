"""
Окно поиска и подбора соседей (табличный вид)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QGroupBox, QFormLayout, QSlider, QDialog,
                             QSpinBox, QHeaderView)  # ✅ ДОБАВЛЕНО: QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from database import db
from algorithms import compatibility_calculator
from models import Profile

class SearchWindow(QWidget):
    def __init__(self, user, on_chat_requested):
        super().__init__()
        self.user = user
        self.on_chat_requested = on_chat_requested
        self.user_profile = db.get_profile(user.id)
        self.all_candidates = []
        self.filtered_candidates = []
        self.init_ui()
        self._load_candidates()

    def init_ui(self):
        self.setWindowTitle('Поиск соседей')
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            QWidget { background-color: #ffffff; }
            QLabel { font-size: 14px; color: #333; }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton#details { background-color: #4CAF50; padding: 8px 15px; font-size: 12px; }
            QPushButton#details:hover { background-color: #45a049; }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #eee;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel('🔍 Поиск совместимых соседей')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)

        filter_group = QGroupBox('Фильтры')
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)

        budget_layout = QVBoxLayout()
        budget_layout.setSpacing(5)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel('💰 Бюджет:'))

        self.budget_slider = QSlider(Qt.Horizontal)
        self.budget_slider.setRange(5000, 50000)
        self.budget_slider.setValue(50000)
        self.budget_slider.setTickPosition(QSlider.TicksBelow)
        self.budget_slider.setTickInterval(5000)
        self.budget_slider.valueChanged.connect(self._on_budget_slider_changed)
        slider_layout.addWidget(self.budget_slider)

        self.budget_input = QSpinBox()
        self.budget_input.setRange(5000, 50000)
        self.budget_input.setValue(50000)
        self.budget_input.setSingleStep(1000)
        self.budget_input.setSuffix(' руб.')
        self.budget_input.setMinimumWidth(120)
        self.budget_input.valueChanged.connect(self._on_budget_input_changed)
        slider_layout.addWidget(self.budget_input)

        budget_layout.addLayout(slider_layout)

        self.budget_label = QLabel('Макс. бюджет: до 50000 руб.')
        self.budget_label.setStyleSheet('color: #666; font-size: 12px;')
        budget_layout.addWidget(self.budget_label)

        filter_layout.addLayout(budget_layout, stretch=2)

        search_btn = QPushButton('🔍 Найти совместимых')
        search_btn.setMinimumWidth(180)
        search_btn.clicked.connect(self._search_candidates)
        filter_layout.addWidget(search_btn)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['№', 'Имя', '% Совместимости', 'Бюджет', 'Район', 'Действия'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.stats_label = QLabel('')
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet('color: #666; font-size: 12px;')
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def _on_budget_slider_changed(self, value):
        self.budget_input.blockSignals(True)
        self.budget_input.setValue(value)
        self.budget_input.blockSignals(False)
        self.budget_label.setText(f'Макс. бюджет: до {value} руб.')

    def _on_budget_input_changed(self, value):
        self.budget_slider.blockSignals(True)
        self.budget_slider.setValue(value)
        self.budget_slider.blockSignals(False)
        self.budget_label.setText(f'Макс. бюджет: до {value} руб.')

    def _load_candidates(self):
        if not self.user_profile:
            self.stats_label.setText('⚠️ Сначала заполните анкету')
            return

        all_profiles = db.get_all_profiles(exclude_user_id=self.user.id)
        self.all_candidates = []

        for profile in all_profiles:
            score, details = compatibility_calculator.calculate_compatibility(self.user_profile, profile)
            self.all_candidates.append({'profile': profile, 'score': score, 'details': details})

        self.all_candidates.sort(key=lambda x: x['score'], reverse=True)
        self.filtered_candidates = self.all_candidates.copy()
        self._update_table()

    def _search_candidates(self):
        max_budget = self.budget_slider.value()
        self.filtered_candidates = [c for c in self.all_candidates if c['profile'].budget_max <= max_budget]
        self._update_table()

    def _update_table(self):
        self.table.setRowCount(len(self.filtered_candidates))

        for i, candidate in enumerate(self.filtered_candidates):
            profile = candidate['profile']
            score = candidate['score']

            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(profile.full_name or f"User {profile.user_id}"))

            score_item = QTableWidgetItem(f"{score}%")
            score_item.setTextAlignment(Qt.AlignCenter)
            if score >= 80:
                score_item.setForeground(QColor('#4CAF50'))
                score_item.setFont(QFont('Arial', 11, QFont.Bold))
            elif score >= 60:
                score_item.setForeground(QColor('#FF9800'))
                score_item.setFont(QFont('Arial', 11, QFont.Bold))
            else:
                score_item.setForeground(QColor('#F44336'))
            self.table.setItem(i, 2, score_item)

            budget_item = QTableWidgetItem(f"{profile.budget_min}-{profile.budget_max} руб.")
            budget_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, budget_item)

            districts = ', '.join(profile.preferred_districts[:2]) if profile.preferred_districts else 'Не указано'
            district_item = QTableWidgetItem(districts)
            district_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, district_item)

            details_btn = QPushButton('📋 Детали')
            details_btn.setObjectName('details')
            details_btn.setCursor(Qt.PointingHandCursor)
            details_btn.clicked.connect(lambda checked, idx=i: self._show_details(idx))
            self.table.setCellWidget(i, 5, details_btn)

        self.stats_label.setText(f'📊 Показано {len(self.filtered_candidates)} из {len(self.all_candidates)} кандидатов')

    def _show_details(self, index):
        if index >= len(self.filtered_candidates):
            return
        candidate = self.filtered_candidates[index]
        dialog = CompatibilityDialog(candidate, self.user, self.on_chat_requested)
        dialog.exec_()

    def closeEvent(self, event):
        """Обработка закрытия окна поиска"""
        parent = self.parent()
        if parent and hasattr(parent, 'child_windows'):
            if self in parent.child_windows:
                parent.child_windows.remove(self)
        event.accept()

class CompatibilityDialog(QDialog):
    def __init__(self, candidate, user, on_chat_requested):
        super().__init__()
        self.candidate = candidate
        self.user = user
        self.on_chat_requested = on_chat_requested
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Детали совместимости')
        self.setMinimumSize(550, 650)
        layout = QVBoxLayout()

        profile = self.candidate['profile']
        score = self.candidate['score']

        title = QLabel(f"💕 Совместимость: {score}%")
        title.setFont(QFont('Arial', 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        chat_btn = QPushButton('💬 Начать чат')
        chat_btn.clicked.connect(self._start_chat)
        btn_layout.addWidget(chat_btn)

        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _start_chat(self):
        self.on_chat_requested(self.candidate['profile'].user_id)
        self.accept()