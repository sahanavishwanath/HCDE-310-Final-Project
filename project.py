import webapp2, urllib, urllib2, json
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
    baseurl = 'http://data.seattle.gov/resource/policereport.json'
    url = baseurl + "?" + urllib.urlencode(params)
    response = safeGet(url)
    if (response != None):
        data = response.read()
        return json.loads(data)

def openBikeData():
    url = "http://data.seattle.gov/resource/fxh3-tqdm.json"
    urlOpen = safeGet(url)
    if(urlOpen != None):
        data = json.loads(urlOpen.read())
        return data

def openParking():
    url = "http://data.seattle.gov/resource/kdkm-y3uh.json"
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

def locationLot(lat,long, data):
    list = []
    for lot in data:
        latitude = lot["shape"]["latitude"]
        longitude = lot["shape"]["longitude"]
        if((lat+0.0724637)>= float(latitude) and (lat-0.0724637)<= float(latitude)):
            if((long +0.0724637)>= float(longitude) and (long -0.0724637)<= float(longitude)):
                list.append(lot)
    return list

def getParkingMap(dict, lat="", long=""):
    baseurl = createParkingMapsLink(dict, lat, long)
    baseurl = baseurl[:-3]
    API_key = 'AIzaSyB2OtiEQpLSgstzxNHiAd0CPMlPiha7MQg'
    url = baseurl + '&key=' + API_key
    return url

def createParkingMapsLink(dict, lat, long):
    baseurl = 'http://maps.googleapis.com/maps/api/staticmap?size=600x600&center=' + lat + ',' + long
    baseurl = baseurl + '&markers=color:green%7C'
    count = 0
    for data in dict:
        if count > 20:
            return baseurl
        baseurl = baseurl + data['shape']['latitude'] + ',' + data['shape']['longitude'] + '%7C'
        count = count + 1
    return baseurl

def getMap(dict, color, lat="", long=""):
    baseurl = createMapsLink(dict, lat, long, color)
    baseurl = baseurl[:-3]
    API_key = 'AIzaSyB2OtiEQpLSgstzxNHiAd0CPMlPiha7MQg'
    url = baseurl + '&key=' + API_key
    return url

def createMapsLink(dict, lat, long, color):
    baseurl = 'http://maps.googleapis.com/maps/api/staticmap?size=600x600&center=' + lat + ',' + long
    baseurl = baseurl + '&markers=color:' + color + '%7C'
    count = 0
    for data in dict:
        if count > 20:
            return baseurl
        baseurl = baseurl + data['latitude'] + ',' + data['longitude'] + '%7C'
        count = count + 1
    return baseurl

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
        url = getMap(reportData, 'red')

        vals['page_title'] = "Police Incident Report Map"
        vals['year'] = year
        vals['type'] = type
        vals['map'] = url

        template = JINJA_ENVIRONMENT.get_template('filterMap.html')
        self.response.write(template.render(vals))

class MapVisualHandlr(webapp2.RequestHandler):
    def post(self):
        vals = {}
        long = float(self.request.get('longitude'))
        lat = float(self.request.get('latitude'))
        vals['page_title'] = "Crime + Parking + Bike Rack Map"
        vals['lat'] = lat
        vals['long'] = long

        reports = getReports()
        bikes = openBikeData()
        parking = openParking()

        filterReports = filterLocation(lat, long, reports)
        filterBikes = filterLocation(lat, long, bikes)
        filterParking = locationLot(lat, long, parking)

        reportMap = getMap(filterReports, 'red', str(lat), str(long))
        bikeMap = getMap(filterBikes, 'blue', str(lat), str(long))
        parkingMap = getParkingMap(filterParking, str(lat), str(long))
        vals['reportMap'] = reportMap
        vals['bikeMap'] = bikeMap
        vals['parkingMap'] = parkingMap

        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
    ('/gresponse', GreetResponseHandlr),
    ('/reportmap', PoliceReportMapHandlr),
    ('/map', MapVisualHandlr),
    ('/home', MainHandler)
],
debug=True)