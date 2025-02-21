import requests
import xmltodict

class MPlusResponse:
    """
    Wrapper for `requests.Response` extending it by some additional helper methods.
    All original response properties are still accessible."""

    def __init__(self, response: requests.Response):
        self._response = response

    def xml_to_dict(self):
        """Parses XML response content into a dictionary using xmltodict."""
        if "xml" in self._response.headers.get("Content-Type", "").lower():
            return xmltodict.parse(self._response.text)
        return None

    def parse_IDs(self):
        """
        Parses response content for moduleItem IDs. If none can be found (e.g. the
        request was no module search request) None is returned
        """
        data = self.xml_to_dict()
        if data:
            result = []
            for item in data['application']['modules']['module']['moduleItem']:
                result.append(item['@id'])
            return result
        return None

    def parse_size(self):
        """
        Parses amount of found moduleItems in response. If none can be found (e.g.
        the request was not a search request) None is returned.
        """
        data = self.xml_to_dict()
        if data:
            return data['application']['modules']['module']['@totalSize']
        return None

    def __getattr__(self, name):
        return getattr(self._response, name)
