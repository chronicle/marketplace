import pytest
from ..core.session import TestSession

@pytest.fixture
def session() -> TestSession:
    return TestSession()

def test_xml_to_json_success(session: TestSession):
    # Arrange: создаём request с правильным XML
    xml_data = "<e><a>text</a><a>text</a></e>"
    request = session.create_request(parameters={"xml": xml_data})

    # Act: вызываем Action
    response = session.product.xml_to_json(request)

    # Assert: проверяем, что конвертация прошла успешно
    assert "json_data" in response
    assert response["json_data"]["converted"] is True
    assert xml_data in response["json_data"]["input"]

def test_xml_to_json_missing_xml(session: TestSession):
    # Arrange: создаём request без xml
    request = session.create_request(parameters={})

    # Act + Assert: должно упасть с ValueError
    with pytest.raises(ValueError, match="Missing XML data"):
        session.product.xml_to_json(request)
