#!/usr/bin/python
import sys,os

sys.path.append("/home/skuper/workspace/MotifNetNew/cgi-bin/JobSubmissionPackage/Includes/")
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes/")

from conf import Conf
#sys.stderr = open(os.path.join(Conf.LogsDir, "error.log"),'a')
#sys.stdout = open(os.path.join(Conf.LogsDir, "error.log"),'a')
#from ClusterConnection import ExecuteFanmod

from Daemon import Daemon
from DBHandler import DBHandler
from FanmodRunner import FanmodRunner
from FanmodOutputHandler import OutputHandler
from EMailer import EMailer
from Logger import Logger



class SubmissionDaemon(Daemon):
    def init(self,executionMode, sessionDirName,jobId,paramsDict, email = None):

        self.mode = executionMode
        self.sessionDirName = sessionDirName
        self.sessionDirPath = os.path.join(Conf.Sessions_dir,self.sessionDirName)
        self.FanmodSessionDirPath = os.path.join(Conf.FANMOD_Sessions_dir,self.sessionDirName)
        self.jobId = jobId
        self.paramsDict = paramsDict
        self.email = email
        self.logger = Logger("Daemon",os.path.join(self.FanmodSessionDirPath, "user.log"))
        self.emailer = EMailer(self.email,logger = self.logger)

    def _sendEmail(self,func):
        try:  
            self.logger.log(2, "sending email to [%s] ..."%self.email)
            func(self.jobId)
        except Exception as inst:
            self.logger.log(3, "E-mail messaging failed. %s."%inst)
    
    def _localrun(self):
        raise Exception("_localrun not implemented!")
    def _remoterun(self):
        raise Exception("_localrun not implemented!")
        
    def run(self):        
        print "starting daemon..."
        
        #self._sendEmail(self.emailer.jobSubmitted)
        #print str(self.paramsDict)
        
        if self.mode==1: #run locally
            self._localrun()
        elif self.mode==2: #run remotely
            self._remoterun()
        else:
            raise Exception("executionMode is not recognized - %s"%self.mode)  
        
        print "finished"
    
        
class FanmodOutputSubmissionDaemon(SubmissionDaemon):
    def _localrun(self):
        targetPath = os.path.join(self.FanmodSessionDirPath,self.paramsDict[Conf.FanmodOutputFilesField])
        self._runOutputHandling(targetPath)
        
    def _runOutputHandling(self,targetPath):
        self.dbhandler = DBHandler(self.logger) 

        try:   
            self.logger.log(2, "starting output handler ...")
            localHandler = OutputHandler(
                                         rootDirPath = self.FanmodSessionDirPath, 
                                         networkFileName = self.paramsDict[Conf.networkFileField], 
                                         csvFileName = self.paramsDict[Conf.FanmodOutputFilesField] ,
                                         dumpFileName = self.paramsDict[Conf.FanmodOutputFilesField] + ".dump",
                                         dictFileName = self.paramsDict[Conf.dictFileField], 
                                         labelsDictFileName = self.paramsDict[Conf.nodeLabelsFileField],
                                         logger = self.logger
                                         )
            
            response = localHandler.run(int(self.paramsDict[Conf.motifSizeField]),
                             MIN_INSTANSES = int( self.paramsDict[Conf.instancesField])  ,
                             MAX_PVALUE = self.paramsDict[Conf.pvalueField] , 
                             MIN_ZSCORE = self.paramsDict[Conf.zscoreField] ,
                             color = self.paramsDict[Conf.colorField] , 
                             dangle = self.paramsDict[Conf.dangleField]
                             )
            network = localHandler.getNetwork()
            if response <=0:
                
                self.logger.log(4,"error occurred while processing FANMOD output.")
                self.emailer.error(self.jobId, "Error occurred while processing FANMOD output.")

                #self.dbhandler.updateSessionStatus(self.jobId,-1*response)
                self.dbhandler.updateSession(self.jobId, localHandler.motifs, network, -1*response)
            
            else:
                
                #self.dbhandler.loadNetwork(network,self.jobId)
                
                status = 1
                loadsubgraphs = True
                if localHandler.getSubgraphsCount() > Conf.SUBGRAPHS_LIMIT:
                    status = 2
                    loadsubgraphs = False
                success = self.dbhandler.loadMotifs(localHandler.motifs,loadsubgraphs,jobId = self.jobId)
                
                if success:
                    mof_suc, sub_suc  = success              
                    if not mof_suc:
                        self.logger.log(4,"error occurred while uploading motifs.")
                        self.emailer.error(self.jobId, "Error occurred while uploading motifs.")

                        self.dbhandler.updateSession(self.jobId, localHandler.motifs, network, 7)
                        
                    elif not sub_suc:
                        self.logger.log(4,"error occurred while uploading subgraphs.")
                        self.emailer.error(self.jobId, "Error occurred while uploading subgraphs.")

                        self.dbhandler.updateSession(self.jobId, localHandler.motifs, network, 8)
                        
                    else:
                        self.dbhandler.updateSession(self.jobId, localHandler.motifs, network, status)
                        self._sendEmail(self.emailer.notify)


                else:
                    self.logger.log(4,"No motifs.")
                    self.emailer.error(self.jobId, "No motifs found.")
                    self._sendEmail(self.emailer.notify)
                    self.dbhandler.updateSession(self.jobId, localHandler.motifs, network, 9)
                    
            
            '''
            self.logger.log(2, "restarting RPC in netbio ...")
            try:
                print "import ssh"
                sys.path.append("./")
                from ssh import Connection

                con = Connection(host = "netbio",
                         username = "motifnet",
                         password = "99motifnet",
                         port = 22)
                self.logger.log(1, "connection = [%s]"%str(con))
                cmd = Conf.RPC_RESTART_CMD
                self.logger.log(2, "restarting. cmd = [%s]"%cmd)
                self.logger.log(2, con.execute(cmd))
                con.close()
            except Exception as inst:
                self.logger.log(4, "Error restarting RPC: %s"%inst)
            '''
            
        except Exception as inst:
            msg = "Unexpected error in JobSubmissionDaemon: " + str(inst)
            self.logger.log(4,msg)
            self.emailer.error(self.jobId, msg)

            self.dbhandler.updateSessionStatus(self.jobId,3)
        
        self.dbhandler.close()
        self.logger.log(2, "output handler finished")

    def _remoterun(self):
        '''
        ef = ExecuteFanmod(self.sessionDirName)
        ef.buildConfigurationFile(self.paramsDict)
        #ef.upload_input_files()
        ef.executeScript("csh ", Conf.CLUSTER_QSUB_FILE) 
        
        if self.mode == 1:
            ef.executeScript("csh ", Conf.CLUSTER_QSUB_FILE) 
        elif self.mode == 2:
            ef.executeScript("csh ", Conf.CLUSTER_FO_QSUB_FILE)
        '''         
        
class FanmodSubmissionDaemon(FanmodOutputSubmissionDaemon):
    def _localrun(self):
        inputFilePath = os.path.join(self.sessionDirPath,self.paramsDict[Conf.networkFileField])
        targetPath = os.path.join(self.FanmodSessionDirPath,"fanmodResults")
        
        print "running FANMOD ..."
        fr = FanmodRunner(inputFilePath)
        
        fr.runFanmod(targetPath,
                 sizeOfMotifs = self.paramsDict[Conf.motifSizeField],
                 fullEnumeration = self.paramsDict['fullEnumeration'],
                 samplingProbabilities = self.paramsDict['samplingProbabilities'],
                 numberOfRandmoNetworks = self.paramsDict['randomNetworks'],
                 exchangesPerEdges = self.paramsDict['edgeSwitch'],
                 exchangeAttemptsPerEdge = self.paramsDict['edgeSwitchAttempt'],
                
                 regardVerticesColors = self.paramsDict['regardNodeColors'],
                 regardEdgesColors = self.paramsDict['regardEdgeColors'],
                 randomType = self.paramsDict['randomizationType'],
                 
                 
                 numberOfSubgraphs = 10, #self.paramsDict['samplesForApproximation'],
                 reestimateSubgraphsNumber = False #self.paramsDict['reestimateSubgraphNumber'],

                )
       

        print "handling FANMOD's output ..."
        self._runOutputHandling(targetPath)
        
        print "done."
        
    def _remoterun(self):
        """
        For running on a remote server
        """
        raise Exception("_remote run not implemented!")
      
        
            
if __name__=="__main__":
    daemon = FanmodSubmissionDaemon("/home/skuper/workspace/MotifNetNew/cgi-bin/Data/pid.txt",
                                          stdout = "/home/skuper/workspace/MotifNetNew/cgi-bin/Data/stdout.txt",
                                          stderr = "/home/skuper/workspace/MotifNetNew/cgi-bin/Data/stderr.txt")
    params = {
          Conf.sessionField:"testDirName", 
          Conf.jobNameField:"test",
          Conf.commentsField:"comments",
          Conf.instancesField:5,
          Conf.pvalueField:0.05, 
          Conf.zscoreField:0, 
          Conf.dangleField:2, 
          Conf.colorField:False,
          Conf.networkFileField:Conf.txt_file,
          Conf.FanmodOutputFilesField:Conf.FanmodOutputFiles,
          Conf.dumpFileField:Conf.dump_file,
          Conf.dictFileField:Conf.undict_file, 
          Conf.nodeLabelsFileField:Conf.labelsDict_file
          }
    
    daemon.init(1,"testDirName",117, params , email="ilansmoly@gmail.com" )
    daemon.run()
    
    