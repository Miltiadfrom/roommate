"""
GUI модули приложения
"""
from .login_window import LoginWindow
from .main_window import MainWindow
from .admin_window import AdminWindow
from .questionnaire_window import QuestionnaireWindow
from .swipe_search_window import SwipeSearchWindow
from .search_window import SearchWindow
from .chat_window import ChatWindow

__all__ = [
    'LoginWindow',
    'MainWindow',
    'AdminWindow',
    'QuestionnaireWindow',
    'SwipeSearchWindow',
    'SearchWindow',
    'ChatWindow'
]