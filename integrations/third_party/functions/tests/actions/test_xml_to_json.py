import pytest
from ..core.session import TestSession


@pytest.fixture
def session() -> TestSession:
    return TestSession()


def test_xml_to_json_success(session: TestSession):
    # Arrange: создаём request с правильным XML
    xml_data = "<e><a>text</a><a>text</a></e>"
    request = session.create_request(parameters={"xml": xml_data})

    # Act: вызываем Action, передаём именно request.parameters (словарь)
    response = session.product.xml_to_json(request.parameters)

    # Assert: проверяем, что конвертация прошла успешно
    assert "json_data" in response
    assert response["json_data"]["converted"] is True
    assert response["json_data"]["input"] == xml_data


def test_xml_to_json_missing_xml(session: TestSession):
    # Arrange: создаём request без xml
    request = session.create_request(parameters={})

    # Act + Assert: должно упасть с ValueError
    with pytest.raises(ValueError, match="Missing XML data"):
        session.product.xml_to_json(request.parameters)


def test_xml_to_json_invalid_xml(session: TestSession):
    # Arrange: создаём request с некорректным XML
    invalid_xml = "<e><a>text</e>"
    request = session.create_request(parameters={"xml": invalid_xml})

    # Act + Assert: должно упасть с ValueError
    with pytest.raises(ValueError, match="Invalid XML format"):
        session.product.xml_to_json(request.parameters)

