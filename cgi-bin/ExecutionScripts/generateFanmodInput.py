#!/usr/bin/python
print "content-type:text/html \n\n"

import sys, os
from conf import Conf

#sys.stderr = open(Conf.errorFilePath,'w')
sys.path.append("/media/disk2/users/motifnet/MotifNetServer/Includes") # sys.path.append("/home/skuper/workspace/MotifNetServer/Includes")
from executor import Executor
ex = Executor(0)


print Conf.GraphsImagesDirPath,ex.userDirName
print "results are ready: <br>"
print "<ul>"
print "<li><a href=\"%s\"> Network </a></li>"%os.path.join(Conf.GraphsImagesDirPath,ex.userDirName,Conf.txt_file)
print "<li><a href=\"%s\"> Gene -> ID Dictionary .pkl file </a></li>"%os.path.join(Conf.GraphsImagesDirPath,ex.userDirName,"nodes-dict.pkl")
print "<li><a href=\"%s\"> ID -> Gene Dictionary .pkl file </a></li>"%os.path.join(Conf.GraphsImagesDirPath,ex.userDirName,"nodes-undict.pkl")
print "<li><a href=\"%s\"> Node color -> Label Dictionary .pkl file </a></li>"%os.path.join(Conf.GraphsImagesDirPath,ex.userDirName,"nodeLabels.pkl")
print "</ul>"
