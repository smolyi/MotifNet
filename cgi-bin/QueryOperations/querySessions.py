#!/usr/bin/python

print "content-type:text/html \n\n"
import sys
sys.path.append("../")
from QueryDB import Query,SessionJSONEncoder
import cgi,json

cgi.parse_header("content-type:application/x-www-form-urlencoded")
form = cgi.FieldStorage()
jsonQueryString = form.getfirst("jsonQueryString", None)
params = json.loads(jsonQueryString)

q = Query()
sessions = q.queryAllSessions(params["user"])
print json.dumps(sessions,skipkeys = True,cls=SessionJSONEncoder)
