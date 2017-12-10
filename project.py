import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

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
    params['param'] = param
    params['type'] = type
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
        #param = self.request.get('filter')
        #type = self.request.get('type')
        vals['page_title'] = "Police Incident Report Map"
        #reportData = getReports(param, type)

        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(vals))

class MapVisualHandlr(webapp2.RequestHandler):
    def post(self):
        vals = {}
        long = self.request.get('longitude')
        lat = self.request.get('latitude')
        vals['page_title'] = "Crime + Parking + Bike Rack Map"
        vals['lat'] = lat
        vals['long'] = long

        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
    ('/gresponse', GreetResponseHandlr),
    ('/reportmap', PoliceReportMapHandlr),
    ('/map', MapVisualHandlr),
    ('/home', MainHandler)
],
debug=True)