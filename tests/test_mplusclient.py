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
        "example-request-1": {
            "type": "POST",
            "url": "ria-ws/application/example",
            "headers": {
                "Content-Type": "application/xml",
                "Accept": "application/xml"
            },
            "xml-body": "example-1.xml"
        },
        "example-request-2": {
            "type": "POST",
            "url": "ria-ws/application/example/{id}",
            "headers": {},
            "xml-body": "example-2.xml"
        },
        "example-request-3": {
            "type": "POST",
            "url": "ria-ws/application/example",
            "headers": {},
            "xml-body": "config/invalid.xml"
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

    mock_xml = {
        "example-1.xml": """<application xmlns="http://www.zetcom.com/ria/ws/module/search">
                            <modules>
                                <module name="Multimedia">
                                    <search">
                                    </search>
                                </module>
                            </modules>
                        </application>
                        """,
        "example-2.xml": """<application xmlns="http://www.zetcom.com/ria/ws/module/search">
                            <modules>
                                <module name="Multimedia">
                                    <search limit="{limit}" offset="{offset}">
                                    </search>
                                </module>
                            </modules>
                        </application>
                        """,
    }
    
    # Create a mock that intercepts the open call and returns the appropriate content
    def mock_open_xml(file, mode):
        if file in mock_xml:
            return mock_open(read_data=mock_xml[file]).return_value
        else:
            raise FileNotFoundError(f"File {file} not found")
        
    with patch("builtins.open", mock_open_xml):
        yield mock_xml

def test_request_success(mock_mplus_client, mock_request, mock_response, mock_xml_file):
    mock_request.return_value = mock_response
    response = mock_mplus_client.request("example-request-1")
    assert isinstance(response, MPlusResponse)
    assert response.status_code == 200
    assert "Success" in response.text

def test_request_invalid(mock_mplus_client):
    with pytest.raises(KeyError):
        mock_mplus_client.request("invalid-request")

def test_request_with_placeholders(mock_mplus_client, mock_request, mock_response, mock_xml_file):
    mock_request.return_value = mock_response
    url_placeholders = {"id": 123}
    xml_placeholders = {"limit": 10, "offset": 0}
    response = mock_mplus_client.request("example-request-2", xml_placeholders=xml_placeholders, url_placeholders=url_placeholders)
    assert isinstance(response, MPlusResponse)
    assert response.status_code == 200

def test_request_with_invalid_url_placeholder(mock_mplus_client, mock_xml_file):
    url_placeholders = {"foo": "bar"}
    xml_placeholders = {"limit": "10", "offset": "0"}
    with pytest.raises(KeyError):
        mock_mplus_client.request("example-request-2", xml_placeholders=xml_placeholders, url_placeholders=url_placeholders)


def test_request_with_invalid_xml_placeholder(mock_mplus_client, mock_xml_file):
    url_placeholders = {"id": 123}
    xml_placeholders = {"foo": "bar"}
    with pytest.raises(KeyError):
        mock_mplus_client.request("example-request-2", xml_placeholders=xml_placeholders, url_placeholders=url_placeholders)


def test_request_with_invalid_xml_file(mock_mplus_client, mock_xml_file):
    mock_request.return_value = mock_response
    with pytest.raises(FileNotFoundError):
        mock_mplus_client.request("example-request-3")

def test_format_timestamp():
    timestamp = datetime(2023, 5, 17, 12, 30, 45, 123456)
    formatted = MPlusClient.format_timestamp(timestamp)
    assert formatted == "2023-05-17T12:30:45.123Z"

def test_request_url(mock_mplus_client):
    url = mock_mplus_client._MPlusClient__request_url("example-request-1")
    assert url == "https://example.zetcom.com/MpWeb/ria-ws/application/example"

    url = mock_mplus_client._MPlusClient__request_url("example-request-1", placeholders={'key': 'value'})
    assert url == "https://example.zetcom.com/MpWeb/ria-ws/application/example"

def test_request_url_with_placeholders(mock_mplus_client):
    url = mock_mplus_client._MPlusClient__request_url("example-request-2", placeholders={'id': '123'})
    assert url == "https://example.zetcom.com/MpWeb/ria-ws/application/example/123"

def test_request_url_missing_placeholders(mock_mplus_client):
    with pytest.raises(KeyError):
        mock_mplus_client._MPlusClient__request_url("example-request-2", placeholders={'key': 'value'})
