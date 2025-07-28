from ..core.mock_action import MockAction
import arrow


class MockProduct(MockAction):
    def __init__(self):
        # Инициализируем атрибуты для bot_details, чтобы можно было имитировать их установку
        self.bot_details = {}

    def set_bot_details(self, details):
        """Настройка данных для бота."""
        self.bot_details = details

    def xml_to_json(self, request):
        """Преобразует XML в JSON."""
        xml_data = request.parameters.get("xml")
        if not xml_data:
            raise ValueError("Missing XML data")
        return {
            "json_data": {
                "converted": True,
                "input": xml_data
            }
        }

    def math_arithmetic(self, request):
        """Выполняет арифметические операции: сложение, вычитание, умножение, деление."""
        num1 = request.parameters.get("num1")
        num2 = request.parameters.get("num2")
        operation = request.parameters.get("operation")

        if not num1 or not num2 or not operation:
            raise ValueError("Missing parameters")

        if operation == "addition":
            result = num1 + num2
        elif operation == "subtraction":
            result = num1 - num2
        elif operation == "multiplication":
            result = num1 * num2
        elif operation == "division":
            if num2 == 0:
                raise ValueError("Division by zero")
            result = num1 / num2
        else:
            raise ValueError("Invalid operation")

        return {
            "result": result,
            "operation": operation
        }

    def convert_time_format(self, request):
        """Преобразует время в заданный формат."""
        time_input = request.parameters.get("time_input")
        from_format = request.parameters.get("from_format")
        to_format = request.parameters.get("to_format")
        time_delta_in_seconds = request.parameters.get("time_delta_in_seconds", 0)
        timezone = request.parameters.get("timezone")

        if not time_input or not from_format or not to_format:
            raise ValueError("Missing time input or format parameters")

        # Используем библиотеку arrow для преобразования времени
        new_time = arrow.get(time_input, from_format)
        new_time = new_time.shift(seconds=int(time_delta_in_seconds))

        if timezone:
            new_time = new_time.to(timezone)

        result_value = new_time.format(to_format)

        return {
            "result": result_value,
            "time_input": time_input,
            "from_format": from_format,
            "to_format": to_format
        }

    def fail_requests(self) -> None:
        """Метод для имитации неудачных запросов."""
        self.logger.error("Simulated API failure.")
        raise Exception("Simulated API failure.")
