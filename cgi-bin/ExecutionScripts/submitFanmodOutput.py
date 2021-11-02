#!/usr/bin/python
print "content-type:text/html \n\n"
from conf import Conf
import cgi,sys,os
#sys.stderr = open(Conf.errorFilePath,'a')
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/ExecutionScripts/Submit/Includes") # sys.path.append("/home/skuper/workspace/MotifNetServer/Includes")

from executor import Executor
ex = Executor(2)
submitJobPage = os.path.join(Conf.webpageRoot,"submitFanmodOutput.php")
queryPage = os.path.join(Conf.webpageRoot,"main.html")

print "job submitted. you will be notified by e-mail when process is done."
print "<li><a href=\"%s\">Submit a job</a></li><li><a href=\"%s\">Request a query</a></li>"%(submitJobPage,queryPage)
