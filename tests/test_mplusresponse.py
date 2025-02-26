import pytest
import requests
from unittest.mock import MagicMock
from mpluspy import MPlusResponse


@pytest.fixture
def mock_xml_response():
    response = MagicMock(spec=requests.Response)
    response.headers = {"Content-Type": "application/xml"}
    response.text = """<?xml version=\'1.0\' encoding=\'UTF-8\'?>
    <application
        xmlns="http://www.zetcom.com/ria/ws/module">
        <modules>
            <module name="Multimedia" totalSize="2">
                <moduleItem hasAttachments="true" id="123" uuid="faf674a0-a7b5-4aea-83a4-5f7913827d91">
                    <systemField dataType="Long" name="__id">
                        <value>123</value>
                    </systemField>
                </moduleItem>
                <moduleItem hasAttachments="true" id="456" uuid="c55372ae-287a-4636-9dd0-e14ed3cc36a2">
                    <systemField dataType="Long" name="__id">
                        <value>456</value>
                    </systemField>
                </moduleItem>
            </module>
        </modules>
    </application>"""
    return response


@pytest.fixture
def mock_non_xml_response():
    response = MagicMock(spec=requests.Response)
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"key": "value"}'
    return response


def test_xml_to_dict(mock_xml_response):
    mplus_response = MPlusResponse(mock_xml_response)
    parsed_data = mplus_response.xml_to_dict()
    assert parsed_data is not None
    assert "application" in parsed_data
    assert "modules" in parsed_data["application"]


def test_xml_to_dict_invalid_content(mock_non_xml_response):
    mplus_response = MPlusResponse(mock_non_xml_response)
    assert mplus_response.xml_to_dict() is None


def test_parse_IDs(mock_xml_response):
    mplus_response = MPlusResponse(mock_xml_response)
    ids = mplus_response.parse_IDs()
    assert ids == ["123", "456"]


def test_parse_IDs_invalid_content(mock_non_xml_response):
    mplus_response = MPlusResponse(mock_non_xml_response)
    assert mplus_response.parse_IDs() is None


def test_parse_size(mock_xml_response):
    mplus_response = MPlusResponse(mock_xml_response)
    size = mplus_response.parse_size()
    assert size == 2


def test_parse_size_invalid_content(mock_non_xml_response):
    mplus_response = MPlusResponse(mock_non_xml_response)
    assert mplus_response.parse_size() is None
