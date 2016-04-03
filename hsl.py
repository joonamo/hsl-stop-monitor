import requests
import datetime

def parse_vehicle_code(code):
    # TODO: Currently everything is a bus
    return "%d%s" % (int(code[1:4]), code[4].strip())

def parse_datetime(time, date):
    if len(time) == 3:
        time = "0%s" % time

    # HSL has more hours in a day than a anyone else
    delta = datetime.timedelta()
    if int(time[0:2]) >= 24:
        delta = datetime.timedelta(days = 1)
        time = "%02d%s" % (int(time[0:2]) % 24, time[2:])

    return datetime.datetime.strptime(
        "%s %s" % (time, date),
        "%H%M %Y%m%d") + delta


class hsl_system(object):
    def __init__(self, username, password):
        super(hsl_system, self).__init__()
        self.username = str(username)
        self.password = str(password)
        self.base_url = "http://api.reittiopas.fi/hsl/prod/?user=%s&pass=%s&epsg_in=wgs84&epsg_out=wgs84&format=json" % (self.username, self.password)

    def get_stop_info(self, stop_code, extra_params = ""):
        url = "%s&request=stop&result_contains=stop&code=%s&%s" % (self.base_url, str(stop_code), extra_params)
        r = requests.get(url)
        if not(r.ok):
            raise Exception(
                "Failed to get stop info from url '%s'" % url , 
                "Reason: %s, Text from HSL: %s" % (r.reason, r.text))
        
        return r.json()[0]

    def get_departures(self, stop_code, dep_limit = 10, time_limit = 360):
        stop = self.get_stop_info(stop_code, ("dep_limit=%d&time_limit=%d" % (dep_limit, time_limit)))
        departures = stop["departures"]
        return [{"code": parse_vehicle_code(d["code"]), "time": parse_datetime(str(d["time"]), str(d["date"]))} for d in departures]
