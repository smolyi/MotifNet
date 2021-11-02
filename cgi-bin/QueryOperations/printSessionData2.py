#!/usr/bin/python

print "content-type:text/html \n\n"

import sys
sys.path.append("../")
from QueryDB import Query
from conf import Conf  
import os,cgi,json

cgi.parse_header("content-type:application/x-www-form-urlencoded")
form = cgi.FieldStorage()
jsonQueryString = form.getfirst("jsonQueryString", None)
params = json.loads(jsonQueryString)

q = Query()
session = q.querySession(params["jobid"])

print "<ul style=\"float: left;font-size: 10px; list-style-type: disc;  margin-top: 10px;  padding-left: 20px; text-align: left; \">"
print "<li style=\"margin-top: 1px; \" >Job id: %s</li>"%session.id
print "<li style=\"margin-top: 1px; \">Job name: %s</li>"%session.name
print "<li style=\"margin-top: 1px; \">Subgraphs size: %s</li>"%session.size
print "<li style=\"margin-top: 1px; \">Subgraphs number: %s</li>"%session.count
print "<li style=\"margin-top: 1px; \">Nodes: %s</li>"%session.nodes
print "<li style=\"margin-top: 1px; \">Edges: %s</li>"%session.edges
print "<li style=\"margin-top: 1px; \">Node colors: %s</li>"%session.node_colors
print "<li style=\"margin-top: 1px; \">Edge colors: %s</li>"%session.edge_colors
print "<li style=\"margin-top: 1px; \">Type: %s</li>"%session.type
print "<li style=\"margin-top: 1px; \">Time: %s</li>"%session.time
print "<li style=\"margin-top: 1px; \">Comments: %s</li>"%session.comments
print "</ul>"
