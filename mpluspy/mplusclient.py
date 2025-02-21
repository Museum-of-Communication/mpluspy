import requests
import yaml
import datetime
from .mplusresponse import MPlusResponse

class MPlusClient:
    """
    Simple client for Zetcom's MuseumPlus using YAML and XML configuration files to define
    specific requests. This way API calls can be tailored to each application and data model used
    by an MuseumPlus instance (e.g. including custom fields, reports, saved searches etc.)
    """

    def __init__(self, config_file: str, auth=('user', 'pass')):
        """
        Sets up MPlusClient from predefined config.yml.

        Args:
            config_file (str): The filename of a local YAML configuration file.
                This file defines API request settings and the base URL.
            auth (tuple, optional): A tuple containing a username and password.
                Defaults to ('user', 'pass').

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the configuration file is not a valid YAML file or missing required keys.

        Config File Format:
            The YAML configuration file must contain the following keys:

            - **baseurl** (str): The base URL for the API.
            - **<request-name>** (dict): Defines an API request configurations.
              Multiple request definitions can be provided.
                - **type** (str): HTTP method, e.g., "POST".
                - **url** (str): API endpoint path, which may contain placeholders like `{id}`.
                - **headers** (dict): HTTP headers, including:
                    - **Content-Type** (str): e.g., "application/xml".
                    - **Accept** (str): e.g., "application/xml".
                - **xml-body** (str, optional): Specifies additional data to be sent for POST requests.
                  Check Zetcom's [Documentation](https://docs.zetcom.com/framework-public/ws/ws-api-module.html)
                  for all available possibilites.

        Usage and URL Placeholders:
            - The request name will be passed as a parameter to `apiRequest(request: str)`.
            - The `url` field can include **named placeholders** (e.g., `{id}`).
            - When calling `apiRequest(request: str, url_placeholders: dict)`, these placeholders will be replaced.
            - Example:
                ```yaml
                get-thumbnail:
                  type: "GET"
                  url: "ria-ws/application/module/Multimedia/{id}/thumbnail"
                  headers:
                    Accept: "application/json"
                ```
            - API call: `client.apiRequest("get-thumbnail", {"id": 123})`
            - This results in a request to:
              `"ria-ws/application/module/Multimedia/123/thumbnail"`

        Example YAML:
            ```yaml
            baseurl: "https://example.zetcom.com/MpWeb/"

            example-request:
              type: "POST"
              url: "ria-ws/application/module/Multimedia/search"
              headers:
                Content-Type: "application/xml"
                Accept: "application/xml"
              xml-body: "config/MultimediaSearch.xml"

            another-request:
              type: "GET"
              url: "ria-ws/application/module/Multimedia/{id}/thumbnail"
              headers:
                Content-Type: "application/octet-stream"
            ```
        """
        self.auth = auth
        with open(config_file, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def request(self, request: str, url_placeholders: dict = {}, xml_placeholders: dict = {}):
        """
        Executes configured request to MuseumPlus API and returns a `MPlusResponse` object wrapping `requests.Response`

        Args:
            request (str): Name of the request as used in the YAML configuration.
            url_placeholders (dict, optional): A dict containing values for placeholders in the request url.
            xml_placeholders (dict, optional): A dict containing values for placeholders in the request xml data.

        Raises:
            KeyError: If the request name does not match the keys in the config file, the config file is not formatted according to
                requirements or placeholders are not matching.
            FileNotFoundError: If an xml file specified in the YAML configuration does not exist.
        """
        method = self.config[request]['type']
        url = self.__request_url(request, placeholders=url_placeholders)
        data = self.__request_data(request, placeholders=xml_placeholders)
        response = requests.request(method, url, data=data, auth=self.auth)
        return MPlusResponse(response)

    @staticmethod
    def format_timestamp(timestamp: datetime.datetime) -> str:
        """Helper for returning formatted timestamp for MPlus API for a given datetime object"""
        return timestamp.strftime('%Y-%m-%dT%H:%M:%S.') + f'{timestamp.microsecond // 1000:03d}Z'

    def __request_url(self, request: str, placeholders: dict = {}):
        url = self.config['baseurl'] + self.config[request]['url']
        return url.format_map(placeholders)

    def __request_data(self, request: str, placeholders: dict = {}):
        if 'xml-body' in self.config[request]:
            with open(self.config[request]['xml-body'], 'r') as f:
                return f.read().format_map(placeholders)
