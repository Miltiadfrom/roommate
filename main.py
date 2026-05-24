"""
Точка входа в приложение
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.main_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Roommate Finder')
        self.setMinimumSize(400, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)

        # Стек для переключения между окнами
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Окно входа
        self.login_window = LoginWindow(self.on_login_success)
        self.stacked_widget.addWidget(self.login_window)

        # Показываем окно входа
        self.stacked_widget.setCurrentWidget(self.login_window)

    def on_login_success(self, user):
        """Обработка успешного входа"""
        self.current_user = user
        self.main_window = MainWindow(user, self.on_logout)
        self.stacked_widget.addWidget(self.main_window)
        self.stacked_widget.setCurrentWidget(self.main_window)
        self.resize(900, 700)

    def on_logout(self):
        """Обработка выхода из аккаунта"""
        self.current_user = None
        self.main_window = None
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.login_window.login_phone.clear()
        self.login_window.login_password.clear()
        self.resize(400, 500)

    def closeEvent(self, event):
        """Закрытие приложения - закрываем всё"""
        event.accept()

def main():
    app = QApplication(sys.argv)

    # Настройка шрифта приложения
    font = QFont('Arial', 10)
    app.setFont(font)

    # Настройка стиля
    app.setStyle('Fusion')

    window = Application()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()