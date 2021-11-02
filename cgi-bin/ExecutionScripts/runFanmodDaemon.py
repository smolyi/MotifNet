import sys,os
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/") 
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes") 
sys.path.append("/home/skuper/workspace/MotifNetNew/cgi-bin/JobSubmissionPackage/Includes") 

import jobSubmissionDaemon
from conf import Conf

jobId = 1000
      
userDirName = "phospho"

params = {
          Conf.networkFileField:Conf.txt_file,
          Conf.sessionField:userDirName, 
          Conf.userNameField:"Anonymous user",
          Conf.jobNameField: "phospho",
          Conf.commentsField:"no comments",
          Conf.motifSizeField: 3,
          Conf.instancesField: 1,
          Conf.pvalueField:0.05, 
          Conf.zscoreField:0, 
          Conf.dangleField:0, 
          Conf.colorField:False,
          
          "randomNetworks":1000,
          "edgeSwitch":3,
          "edgeSwitchAttempt":3, 
          "fullEnumeration":True, 
          Conf.FanmodOutputFilesField:Conf.FanmodOutputFiles,
          Conf.dictFileField:Conf.undict_file, 
          Conf.nodeLabelsFileField:Conf.labelsDict_file
          }
print ";".join (map(lambda x: str(x[0])+":"+str(x[1]), params.iteritems()))

#import pickle
#pickle.dump(params,open("params.pkl",'w'))

'''
SESSION_DIR_PATH = os.path.join(Conf.Sessions_dir, userDirName)


DAEMON_DIR_PATH = os.path.join( SESSION_DIR_PATH,Conf.DAEMON_DIR_NAME)

#print "OS response: %s"%os.mkdir(DAEMON_DIR_PATH)
pid = os.path.join( DAEMON_DIR_PATH,"pid.txt")
out = os.path.join( DAEMON_DIR_PATH,"out.txt")
err = os.path.join( DAEMON_DIR_PATH,"err.txt")

print  "executing daemon ..."
daemon = jobSubmissionDaemon.FanmodSubmissionDaemon(pid,stdout = out,stderr = err)
daemon.init(1,userDirName,jobId,params,"email")
print "starting Daemon"
daemon.start()
print "done"
'''