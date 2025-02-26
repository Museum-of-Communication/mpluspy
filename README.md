# mpluspy
`mpluspy` is a Python package intended to work with Zetcom's MuseumPlus API. The API requests are highly configurable, and setup is done using YAML and XML configuration files. This allows tailoring the client to specific use cases and custom data models of any given MuseumPlus instance. The configuration uses a simple schema and follows the official [documentation](https://docs.zetcom.com/framework-public/ws/ws-api-module.html) from Zetcom.

## Installation
Install from this repository:
```shell
$ pip install git+https://github.com/Museum-of-Communication/mpluspy.git
```

## Basic Usage
API requests are configured in a YAML file with additional XML files that are passed to `MPlusClient`:

```python
from mpluspy import MPlusClient
client = MPlusClient("config.yml", auth=("user", "pass")
```

Execute requests defined in the configuration. This returns an `MPlusResponse`:

```python
response = client.request("example-request")
```

## YAML Configuration
The YAML configuration file must contain the following keys:

- **baseurl**: The base URL for the API.
- **\<request-name\>**: Defines an API request configuration.
    - **type**: HTTP method, e.g., "POST".
    - **url**: API endpoint path, which may contain placeholders like `{id}`.
    - **headers**: HTTP headers, including:
        - **Content-Type**: e.g., "application/xml".
        - **Accept**: e.g., "application/xml".
    - **xml-body** (optional): Specifies additional data to be sent for POST requests.
        
**Example YAML:**

```yml
# config.yml

baseurl: "https://example.zetcom.com/MpWeb/" # Use the URL of your MPlus instance here

download-thumbnail:
  # URL using placeholders for ID
  url: "ria-ws/application/module/Multimedia/{id}/thumbnail?size=extra_large"
  headers:
    Content-Type: "application/octet-stream"

multimedia-search:
  type: "POST"
  url: "ria-ws/application/module/Multimedia/search"
  headers:
    Content-Type: "application/xml"
    Accept: "application/xml"
  # Separate XML file defines actual search parameters
  xml-body: "MultimediaSearch.xml"
```

## XML Bodies
The request definitions in the YAML configuration can reference additional XML bodies. These follow Zetcom's [documentation](https://docs.zetcom.com/framework-public/ws/ws-api-module.html). Like the request URLs, you can also use placeholders in the XML bodies.

**Example XML:**

```xml
<!-- MultimediaSearch.xml -->

<application xmlns="http://www.zetcom.com/ria/ws/module/search">
    <modules>
        <module name="Multimedia">
            <search limit="{limit}" offset="{offset}">
                <select>
                    <field fieldPath="__id"/>
                </select>
                <expert>
                    <and>
                        <greaterEquals fieldPath="__lastModified" operand="{timestamp}"/>
                    </and>
                </expert>
            </search>
        </module>
    </modules>
</application>
```

## Using Placeholders
When executing requests with placeholders, you can use dictionaries with values to be replaced. See the following example using the above configurations:

```python
url_placeholders = {"id": 123}

img = client.request("download-thumbnail", url_placeholders=url_placeholders)
```

For some requests, you might need to pass timestamps to the MuseumPlus API. Use the static helper `MPlusClient.format_timestamp()` to get the proper formatting:

```python
from datetime import datetime
t = datetime(2025, 1, 1)
timestamp = MPlusClient.format_timestamp(t)

xml_placeholders = {
    "limit": 100,
    "offset": 0,
    "timestamp": timestamp
}

result = client.request("multimedia-search", xml_placeholders=xml_placeholders)
```

## Responses
`MPlusResponse` objects wrap regular `requests.Response` objects, including all usual attributes like `response.content`. Additionally, some helper methods are provided if the request returns XML from the MuseumPlus API:

- Use `parse_IDs()` to get a list of all IDs in the response. This is especially useful for search queries. The list can then be processed and used to execute additional API requests for these IDs.
    
    ```python
    result = client.request("multimedia-search")
    ids = result.parse_IDs()
    for id in ids:
        img = client.request("download-thumbnail", url_placeholders={"id": id})
    ```

- Use `parse_size()` to get the total number of objects found in a search request. This can then be used for pagination in further requests.
    
    ```python
    result = client.request("search-objects")
    size = result.parse_size()
    PAGESIZE = 1000
    for offset in range(0, size, PAGESIZE):
        json = client.request("export-json", xml_placeholders={"limit": PAGESIZE, "offset": offset})
    ```

