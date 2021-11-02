#!/usr/bin/python
print "content-type:text/html \n\n"

import os
import sys
sys.path.append("../")
from QueryDB import Query 
from formHandler import FormHandler
from conf import Conf  
sys.stderr = open(os.path.join(Conf.LogsDir, "error.log"),'a')


fh = FormHandler()
q = Query()
session = q.querySession(fh.jobId)
fh.parse(session.edge_colors,session.node_colors)

motifs = q.queryMotifs(fh.jobId, 
                       [fh.proteins,fh.proteins_function], [],
                       [fh.edges,fh.edges_function], fh.noedges,
                       [fh.nodes,fh.nodes_function], fh.nonodes,
                       fh.min_instances, fh.max_pvalue, fh.min_zscore, fh.min_frequency)

print "<div id=\"motifsHeader\">found %d motifs.</div>"%len(motifs)
print "<div id=\"motifsHeader\"><a>Adj</a><a>inst</a><a>P</a><a>Z</a><a>freq</a></div>"
print "<div id=\"motifResults\">"

for motif in motifs.values():
    print "<div id=\"resultBox\">"
    print "<div id=\"textInfo\">"
    print "<a>%s</a><a>%d</a><a>%s</a><a>%s</a><a>%s</a>"%(motif.adj,len(motif),motif.pval,motif.zscore,motif.freq)
    print "</div>"
    print "<div id=\"motifImage\">"
    print "<form id=\"%s\" >"%motif.adj
    imagePath = os.path.join(Conf.MotifsImagesDirPath,session.directory,motif.img_path)
    print "<a href=\"javascript:openInstance( 'instances', '"+motif.adj+"',-1,-1);\"><img src=\"%s\" width=\"180\" height=\"200\" ></a>"%imagePath
    print "</form></div>" 
    print "</div>"
print "</div>"
