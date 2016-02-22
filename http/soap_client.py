#!/usr/bin/python

import requests
url="http://192.168.1.82:55555"
#headers = {'content-type': 'application/soap+xml'}
headers = {'content-type': 'text/xml'}
body = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body><u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">
<ObjectID>0</ObjectID>
<BrowseFlag>BrowseDirectChildren</BrowseFlag>
<Filter>id,dc:title,res,sec:CaptionInfo,sec:CaptionInfoEx,pv:subtitlefile</Filter>
<StartingIndex>0</StartingIndex>
<RequestedCount>0</RequestedCount>
<SortCriteria></SortCriteria>
</u:Browse>
</s:Body>
</s:Envelope>"""

response = requests.post(url,data=body,headers=headers)
print response.content