import pytest
import requests
import yaml
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime
from mpluspy import MPlusClient, MPlusResponse

@pytest.fixture
def mock_config():
    return {
        "baseurl": "https://example.zetcom.com/MpWeb/",
        "example-request": {
            "type": "POST",
            "url": "ria-ws/application/module/Multimedia/search",
            "headers": {
                "Content-Type": "application/xml",
                "Accept": "application/xml"
            },
            "xml-body": "config/MultimediaSearch.xml"
        }
    }

@pytest.fixture
def mock_mplus_client(mock_config):
    with patch("builtins.open", mock_open(read_data=yaml.dump(mock_config))):
        return MPlusClient("config.yml")

@pytest.fixture
def mock_response():
    response = MagicMock(spec=requests.Response)
    response.status_code = 200
    response.text = "<response>Success</response>"
    return response

@pytest.fixture
def mock_request():
    with patch("requests.request") as mock_request:
        yield mock_request

@pytest.fixture
def mock_xml_file():
    with patch("builtins.open", mock_open(read_data="<xml>Mock XML Content</xml>")):
        yield

def test_request_success(mock_mplus_client, mock_request, mock_response, mock_xml_file):
    mock_request.return_value = mock_response
    response = mock_mplus_client.request("example-request")
    assert isinstance(response, MPlusResponse)
    assert response.status_code == 200
    assert "Success" in response.text

def test_request_invalid_key(mock_mplus_client):
    with pytest.raises(KeyError):
        mock_mplus_client.request("invalid-request")

def test_request_with_placeholders(mock_mplus_client, mock_request, mock_response, mock_xml_file):
    mock_request.return_value = mock_response
    url_placeholders = {"id": 123}
    response = mock_mplus_client.request("example-request", url_placeholders=url_placeholders)
    assert isinstance(response, MPlusResponse)
    assert response.status_code == 200

def test_format_timestamp():
    timestamp = datetime(2023, 5, 17, 12, 30, 45, 123456)
    formatted = MPlusClient.format_timestamp(timestamp)
    assert formatted == "2023-05-17T12:30:45.123Z"

def test_request_url(mock_mplus_client):
    url = mock_mplus_client._MPlusClient__request_url("example-request", placeholders={})
    assert url == "https://example.zetcom.com/MpWeb/ria-ws/application/module/Multimedia/search"
