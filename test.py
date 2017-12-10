import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    except urllib2.URLError, e:
        print 'We failed to reach a server'
        print 'Reason: ', e.reason
    return None


def getReports(param = "", type = ""):
    baseurl = 'https://data.seattle.gov/resource/policereport.json'
    params = {}
    params[param] = type
    url = baseurl + "?" + urllib.urlencode(params)
    response = safeGet(url)
    if (response != None):
        data = response.read()
        return json.loads(data)

def getBicycleRacks():
    baseurl = 'https://data.seattle.gov/resource/fxh3-tqdm.json'
    response = safeGet(baseurl)
    if (response != None):
        data = response.read()
        return json.loads(data)

def getParkingLots():
    baseurl = 'https://data.seattle.gov/resource/kdkm-y3uh.json'
    response = safeGet(baseurl)
    if (response != None):
        data = response.read()
        return json.loads(data)


reports = getReports("year", "2010")
print(reports)

bikes = getBicycleRacks()
print(bikes)

parking = getParkingLots()
print(parking)