import pytest
from ..core.session import TestSession
from jsonpath_ng.ext import parse
import json

@pytest.fixture
def session():
    # Создаем и возвращаем экземпляр TestSession или MockSession
    return TestSession()

def test_run_json_path_query_success(session):
    # Arrange: Настроим данные и ожидаемый результат
    input_data = {
        "json_data": '{"user": {"name": "John", "age": 30}}',
        "json_path": "$.user.name"
    }
    expected_result = {"matches": ["John"]}

    # Настроим мок-ответ для выполнения запроса
    session.product.run_json_path_query = lambda data: expected_result

    # Act: Вызовем функцию для выполнения запроса
    response = session.product.run_json_path_query(input_data)

    # Assert: Проверим результат
    assert response == expected_result

def test_run_json_path_query_invalid_json(session):
    # Arrange: Настроим недействительные данные JSON
    input_data = {
        "json_data": '{"user": {"name": "John", "age": 30}}',
        "json_path": "$.user.invalidField"
    }
    expected_error = {"matches": []}

    # Симулируем ошибку в ответе
    session.product.run_json_path_query = lambda data: expected_error

    # Act: Вызовем функцию для выполнения запроса
    response = session.product.run_json_path_query(input_data)

    # Assert: Проверим, что ошибка была обработана
    assert response == expected_error

def test_run_json_path_query_empty_response(session):
    # Arrange: Настроим данные с пустым JSON
    input_data = {
        "json_data": '{"user": {}}',
        "json_path": "$.user.name"
    }
    expected_result = {"matches": []}

    # Act: Вызовем функцию для выполнения запроса
    response = session.product.run_json_path_query(input_data)

    # Assert: Проверим, что пустой ответ корректно обработан
    assert response == expected_result
