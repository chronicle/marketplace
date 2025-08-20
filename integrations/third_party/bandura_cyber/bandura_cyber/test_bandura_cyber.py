import pytest
from unittest.mock import patch, MagicMock
from ...core import BanduraCyberManager

from packages.integration_testing.src.integration_testing.set_meta import set_metadata

class test_bandura_cyber:
@set_metadata(parameters=(API Root=))


def manager():
    with patch("BanduraCyber.core.BanduraCyberManager.requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "accessToken": "test-access-token",
            "refreshToken": "test-refresh-token"
        }
        mock_post.return_value = mock_response

        return BanduraCyberManager(username="user", password="pass", verify_ssl=False)


def test_login_sets_tokens(manager):
    assert manager.access_token == "test-access-token"
    assert manager.refresh_token == "test-refresh-token"
    assert manager.session.headers["Authorization"] == "Bearer test-access-token"


def test_logout(manager):
    with patch.object(manager.session, "post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.return_value = None

        result = manager.logout()
        assert result is True
        assert mock_post.called


def test_get_api_token(manager):
    with patch.object(manager.session, "get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"token": "api-token"}

        token = manager.get_api_token()
        assert token == "api-token"


def test_show_denied_ip_list(manager):
    with patch.object(manager.session, "get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"name": "blocklist", "uuid": "1234"}]

        result = manager.show_denied_ip_list(list_name="blocklist")
        assert result[0]["uuid"] == "1234"


def test_add_denied_ip_entity(manager):
    with patch.object(manager, "show_denied_ip_list") as mock_list, \
         patch.object(manager.session, "post") as mock_post:

        mock_list.return_value = [{"uuid": "abcd-1234"}]
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        result = manager.add_denied_ip_entity("test-list", "8.8.8.8", "32")
        assert result["success"] is True
        assert mock_post.called


def test_validate_response_success():
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    # Should not raise
    BanduraCyberManager.validate_response(mock_response)


def test_validate_response_failure():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        response=MagicMock(content=b"Error content")
    )
    with pytest.raises(BanduraCyberException):
        BanduraCyberManager.validate_response(mock_response)


def test_filter_list_by_name_found():
    data = [{"name": "mylist", "uuid": "u1"}, {"name": "otherlist", "uuid": "u2"}]
    result = BanduraCyberManager.filter_list_by_name("mylist", data)
    assert result == [{"name": "mylist", "uuid": "u1"}]


def test_filter_list_by_name_not_found():
    data = [{"name": "mylist", "uuid": "u1"}]
    result = BanduraCyberManager.filter_list_by_name("nonexistent", data)
    assert result is None


