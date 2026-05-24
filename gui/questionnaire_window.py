"""
Окно анкеты пользователя
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QStackedWidget,
                             QComboBox, QSlider, QCheckBox, QGroupBox,
                             QScrollArea, QFormLayout, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models import Profile
from database import db


class QuestionnaireWindow(QWidget):
    def __init__(self, user, on_complete):
        super().__init__()
        self.user = user
        self.on_complete = on_complete
        self.profile = db.get_profile(user.id) or Profile(user_id=user.id)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Заполнение анкеты')
        self.setMinimumSize(600, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#back {
                background-color: #9e9e9e;
            }
            QPushButton#back:hover {
                background-color: #757575;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4CAF50;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #388E3C;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title = QLabel('Анкета пользователя')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        layout.addWidget(title)

        # Прогресс бар
        self.progress_label = QLabel('Страница 1 из 5')
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        # Стек страниц
        self.stacked_widget = QStackedWidget()

        # Создание страниц
        self.stacked_widget.addWidget(self._create_page1_personal())
        self.stacked_widget.addWidget(self._create_page2_housing())
        self.stacked_widget.addWidget(self._create_page3_habits())
        self.stacked_widget.addWidget(self._create_page4_personality())
        self.stacked_widget.addWidget(self._create_page5_requirements())

        layout.addWidget(self.stacked_widget)

        # Кнопки навигации
        btn_layout = QHBoxLayout()

        self.back_btn = QPushButton('← Назад')
        self.back_btn.setObjectName('back')
        self.back_btn.clicked.connect(self._prev_page)
        self.back_btn.setEnabled(False)

        self.next_btn = QPushButton('Далее →')
        self.next_btn.clicked.connect(self._next_page)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Загрузка существующих данных
        self._load_profile_data()

    def _create_page1_personal(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)

        self.full_name = QLineEdit()
        layout.addRow('ФИО:', self.full_name)

        self.age = QSpinBox()
        self.age.setRange(18, 80)
        layout.addRow('Возраст:', self.age)

        self.gender = QComboBox()
        self.gender.addItems(['', 'Мужской', 'Женский'])
        layout.addRow('Пол:', self.gender)

        self.occupation = QLineEdit()
        layout.addRow('Род деятельности:', self.occupation)

        self.contact_info = QLineEdit()
        layout.addRow('Контакты:', self.contact_info)

        widget.setLayout(layout)
        return widget

    def _create_page2_housing(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Бюджет
        budget_group = QGroupBox('Бюджет (руб/месяц)')
        budget_layout = QHBoxLayout()

        self.budget_min = QSpinBox()
        self.budget_min.setRange(5000, 50000)
        self.budget_min.setValue(5000)

        self.budget_max = QSpinBox()
        self.budget_max.setRange(5000, 50000)
        self.budget_max.setValue(50000)

        budget_layout.addWidget(QLabel('От:'))
        budget_layout.addWidget(self.budget_min)
        budget_layout.addWidget(QLabel('До:'))
        budget_layout.addWidget(self.budget_max)
        budget_group.setLayout(budget_layout)
        layout.addWidget(budget_group)

        # Район
        district_group = QGroupBox('Предпочитаемые районы')
        district_layout = QVBoxLayout()
        self.district_checks = {}
        districts = ['Центральный', 'Советский', 'Кировский', 'Самарский', 'Промышленный']
        for district in districts:
            cb = QCheckBox(district)
            self.district_checks[district] = cb
            district_layout.addWidget(cb)
        district_group.setLayout(district_layout)
        layout.addWidget(district_group)

        # Тип жилья
        housing_group = QGroupBox('Тип жилья')
        housing_layout = QVBoxLayout()
        self.housing_type = QComboBox()
        self.housing_type.addItems(['', 'Квартира', 'Апартаменты', 'Дом', 'Комната'])
        housing_layout.addWidget(self.housing_type)
        housing_group.setLayout(housing_layout)
        layout.addWidget(housing_group)

        # Срок аренды
        period_group = QGroupBox('Срок аренды')
        period_layout = QVBoxLayout()
        self.rental_period = QComboBox()
        self.rental_period.addItems(['', 'От 3 месяцев', 'От 6 месяцев', 'От 1 года', 'Бессрочно'])
        period_layout.addWidget(self.rental_period)
        period_group.setLayout(period_layout)
        layout.addWidget(period_group)

        widget.setLayout(layout)
        return widget

    def _create_page3_habits(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Распорядок дня
        schedule_group = QGroupBox('Распорядок дня')
        schedule_layout = QVBoxLayout()
        self.daily_schedule = QComboBox()
        self.daily_schedule.addItems(['', 'Утро (до 12:00)', 'День (12:00-18:00)', 'Ночь (после 18:00)'])
        schedule_layout.addWidget(self.daily_schedule)
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)

        # Чистота
        cleanliness_group = QGroupBox('Отношение к чистоте (1-10)')
        cleanliness_layout = QVBoxLayout()
        self.cleanliness_slider = QSlider(Qt.Horizontal)
        self.cleanliness_slider.setRange(1, 10)
        self.cleanliness_slider.setValue(5)
        self.cleanliness_label = QLabel('5')
        self.cleanliness_slider.valueChanged.connect(lambda v: self.cleanliness_label.setText(str(v)))
        cleanliness_layout.addWidget(self.cleanliness_slider)
        cleanliness_layout.addWidget(self.cleanliness_label, alignment=Qt.AlignCenter)
        cleanliness_group.setLayout(cleanliness_layout)
        layout.addWidget(cleanliness_group)

        # Шум
        noise_group = QGroupBox('Отношение к шуму (1-10)')
        noise_layout = QVBoxLayout()
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setRange(1, 10)
        self.noise_slider.setValue(5)
        self.noise_label = QLabel('5')
        self.noise_slider.valueChanged.connect(lambda v: self.noise_label.setText(str(v)))
        noise_layout.addWidget(self.noise_slider)
        noise_layout.addWidget(self.noise_label, alignment=Qt.AlignCenter)
        noise_group.setLayout(noise_layout)
        layout.addWidget(noise_group)

        # Вредные привычки
        habits_group = QGroupBox('Вредные привычки')
        habits_layout = QVBoxLayout()
        self.smoking_cb = QCheckBox('Курение')
        self.alcohol_cb = QCheckBox('Алкоголь')
        habits_layout.addWidget(self.smoking_cb)
        habits_layout.addWidget(self.alcohol_cb)
        habits_group.setLayout(habits_layout)
        layout.addWidget(habits_group)

        widget.setLayout(layout)
        return widget

    def _create_page4_personality(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Личностный тип
        personality_group = QGroupBox('Личностный тип (1-интроверт, 10-экстраверт)')
        personality_layout = QVBoxLayout()
        self.personality_slider = QSlider(Qt.Horizontal)
        self.personality_slider.setRange(1, 10)
        self.personality_slider.setValue(5)
        self.personality_label = QLabel('5')
        self.personality_slider.valueChanged.connect(lambda v: self.personality_label.setText(str(v)))
        personality_layout.addWidget(self.personality_slider)
        personality_layout.addWidget(self.personality_label, alignment=Qt.AlignCenter)
        personality_group.setLayout(personality_layout)
        layout.addWidget(personality_group)

        # Хобби
        hobbies_group = QGroupBox('Хобби')
        hobbies_layout = QVBoxLayout()
        self.hobby_checks = {}
        hobbies = ['Спорт', 'Музыка', 'Кино', 'Чтение', 'Игры', 'Путешествия', 'Готовка', 'Технологии']
        for hobby in hobbies:
            cb = QCheckBox(hobby)
            self.hobby_checks[hobby] = cb
            hobbies_layout.addWidget(cb)
        hobbies_group.setLayout(hobbies_layout)
        layout.addWidget(hobbies_group)

        # Животные
        pets_group = QGroupBox('Домашние животные')
        pets_layout = QVBoxLayout()
        self.has_pets_cb = QCheckBox('Есть домашние животные')
        pets_layout.addWidget(self.has_pets_cb)
        pets_group.setLayout(pets_layout)
        layout.addWidget(pets_group)

        widget.setLayout(layout)
        return widget

    def _create_page5_requirements(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Пол соседа
        gender_group = QGroupBox('Предпочтительный пол соседа')
        gender_layout = QVBoxLayout()
        self.neighbor_gender = QComboBox()
        self.neighbor_gender.addItems(['Любой', 'Мужской', 'Женский'])
        gender_layout.addWidget(self.neighbor_gender)
        gender_group.setLayout(gender_layout)
        layout.addWidget(gender_group)

        # Возраст соседа
        age_group = QGroupBox('Возрастной диапазон соседа')
        age_layout = QHBoxLayout()
        self.neighbor_age_min = QSpinBox()
        self.neighbor_age_min.setRange(18, 80)
        self.neighbor_age_min.setValue(18)
        self.neighbor_age_max = QSpinBox()
        self.neighbor_age_max.setRange(18, 80)
        self.neighbor_age_max.setValue(60)
        age_layout.addWidget(QLabel('От:'))
        age_layout.addWidget(self.neighbor_age_min)
        age_layout.addWidget(QLabel('До:'))
        age_layout.addWidget(self.neighbor_age_max)
        age_group.setLayout(age_layout)
        layout.addWidget(age_group)

        # Важные критерии
        criteria_group = QGroupBox('Важные критерии')
        criteria_layout = QVBoxLayout()
        self.criteria_checks = {}
        criteria = ['Не курит', 'Не употребляет алкоголь', 'Без животных', 'Чистоплотный', 'Тихий']
        for criterion in criteria:
            cb = QCheckBox(criterion)
            self.criteria_checks[criterion] = cb
            criteria_layout.addWidget(cb)
        criteria_group.setLayout(criteria_layout)
        layout.addWidget(criteria_group)

        widget.setLayout(layout)
        return widget

    def _load_profile_data(self):
        """Загрузка существующих данных профиля"""
        if not self.profile:
            return

        # Страница 1
        self.full_name.setText(self.profile.full_name)
        self.age.setValue(self.profile.age)
        self.gender.setCurrentText(self.profile.gender)
        self.occupation.setText(self.profile.occupation)
        self.contact_info.setText(self.profile.contact_info)

        # Страница 2
        self.budget_min.setValue(self.profile.budget_min)
        self.budget_max.setValue(self.profile.budget_max)
        for district, cb in self.district_checks.items():
            cb.setChecked(district in self.profile.preferred_districts)
        self.housing_type.setCurrentText(self.profile.housing_type)
        self.rental_period.setCurrentText(self.profile.rental_period)

        # Страница 3
        self.daily_schedule.setCurrentText(self.profile.daily_schedule)
        self.cleanliness_slider.setValue(self.profile.cleanliness_level)
        self.cleanliness_label.setText(str(self.profile.cleanliness_level))
        self.noise_slider.setValue(self.profile.noise_tolerance)
        self.noise_label.setText(str(self.profile.noise_tolerance))
        self.smoking_cb.setChecked(self.profile.smoking)
        self.alcohol_cb.setChecked(self.profile.alcohol)

        # Страница 4
        self.personality_slider.setValue(self.profile.personality_type)
        self.personality_label.setText(str(self.profile.personality_type))
        for hobby, cb in self.hobby_checks.items():
            cb.setChecked(hobby in self.profile.hobbies)
        self.has_pets_cb.setChecked(self.profile.has_pets)

        # Страница 5
        self.neighbor_gender.setCurrentText(self.profile.preferred_neighbor_gender or 'Любой')
        self.neighbor_age_min.setValue(self.profile.neighbor_age_min)
        self.neighbor_age_max.setValue(self.profile.neighbor_age_max)
        for criterion, cb in self.criteria_checks.items():
            cb.setChecked(criterion in self.profile.important_criteria)

    def _save_profile_data(self):
        """Сохранение данных профиля"""
        # Страница 1
        self.profile.full_name = self.full_name.text()
        self.profile.age = self.age.value()
        self.profile.gender = self.gender.currentText()
        self.profile.occupation = self.occupation.text()
        self.profile.contact_info = self.contact_info.text()

        # Страница 2
        self.profile.budget_min = self.budget_min.value()
        self.profile.budget_max = self.budget_max.value()
        self.profile.preferred_districts = [d for d, cb in self.district_checks.items() if cb.isChecked()]
        self.profile.housing_type = self.housing_type.currentText()
        self.profile.rental_period = self.rental_period.currentText()

        # Страница 3
        self.profile.daily_schedule = self.daily_schedule.currentText()
        self.profile.cleanliness_level = self.cleanliness_slider.value()
        self.profile.noise_tolerance = self.noise_slider.value()
        self.profile.smoking = self.smoking_cb.isChecked()
        self.profile.alcohol = self.alcohol_cb.isChecked()

        # Страница 4
        self.profile.personality_type = self.personality_slider.value()
        self.profile.hobbies = [h for h, cb in self.hobby_checks.items() if cb.isChecked()]
        self.profile.has_pets = self.has_pets_cb.isChecked()

        # Страница 5
        self.profile.preferred_neighbor_gender = self.neighbor_gender.currentText()
        if self.profile.preferred_neighbor_gender == 'Любой':
            self.profile.preferred_neighbor_gender = ''
        self.profile.neighbor_age_min = self.neighbor_age_min.value()
        self.profile.neighbor_age_max = self.neighbor_age_max.value()
        self.profile.important_criteria = [c for c, cb in self.criteria_checks.items() if cb.isChecked()]

        return db.save_profile(self.profile)

    def _next_page(self):
        current = self.stacked_widget.currentIndex()
        if current < 4:
            # Валидация текущей страницы
            if not self._validate_page(current):
                return
            self.stacked_widget.setCurrentIndex(current + 1)
            self._update_buttons()
        else:
            # Сохранение и завершение
            if self._save_profile_data():
                QMessageBox.information(self, 'Успех', 'Анкета сохранена!')
                self.on_complete()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось сохранить анкету')

    def _prev_page(self):
        current = self.stacked_widget.currentIndex()
        if current > 0:
            self.stacked_widget.setCurrentIndex(current - 1)
            self._update_buttons()

    def _update_buttons(self):
        current = self.stacked_widget.currentIndex()
        self.back_btn.setEnabled(current > 0)
        self.next_btn.setText('Завершить' if current == 4 else 'Далее →')
        self.progress_label.setText(f'Страница {current + 1} из 5')

    def _validate_page(self, page_index):
        """Валидация данных на странице"""
        if page_index == 0:
            if not self.full_name.text().strip():
                QMessageBox.warning(self, 'Ошибка', 'Введите ФИО')
                return False
            if self.age.value() < 18:
                QMessageBox.warning(self, 'Ошибка', 'Возраст должен быть не менее 18 лет')
                return False
        return True