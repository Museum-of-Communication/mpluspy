from mpluspy import MPlusClient
from datetime import datetime

AUTH = ('user', 'pass') # replace with your credentials


# creating new client with example config
client = MPlusClient('example.yml', auth=AUTH)

# XML placeholders for paging and timestamp
TIMESTAMP = datetime(2025, 1, 1) # this is used in the request to query any assets modified after this date
XML_PLACEHOLDERS = {'limit': 10,
                    'offset': 0,
                    'timestamp': MPlusClient.format_timestamp(TIMESTAMP)}

# execute request
response = client.request('example-request', xml_placeholders=XML_PLACEHOLDERS)

print("whole response:")
print(response.content)

print("the same data but parsed to xml:")
print(response.xml_to_dict())

print("total of items found:")
print(response.parse_size())

print("IDs of found items. Contains only the current page, i.e. max 10 items:")
print(response.parse_IDs())
