import arrow
import datetime  # Если используете datetime для резервного парсинга
from .mock_math import MockMath  # Импортируем MockMath для арифметических операций
from .mock_time import MockTime  # Импортируем MockTime для работы с временем
from ..core.mock_action import MockAction  # Импортируем MockAction, если это родительский класс для MockProduct


class MockProduct(MockAction):
    def __init__(self):
        self.bot_details = {}
        self.updates_response = {}

        # Инициализируем другие моки
        self.mock_math = MockMath()
        self.mock_time = MockTime()

    def set_bot_details(self, details):
        """Настройка данных для бота."""
        self.bot_details = details

    def set_updates_response(self, response):
        """Настройка мока для ответа с обновлениями."""
        self.updates_response = response

    def xml_to_json(self, request):
        """Преобразует XML в JSON"""
        xml_data = request.get("xml")
        if not xml_data:
            raise ValueError("Missing XML data")
        return {
            "json_data": {
                "converted": True,
                "input": xml_data
            }
        }

    # Мокаем математические операции
    def math_arithmetic(self, request):
        return self.mock_math.math_arithmetic(request)

    # Мокаем преобразование времени
    def convert_time_format(self, request):
        return self.mock_time.convert_time_format(request)
