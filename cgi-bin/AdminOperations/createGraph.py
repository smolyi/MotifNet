import pickle,os, sys

sys.path.append("/home/skuper/workspace/MotifNetNew/cgi-bin/JobSubmissionPackage/Includes/")
sys.path.append("/media/disk2/users/motifnet/Websites/Product/cgi-bin/JobSubmissionPackage/Includes/")

from conf import Conf

from fanmodGraph import FanmodGraph

def run( sessionDir, jobId):  
    sessionDirPath = os.path.join(Conf.Sessions_dir, sessionDir)
    FanmodSessionDirPath = os.path.join(Conf.FANMOD_Sessions_dir,sessionDir)
     
    files = os.listdir(os.path.join(sessionDirPath,Conf.EdgesFilesDir))
    edges = []
    for filename in files:
        edges.append(os.path.join(sessionDirPath,Conf.EdgesFilesDir,filename))
    
    files = os.listdir(os.path.join(sessionDirPath,Conf.NodesFilesDir))
    nodes = []
    for filename in files:
        nodes.append(os.path.join(sessionDirPath,Conf.NodesFilesDir,filename))
    
    inputGraphFilePath = os.path.join(sessionDirPath,Conf.txt_file)
    
    edges.sort()
    nodes.sort()
    
    print  str([inputGraphFilePath,os.path.join(sessionDirPath),edges,nodes])
    
    fg = FanmodGraph(inputGraphFilePath,
                [os.path.join(sessionDirPath,Conf.dict_file),os.path.join(sessionDirPath,Conf.undict_file)],
                edges,nodes,[False,True])    


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
    
    
   


