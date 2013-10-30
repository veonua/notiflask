import json
import urllib2

__author__ = 'veon'


def gcm_send_request(deviceIds, data):
    json_data = {"collapse_key" : "msg",
                 "data" : data,
                 "registration_ids": deviceIds,
                 }


    url = 'https://android.googleapis.com/gcm/send'
    myKey = "AIzaSyA5rLGhEptdNR7sYfo1YLkzZhG7dyXneKk"
    data = json.dumps(json_data)
    headers = {'Content-Type': 'application/json', 'Authorization': 'key=%s' % myKey}
    req = urllib2.Request(url, data, headers)
    f = urllib2.urlopen(req)
    return json.loads(f.read())


