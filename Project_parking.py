#Reksha Rathnam and Sahana Vishwananth
#Final Project
#Seattle-Parking

import urllib.request, urllib.error, urllib.parse, json, webbrowser

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None

def open():
    url = "https://data.seattle.gov/resource/kdkm-y3uh.json"
    urlOpen = safeGet(url)
    data = json.loads(urlOpen.read())
    return data

data = open()
print(pretty(data))
