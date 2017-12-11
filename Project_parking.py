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

def openParking():
    url = "https://data.seattle.gov/resource/kdkm-y3uh.json"
    urlOpen = safeGet(url)
    data = json.loads(urlOpen.read())
    return data


def location(lat,long):
    data = openParking()
    list = []
    for lot in data:
        latitude = lot["shape"]["latitude"]
        longitude = lot["shape"]["longitude"]
        if((lat+0.0724637)>= float(latitude) and (lat-0.0724637)<= float(latitude)):
            if((long +0.0724637)>= float(longitude) and (long -0.0724637)<= float(longitude)):
                list.append(lot)
    return list

class ParkingInfo:
    def __init__(self,data):
        if (data.get("fac_type") == None):
            self.type = 'Unknown'
        else:
            self.type = data['fac_type']
        if (data.get("disbaled") == None):
            self.disabled = 'Unknown'
        else:
            self.disabled = data['disabled']
        if (data.get("rte_1hr") == None):
            self.rate1hour = 'Unknown'
        else:
            self.rate1hour = data['rte_1hr']
        if (data.get("rte_allday") == None):
            self.rateAllDay = 'Unknown'
        else:
            self.rateAllDay = data['rte_allday']


# Testing
# data = openParking()
# print(pretty(data))
# list = location(47.6,-122.3)
# for dic in list:
#     info = ParkingInfo(dic)
#     print(info.rateAllDay)







