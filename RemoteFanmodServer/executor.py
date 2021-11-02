import os,pickle,sys
sys.path.append("/home/skuper/workspace/MotifNetNew/cgi-bin/JobSubmissionPackage/Includes")
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes") 

from conf import Conf 
from Logger import Logger 
import jobSubmissionDaemon 



class Executor():
    
    def __init__(self, jobId, sessionDir, email = None):
        self.logger = Logger("executor", os.path.join(Conf.LogsDir, "main.log"))
        self.jobId = jobId
        self.email = email
                        
        self.logger.log(1,self.jobId)
        self.userDirName = sessionDir 
        self.CGIDirPath = os.path.join(Conf.Sessions_dir, str(self.userDirName))
        self.LocalDirPath = os.path.join(Conf.FANMOD_Sessions_dir, str(self.userDirName))
        
        self.PARAMS_DICT_FILE_PATH = os.path.join(self.CGIDirPath,"params.pkl")
        
        self.DAEMON_DIR_PATH = os.path.join( self.LocalDirPath,Conf.DAEMON_DIR_NAME)
        
        self.__buildUserDir()        

    
    def handleFanmodOutput(self):
        self.__runOutputHandlingDaemon()
        
    def runFanmod(self):
        self.__runFanmodDaemon()
    
    def __runOutputHandlingDaemon(self):
        params = pickle.load(open(self.PARAMS_DICT_FILE_PATH))
        self.__runDaemon(2, params)
        
    def __runFanmodDaemon(self):
        params = pickle.load(open(self.PARAMS_DICT_FILE_PATH))

        self.__runDaemon(1, params)
    
    def __runDaemon(self, daemonMode, params):
        
        self.logger.log(2, "creating daemon directory - [%s]"%self.DAEMON_DIR_PATH)
        try:
            self.logger.log(1,os.mkdir(self.DAEMON_DIR_PATH))
        except Exception as inst: 
            self.logger.log(3,inst)
        pid = os.path.join( self.DAEMON_DIR_PATH,"pid.txt")
        out = os.path.join( self.DAEMON_DIR_PATH,"out.txt")
        err = os.path.join( self.DAEMON_DIR_PATH,"err.txt")
        
        email = self.email
        self.logger.log(2, "executing daemon ...")
        daemon = {
                  1: jobSubmissionDaemon.FanmodSubmissionDaemon(pid,stdout = out,stderr = err),
                  2: jobSubmissionDaemon.FanmodOutputSubmissionDaemon(pid,stdout = out,stderr = err)
                  }[daemonMode]
        daemon.init(1,self.userDirName,self.jobId,params,email)
        self.logger.log(2, "starting")
        daemon.start()
        self.logger.log(2, "executed")
        
    def __buildUserDir(self):
        import shutil
        try:
            self.logger.log(2, "making user directories on [%s]"%self.LocalDirPath)
            self.logger.log(1, "OS response: %s"%os.mkdir(self.LocalDirPath) )
            self.logger.log(1, "copying dist file: %s"% shutil.copyfile(os.path.join(self.CGIDirPath, Conf.undict_file), os.path.join(self.LocalDirPath, Conf.undict_file)) )
            self.logger.log(1, "copying network file: %s"% shutil.copyfile(os.path.join(self.CGIDirPath, Conf.txt_file), os.path.join(self.LocalDirPath, Conf.txt_file)) )
        except Exception as inst:
            self.logger.log(3, inst)
        


    
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This program executes a daemon that runs FANMOD and handles the output.')
    parser.add_argument( 'jobId',type=str, help='session job ID.')
    parser.add_argument( 'folder',type=str, help='session folder name.')
    parser.add_argument( '--email',type=str, dest='email', default=None, help='user e-mail.')
    args = parser.parse_args()
    #print args
    
    ex = Executor(args.jobId, args.folder,args.email)
    ex.runFanmod()
