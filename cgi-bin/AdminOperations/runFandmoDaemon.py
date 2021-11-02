import pickle,os, sys

sys.path.append("/home/skuper/workspace/MotifNetNew/cgi-bin/JobSubmissionPackage/Includes/")
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes/")

from conf import Conf

from jobSubmissionDaemon import FanmodSubmissionDaemon

def run( sessionDir, jobId):  
    sessionDirPath = os.path.join(Conf.Sessions_dir, sessionDir)
    FanmodSessionDirPath = os.path.join(Conf.FANMOD_Sessions_dir,sessionDir)
    
    
    PARAMS_DICT_FILE_PATH = os.path.join(sessionDirPath,"params.pkl")  
    params = pickle.load(open(PARAMS_DICT_FILE_PATH))
        
    DAEMON_DIR_PATH = os.path.join( FanmodSessionDirPath,Conf.DAEMON_DIR_NAME)

    try:
        print (2, "creating daemon directory - [%s]"%DAEMON_DIR_PATH)
   
        print (1,"OS response: %s"%os.mkdir(DAEMON_DIR_PATH))
    except Exception as inst:
        print inst
        
    
    pid = os.path.join( DAEMON_DIR_PATH,"pid.txt")
    out = os.path.join( DAEMON_DIR_PATH,"out.txt")
    err = os.path.join( DAEMON_DIR_PATH,"err.txt")
    
    print (2, "executing daemon ...")
    daemon = FanmodSubmissionDaemon(pid,stdout = out,stderr = err)

    daemon.init(1,sessionDir,jobId,params,"-")
    print (2, "starting Daemon")
    daemon.start()
    print (2, "executed")


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='run output handling daemon.')
    parser.add_argument( 'dir',type=str, help='path to directory.')
    parser.add_argument( 'id',type=int, help='job id.')
    args = parser.parse_args()
    #print args
    
    sessionDir = args.dir
    id = args.id
    
    run(sessionDir,id)
    
    
   


