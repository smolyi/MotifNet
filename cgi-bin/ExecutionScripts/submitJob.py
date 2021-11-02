#!/usr/bin/python
print "content-type:text/html \n\n"
import sys


sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/") 
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes") 
#sys.path.append("/home/skuper/workspace/MotifNetNew/Includes")
from conf import Conf
sys.stderr = open(Conf.errorFilePath,'w')
from executor import Executor
ex = Executor(1)


#print "job submitted. you will be notified by e-mail when process is done."
#print "<li><a href=\"/motifNet/submit.html\">Submit a job</a></li><li><a href=\"/motifNet/index.html\">Request a query</a></li>"
