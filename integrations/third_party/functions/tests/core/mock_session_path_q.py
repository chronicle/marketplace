from integration_testing.requests.session import MockSession as BaseMockSession
from ..core.product import Product

class MockProduct(Product):
    def __init__(self, session):
        super().__init__(session)

    def run_json_path_query(self, input_data):
        # Моковая реализация для метода run_json_path_query
        json_data = input_data["json_data"]
        json_path = input_data["json_path"]
        json_result = {"matches": []}

        # Имитация выполнения запроса JSONPath
        if json_path == "$.user.name":
            # Например, если путь запроса это $.user.name
            if "user" in json_data and "name" in json_data["user"]:
                json_result["matches"].append(json_data["user"]["name"])

        # Возвращаем моковый результат
        return json_result

class MockSession(BaseMockSession):
    def __init__(self):
        super().__init__()
        self.product = MockProduct(self)

    def setup_mock_responses(self):
        # Здесь можно добавить другие моки, если необходимо
        pass
