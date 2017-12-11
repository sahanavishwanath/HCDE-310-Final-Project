import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

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

def getReports(params={}):
    baseurl = 'https://data.seattle.gov/resource/policereport.json'
    url = baseurl + "?" + urllib.urlencode(params)
    response = safeGet(url)
    if (response != None):
        data = response.read()
        return json.loads(data)

#Testing getReports
data = getReports({'district_sector': "U", 'year':"2010"})
print(pretty(data))

data2 = getReports()
print(pretty(data2))

def openBikeData():
    url = "https://data.seattle.gov/resource/fxh3-tqdm.json"
    urlOpen = safeGet(url)
    if(urlOpen != None):
        data = json.loads(urlOpen.read())
        return data

def filterLocation(lat, long, data):
    output = []
    for one in data:
        latitude = one['latitude']
        longitude = one['longitude']
        if ((lat + 0.0724637) >= float(latitude) and (lat - 0.0724637) <= float(latitude)):
            if ((long + 0.0724637) >= float(longitude) and (long - 0.0724637) <= float(longitude)):
                output.append(one)
    return output

def locationBike(lat,long):
    data = openBikeData()
    list = []
    for lot in data:
        latitude = lot["latitude"]
        longitude = lot["longitude"]
        if((lat+0.0724637)>= float(latitude) and (lat-0.0724637)<= float(latitude)):
            if((long +0.0724637)>= float(longitude) and (long -0.0724637)<= float(longitude)):
                list.append(lot)
    return list

class RackInfo:
    def __init__(self,data):
        if (data.get("condition") == None):
            self.condition = 'Unknown'
        else:
            self.condition = data['condition']
        if (data.get("rack_capac") == None):
            self.capacity = 'Unknown'
        else:
            self.capacity = data['rack_capac']

def openParking():
    url = "https://data.seattle.gov/resource/kdkm-y3uh.json"
    urlOpen = safeGet(url)
    if(urlOpen != None):
        data = json.loads(urlOpen.read())
        return data

def locationLot(lat,long):
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

def getMap(reports, bikes=[], lots=[]):
    baseurl = 'https://maps.googleapis.com/maps/api/staticmap?size=600x600&markers=color:red%7C'
    for report in reports:
        baseurl = baseurl + report['latitude'] + ',' + report['longitude'] + '%7C'
    baseurl = baseurl[:-3]
    if(bikes != None and lots != None):
        baseurl = baseurl + '&markers=color:blue%7C'
        for bike in bikes:
            baseurl = baseurl + bike['latitude'] + ',' + bike['longitude'] + '%7C'
        baseurl = baseurl[:-3]
        baseurl = baseurl + '&markers=color:green%7C'
        for lot in lots:
            baseurl = baseurl + lot['latitude'] + ',' + lot['longitude'] + '%7C'
        baseurl = baseurl[:-3]
    API_key = 'AIzaSyB2OtiEQpLSgstzxNHiAd0CPMlPiha7MQg'
    url = baseurl + '&key=' + API_key
    img = safeGet(url)
    return img

#Testing getMap()
test = [{'latitude': "47.67578125", 'longitude': "-122.292984009"}, {'latitude': "47.685764313", 'longitude':"-122.300827026"}, {'latitude': "47.661296844", 'longitude':"-122.317642212"}]
img = getMap(test)

trial1 = [{'latitude': "47.67578125", 'longitude': "-122.292984009"}]
trial2 = [{'latitude': "47.685764313", 'longitude':"-122.300827026"}]
trial3 = [{'latitude': "47.661296844", 'longitude':"-122.317642212"}]
img = getMap(trial1, trial2, trial3)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")

        template_values = {}
        template_values['page_title'] = "Seattle Government Data Visualizer"
        template = JINJA_ENVIRONMENT.get_template('greetform.html')
        self.response.write(template.render(template_values))

class GreetResponseHandlr(webapp2.RequestHandler):
    def post(self):
        vals = {}
        checkReports = self.request.POST.get('crime')
        checkPark = self.request.POST.get('crimepark')
        if(checkReports):
            vals['page_title'] = "Police Incident Reporter"
            template = JINJA_ENVIRONMENT.get_template('policereport.html')
            self.response.write(template.render(vals))
        elif(checkPark):
            vals['page_title'] = "Police Incident Report, Bike Racks, and Parking Lot Visualizer"
            template = JINJA_ENVIRONMENT.get_template('visualizer.html')
            self.response.write(template.render(vals))

class PoliceReportMapHandlr(webapp2.RequestHandler):
    def post(self):
        vals = {}
        year = self.request.POST.get('year')
        type = self.request.POST.get('type')

        params = {}
        if(year):
            params['year'] = year
        if(type):
            params['summarized_offense_description'] = type
        params['district_sector'] = 'U'
        reportData = getReports(params)
        img = getMap(reportData)

        vals['page_title'] = "Police Incident Report Map"
        vals['year'] = year
        vals['type'] = type
        vals['map'] = img

        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(vals))

class MapVisualHandlr(webapp2.RequestHandler):
    def post(self):
        vals = {}
        long = int(self.request.get('longitude'))
        lat = int(self.request.get('latitude'))
        vals['page_title'] = "Crime + Parking + Bike Rack Map"

        reports = getReports()
        bikes = openBikeData()
        parking = openParking()

        filterReports = filterLocation(lat, long, reports)
        filterBikes = filterLocation(lat, long, bikes)
        filterParking = filterLocation(lat, long, parking)

        img = getMap(filterReports, filterBikes, filterParking)
        vals['map'] = img

        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
    ('/gresponse', GreetResponseHandlr),
    ('/reportmap', PoliceReportMapHandlr),
    ('/map', MapVisualHandlr),
    ('/home', MainHandler)
],
debug=True)