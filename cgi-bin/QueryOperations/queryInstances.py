#!/usr/bin/python

print "content-type:text/html \n\n"

import sys
sys.path.append("../")
from conf import Conf  
sys.stderr = open(Conf.errorFilePath,'a')
from QueryDB import Query 
from formHandler import FormHandler
import os,math

MAX_ENTRIES = 100

fh = FormHandler()
q = Query()
session = q.querySession(fh.jobId)
fh.parse(session.edge_colors,session.node_colors)

q = Query()
motif = q.queryMotifByAdj(fh.jobId, fh.adj)
if motif:
    adjMat = motif.getAdjAsMat()
    print "<div id=\"instancesHeader\">"
    print "<table id=\"instancesHeader\" >"
    print "<tr class=\"instancesHeaderTop\" >"
    print "<td>adj</td>"
    print "<td>size</td>"
    print "<td>subgraphs</td>"
    print "<td>pvalue</td>"
    print "<td>zscore</td>"
    print "<td>frequency</td>"
    print "</tr>"
    
    print "<tr class=\"instancesHeaderBottom\" >"
    print "<td>"
    for i in range (0,len(adjMat)):
        for j in range (0,len(adjMat[i])):
            print adjMat[i][j]
        print "<br>"
    print "</td>"
    print "<td>%s</td>"%motif.size
    print "<td>%s</td>"%len(motif)
    print "<td>%s</td>"%motif.pval
    print "<td>%s</td>"%motif.zscore
    print "<td>%s</td>"%motif.freq
    print "</tr>"
    print "</table></div>"
    print "<div id=\"instances_content\">"
    print "<div id=\"instances_subgraphs\">"

    print "<table>"
    if MAX_ENTRIES >= len(motif): 
        print "<tr><td>id</td>"
        for i in range(1,motif.size+1): print "<td>node%d</td>"%i
        for i in range(1,math.factorial(motif.size)+1):
            print "<td>edge%d</td>"%i
        print "</tr>"
        count = 0
        for inst in motif.instances:
            count += 1
            print "<tr><td>%d</td>"%count
            for k in range(0,motif.size):
                print "<td>%s</td>"%inst[k]
            for i in range(0,motif.size):
                for j in range(0,motif.size):
                    if i!=j:
                        print "<td><a href=javascript:printEdgeData(\'%s\',\'%s\',\'%s\'); >%s,%s</a></td>"%(fh.jobId,inst[i],inst[j],inst[i],inst[j])
            print "</tr>"
    else:
        print "<tr><td>%d subgraphs found. the number exceed the limit - %d</td></tr>"%(len(motif),MAX_ENTRIES)
    print "</table>"
    print"</div>"
    
    
    
    print "<div id=\"instances_nodes\">"
    nodesList = motif.getNodesFrequencyTable(fh.sort_nodes)
    print "<table><tr><td>num</td><td>node</td>"
    for i in range (1,motif.size+1):
        print "<td><a href=javascript:openInstance(\'instances\',\'%s\',%d,%d);>pos%d</a></td>"%(fh.adj,i-1,fh.sort_edges,i)
    print "<td><a href=javascript:openInstance(\'instances\',\'%s\',-1,%d); >total</a></td>"%(fh.adj,fh.sort_edges)
    print "</tr>"
    count = 0 
    for k in range(0,min(MAX_ENTRIES,len(nodesList))):
        count += 1
        print "<tr><td>%d</td><td>%s</td>"%(count,nodesList[k][0])
        for i in range (0,motif.size+1):
            print "<td>%f</td>"%(nodesList[k][1][i])
        print "</tr>"
    print "</table>"
    print"</div>"
    
    
    
    print "<div id=\"instances_edges\">"
    edgesList = motif.getEdgesFrequencyTable(fh.sort_edges)
    print "<table><tr><td>num</td><td>edge</td>"
    for i in range (1,math.factorial(motif.size)+1):
        print "<td><a href=javascript:openInstance(\'instances\',\'%s\',%d,%d);>pos%d</a></td>"%(fh.adj,fh.sort_nodes,i-1,i)
    print "<td><a href=javascript:openInstance(\'instances\',\'%s\',%d,-1); >total</a></td>"%(fh.adj,fh.sort_nodes)
    print "</tr>"
    count = 0 
    for k in range(0,min(MAX_ENTRIES,len(edgesList))):
        count += 1
        print "<tr><td>%d</td><td>%s</td>"%(count,edgesList[k][0])
        for i in range (0,len(edgesList[k][1])):
            print "<td>%f</td>"%(edgesList[k][1][i])
        print "</tr>"
    print "</table>"
    print"</div>"
    print"</div>" #instances_content
    
else:
    print "data is not available for motif '%s' in job '%s'"%(fh.adj,fh.jobId)