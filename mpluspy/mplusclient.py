import requests
import yaml

class MPlusClient:

    def __init__(self, configFile: str, auth=('user', 'pass')):
        """
        Sets up MPlusClient from predefined config.yml.

        Args:
            configFile (str): The filename of a local YAML configuration file.
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
                - **xml-body** (str, optional): Specifies additional data to be sent with the request.

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
        with open(configFile, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def apiRequest(self, request: str, url_placeholders: dict = {}, xml_placeholders: dict = {})
        url = config['baseurl'] + config[request]
        url = url.format_map(url_placeholders)

    def __get():

    def __post():
        # get request parameters from config
        url = self.BASEURL + config[config_name]['url']
        headers = config[config_name]['headers']

        # get request body and replace placeholders
        with open(config[config_name]['xml-body'], 'r') as f:
            data = f.read().format_map(placeholders)

        return requests.post(url, headers=headers, data=data, auth=self.auth)
