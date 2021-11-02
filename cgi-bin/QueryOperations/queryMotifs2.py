#!/usr/bin/python
print "content-type:text/html \n\n"
import json,cgi
import os, sys
sys.path.append("../")
from QueryDB import Query,MotifJSONEncoder
from conf import Conf  
sys.stderr = open(os.path.join(Conf.LogsDir, "error.log"),'a')

cgi.parse_header("content-type:application/x-www-form-urlencoded")
form = cgi.FieldStorage()
jsonQueryString = form.getfirst("jsonQueryString", None)
params = json.loads(jsonQueryString)


q = Query()
session = q.querySession(params["jobid"])

motifs = q.queryMotifs(params["jobid"], 
                       [params["proteins"],2 == int(params["radioProteinShow"])], [],
                       [params["showedges"],2 == int(params["radioEdgeShow"])], params["hideedges"],
                       [params["shownodes"],2 == int(params["radioNodeShow"])], params["hidenodes"],
                       float(params["minInstances"]), 
                       float(params["maxPvalue"]), 
                       float(params["minZscore"]), 
                       float(params["minFrequency"]))

print json.dumps(motifs,skipkeys = True, cls=MotifJSONEncoder)







'''
print "<div id=\"motifsHeader\">found %d motifs.</div>"%len(motifs)
print "<div id=\"motifsHeader\"><a>Adj</a><a>inst</a><a>P</a><a>Z</a><a>freq</a></div>"
print "<div id=\"motifResults\">"

for motif in motifs.values():
    print "<li id='%s'><table class='motifTable'><tr><th>Adj</th><th>Inst</th><th>P</th><th>Z</th><th>Freq</th></tr>"%motif.adj
    print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr><tr><td colspan='5'><div class='crop'>"%(motif.adj,len(motif),motif.pval,motif.zscore,motif.freq)
    magePath = os.path.join(Conf.MotifsImagesDirPath,session.directory,motif.img_path)
    print "<img src='%s' alt='%s'></div></td></tr></table></li>"%(magePath,motif.adj)

'''