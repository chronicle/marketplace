class MockMath:
    def math_arithmetic(self, request):
        """Выполняет арифметические операции: сложение, вычитание, умножение, деление."""
        num1 = request.get("num1")
        num2 = request.get("num2")
        operation = request.get("operation")

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
