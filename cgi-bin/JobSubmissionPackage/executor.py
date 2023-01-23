import os,sys
sys.path.append("/home/skuper/workspace/MotifNetNew/cgi-bin/JobSubmissionPackage/Includes/")
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes/")
from fanmodGraph import FanmodGraph
from CGIHandler import CGIHandler
from EMailer import EMailer

from conf import Conf
from Logger import Logger
import jobSubmissionDaemon
from DBHandler import DBHandler
from ssh import Connection
from datetime import datetime

class Executor():
    
    def __init__(self, mode):
        try: 
            self.logger = Logger("executor", os.path.join(Conf.LogsDir, "main.log"))
            self.cgiHandler = CGIHandler(self.logger)
            self.dbh = DBHandler(self.logger)
            self.jobId =  self.__createSession()
            
            if self.jobId>=0: 
                print self.jobId
                self._sendEmail()
                self.logger.log(1,"session id: %d " % self.jobId)
                self.logger.log(1,"user: " + self.cgiHandler.user)
                self.logger.log(1,"job: " + self.cgiHandler.jobName)
                
                self.userDirName = self.__buildUserDir(self.jobId)
                
                self.SESSION_DIR_PATH = os.path.join(Conf.Sessions_dir, self.userDirName)
                
                #self.DAEMON_DIR_PATH = os.path.join( Conf.FANMOD_Sessions_dir, self.userDirName,Conf.DAEMON_DIR_NAME)
        
                self.DAEMON_DIR_PATH = os.path.join( self.SESSION_DIR_PATH,Conf.DAEMON_DIR_NAME)
                
            
                
                res = {0: self.createFanmodGraph,
                    1: self.runFanmod,
                    2: self.handleFanmodOutput,
                    3: self.remoteExecution
                    }\
                    [mode]()
            else:
                self.logger.log(5, "Error creating session in db!")
                self._sendError("Error creating session in db!")
        except Exception as inst:
            msg = "Unexpected error: %s"%str(inst)
            self.logger.log(5, msg)
            self._sendError(msg)
            
    def _sendEmail(self):
        try:  
            self.logger.log(2, "sending email to [%s] ..."%self.cgiHandler.email)
            m = EMailer(self.cgiHandler.email,self.logger)
            m.jobSubmitted(self.jobId)
        except Exception as inst:
            self.logger.log(2, "E-mail messaging failed. %s."%inst)
    def _sendError(self,msg):
        try:  
            self.logger.log(2, "sending email to [%s] ..."%self.cgiHandler.email)
            m = EMailer(self.cgiHandler.email,self.logger)
            m.error(self.jobId,msg)
        except Exception as inst:
            self.logger.log(2, "E-mail messaging failed. %s."%inst)

    def __createSession(self):
        #try:
        self.logger.log(2, "creating session ........")
        jobId = self.dbh.loadSession(self.cgiHandler.user, 
                                          self.cgiHandler.jobName, 
                                          self.cgiHandler.sizeOfMotif, 
                                          str(datetime.today()).replace(" ","_"),
                                          self.cgiHandler.email, 
                                          self.cgiHandler.comments,
                                          ";".join (map(lambda x: str(x[0])+":"+str(x[1]), self.__createParamsDictFanmodExecutionArguments().iteritems()))
                                          ) 
        
        return jobId
        '''
        except Exception as inst:
            self.logger.log(5, "Error creating session.")
            self.logger.log(5, inst)
            return -1
        '''
     
    def remoteExecution(self):
        
        PARAMS_DICT_FILE_PATH = os.path.join(self.SESSION_DIR_PATH,"params.pkl")
        self.logger.log(2, "dumping params file to [%s]"%PARAMS_DICT_FILE_PATH)
        params = self.__createParamsDictFanmodExecution()
        
        import pickle
        pickle.dump(params, open(PARAMS_DICT_FILE_PATH,'w'))
        
        self.createFanmodGraph()
        
        self.logger.log(2, "connecting to remote server ...")
        try:
            
            con = Connection(host = "netbio-test.med.ad.bgu.ac.il",
                     username = "",
                     password = "",
                     port = 22)
            self.logger.log(1, "connection = [%s]"%str(con))
            cmd = "python /media/disk2/users/motifnet/Websites/Product/RemoteFanmodServer/executor.py %d %s --email %s"%(self.jobId,self.userDirName, self.cgiHandler.email)
            self.logger.log(2, "running daemon. cmd = [%s]"%cmd)
            self.logger.log(2, con.execute(cmd))
            con.close()
        except Exception as inst:
            self.logger.log(4, "Error executing motifnet on remote server: %s"%inst)
            self.logger.log(5, "Job was not processed!!!")
            raise inst
            
            
    def handleFanmodOutput(self):
        self.cgiHandler.getFanmodOutputFiles(self.SESSION_DIR_PATH)
        self.runOutputHandlingDaemon()
        
    def runFanmod(self):
        self.createFanmodGraph()
        self.runFanmodDaemon()
     
    def createFanmodGraph(self):
        edgefiles = self.cgiHandler.getEdgeFiles(self.SESSION_DIR_PATH)
        nodefiles = self.cgiHandler.getNodeFiles(self.SESSION_DIR_PATH)
        self.dbh.loadNetworkFiles(self.jobId, nodefiles, edgefiles)
        
        #list all files in the Nodes/Edges folders
        files = os.listdir(os.path.join(self.SESSION_DIR_PATH,Conf.EdgesFilesDir))
        edges = []
        for filename in files:
            edges.append(os.path.join(self.SESSION_DIR_PATH,Conf.EdgesFilesDir,filename))
        
        files = os.listdir(os.path.join(self.SESSION_DIR_PATH,Conf.NodesFilesDir))
        nodes = []
        for filename in files:
            nodes.append(os.path.join(self.SESSION_DIR_PATH,Conf.NodesFilesDir,filename))
        
        inputGraphFilePath = os.path.join(self.SESSION_DIR_PATH,Conf.txt_file)
        
        edges.sort()
        nodes.sort()
        
        self.logger.log(1, str([inputGraphFilePath,os.path.join(self.SESSION_DIR_PATH),edges,nodes,self.cgiHandler.edgesDirection]))
        
        fg = FanmodGraph(inputGraphFilePath,
                    [os.path.join(self.SESSION_DIR_PATH,Conf.dict_file),os.path.join(self.SESSION_DIR_PATH,Conf.undict_file)],
                    edges,nodes,self.cgiHandler.edgesDirection)
        self.dbh.updateSessionNetwork(self.jobId, len(fg.translate),len(fg.edges))
        '''
        #node-labels dict
        _dict = {}
        for i in range(0,len(nodeLabels)):
            _dict[str(i)]=str(nodeLabels[i])
        pickle.dump(_dict,open(os.path.join(self.SESSION_DIR_PATH,Conf.labelsDict_file),'w'))
        '''
    
    def runOutputHandlingDaemon(self):
        self.__runDaemon(2, self.__createParamsDictFanmodOutput())
        
    def runFanmodDaemon(self):
        self.__runDaemon(1, self.__createParamsDictFanmodExecution())
    
    def __runDaemon(self, daemonMode, params):        
        self.logger.log(2, "creating daemon directory - [%s]"%self.DAEMON_DIR_PATH)
        self.logger.log(1,"OS response: %s"%os.mkdir(self.DAEMON_DIR_PATH))
        pid = os.path.join( self.DAEMON_DIR_PATH,"pid.txt")
        out = os.path.join( self.DAEMON_DIR_PATH,"out.txt")
        err = os.path.join( self.DAEMON_DIR_PATH,"err.txt")
        
        self.logger.log(2, "executing daemon ...")
        daemon = {
                  1: jobSubmissionDaemon.FanmodSubmissionDaemon(pid,stdout = out,stderr = err),
                  2: jobSubmissionDaemon.FanmodOutputSubmissionDaemon(pid,stdout = out,stderr = err)
                  }[daemonMode]
        daemon.init(1,self.userDirName,self.jobId,params,self.cgiHandler.email)
        self.logger.log(2, "starting Daemon")
        daemon.start()
        self.logger.log(2, "executed")
    
    def __buildUserDir(self, jobid):
        '''
        from datetime import datetime
        dt = str(datetime.today()).replace(" ","_")
        dirName = "%s-%s"%(dt,jobid)
        '''
        sessionDirectory = os.path.join( Conf.Sessions_dir  ,str(jobid))
        
        self.logger.log(2, "making user directories on [%s]"%sessionDirectory)
        self.logger.log(1, "OS response: %s"%os.mkdir(sessionDirectory) )

        self.logger.log(1, "OS response (edge/node sub-folder): [%s ; %s]"%
                        (os.mkdir( os.path.join(sessionDirectory,Conf.EdgesFilesDir)),
                        os.mkdir( os.path.join(sessionDirectory,Conf.NodesFilesDir))))
        
        return str(jobid) 
    
    
    def __createBasicParamsDict(self):
        return {
                  Conf.motifSizeField:self.cgiHandler.sizeOfMotif,
                  Conf.instancesField:self.cgiHandler.minOccurrences,
                  Conf.pvalueField:self.cgiHandler.maxPvalue, 
                  Conf.zscoreField:self.cgiHandler.minZscore, 
                  Conf.dangleField:self.cgiHandler.avoidDanglingEdges, 
                  Conf.colorField:self.cgiHandler.onlyColored,
                  }
        
    def __createParamsDictFanmodExecution(self):
        basics = self.__createBasicParamsDict()
        other =  {
                  Conf.networkFileField:Conf.txt_file,
                  Conf.sessionField:self.userDirName, 
                  Conf.userNameField:self.cgiHandler.user,
                  Conf.jobNameField:self.cgiHandler.jobName,
                  Conf.commentsField:self.cgiHandler.comments,
                  Conf.FanmodOutputFilesField:Conf.FanmodOutputFiles,
                  Conf.dictFileField:Conf.undict_file, 
                  Conf.nodeLabelsFileField:Conf.labelsDict_file,
                  
                  "randomNetworks":self.cgiHandler.randomNetworks,
                  "edgeSwitch":self.cgiHandler.edgeSwitch,
                  "edgeSwitchAttempt":self.cgiHandler.edgeSwitchAttempt, 
                  "fullEnumeration":self.cgiHandler.fullEnumeration, 
                  "randomizationType":self.cgiHandler.randomizationType,
                  "regardEdgeColors":self.cgiHandler.regardEdgeColors, 
                  "regardNodeColors":self.cgiHandler.regardNodeColors, 
                  "samplingProbabilities":self.cgiHandler.samplingProbabilities,
                  
                  #"reestimateSubgraphNumber":self.cgiHandler.reestimateSubgraphNumber,
                  #"samplesForApproximation":self.cgiHandler.samplesForApproximation
                  }
        
        other.update(basics)
        return other
        
    def __createParamsDictFanmodExecutionArguments(self):
        basics = self.__createBasicParamsDict()
        other =  {
                  "randomNetworks":self.cgiHandler.randomNetworks,
                  "edgeSwitch":self.cgiHandler.edgeSwitch,
                  "edgeSwitchAttempt":self.cgiHandler.edgeSwitchAttempt, 
                  "fullEnumeration":self.cgiHandler.fullEnumeration, 
                  "randomizationType":self.cgiHandler.randomizationType,
                  "regardEdgeColors":self.cgiHandler.regardEdgeColors, 
                  "regardNodeColors":self.cgiHandler.regardNodeColors, 
                  "samplingProbabilities":self.cgiHandler.samplingProbabilities,
                  
                  #"reestimateSubgraphNumber":self.cgiHandler.reestimateSubgraphNumber,
                  #"samplesForApproximation":self.cgiHandler.samplesForApproximation
                  }
        
        other.update(basics)
        return other
    def __createParamsDictFanmodOutput(self):
        basics = self.__createBasicParamsDict()
        other =   {
                  Conf.sessionField: self.userDirName, 
                  Conf.userNameField: self.cgiHandler.user,
                  Conf.jobNameField: self.cgiHandler.jobName,
                  Conf.commentsField: self.cgiHandler.comments,
                  Conf.networkFileField:Conf.txt_file,
                  Conf.csvFileField:Conf.csv_file,
                  Conf.dumpFileField:Conf.dump_file,
                  Conf.dictFileField:Conf.undict_file, 
                  Conf.nodeLabelsFileField:Conf.labelsDict_file
                  }   
        other.update(basics)
        return other         


            
#Executor(1)
'''
params = {
          Conf.networkFileField:Conf.txt_file,
                  Conf.sessionField:"test", 
                  Conf.userNameField:"skuper",
                  Conf.jobNameField:"remote",
                  Conf.commentsField:"bllllll",
                  Conf.motifSizeField:3,
                  Conf.instancesField:5,
                  Conf.pvalueField:0.05, 
                  Conf.zscoreField:1}
pa =  {       Conf.dangleField:0, 
      Conf.colorField:1,
      
      "randomNetworks":10,
      "edgeSwitch":3,
      "edgeSwitchAttempt":3, 
      "fullEnumeration":1, 
      Conf.FanmodOutputFilesField:Conf.FanmodOutputFiles,
      Conf.dictFileField:Conf.undict_file, 
      Conf.nodeLabelsFileField:Conf.labelsDict_file
      }
pa.update(params)
print len(pa)
print ";".join (map(lambda x: str(x[0])+":"+str(x[1]), params.iteritems()))

#pickle.dump(params, open("params.pkl",'w'))
'''
