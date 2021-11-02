import sys

sys.path.append("../Server/Server")
sys.path.append("../Server/Infrastructure")


LISTENER_IP = "132.72.23.114" #"127.0.0.1" #"132.72.216.162"
LISTENER_PORT = 32004
#from ExceptionHandler import ExceptionHandler
#from Serialization import *

#import generateGraph
#from ResponseGraphToGraphMLConvertor import *

sys.setrecursionlimit(10000) #????

import xmlrpclib
serverProxy = xmlrpclib.ServerProxy("http://%s:%s" % (LISTENER_IP, LISTENER_PORT))

class BasicQueriesCGI:

    """
    Administrators actions
    """
    def CreateUser(self, userName, email, institution):
        return serverProxy.CreateUser(userName, email, institution)

    def DeleteSession(self,sessionID):
        return serverProxy.DeleteSession(sessionID)

    def DeleteUser(self,userId):
        return serverProxy.DeleteUser(userId)

    """
    Session Action
    """
    def GetSessions(self, userName):
        return serverProxy.GetSessions(userName)

    def LoadSession(self, sessionid):
        return serverProxy.LoadSession(sessionid)

    def GetAllMotifs(self, sessionID):
    #retData = serverProxy.GetAllMotifs(sessionID)
        return serverProxy.GetAllMotifs(sessionID)

    def GetAllGenes(self, sessionID):
    #retData = serverProxy.GetAllMotifs(sessionID)
        return serverProxy.GetAllGenes(sessionID)

    def GetGenes(self, sessionID, gene):
    #retData = serverProxy.GetAllMotifs(sessionID)
        return serverProxy.GetGenes(sessionID, gene)

    def GetUser(self,userName):
        return serverProxy.GetUser(userName)

    def GetMotifs(self, sessionID):
        return serverProxy.GetMotifs(sessionID)

    def GetMotifsOLD(self, sessionID, proteins, proteins_world, edge_colors, no_edge_colors, node_colors, no_node_colors, min_instances, max_pvalue, min_zscore, min_frequency):
        return serverProxy.GetMotifs(sessionID, proteins, proteins_world, edge_colors, no_edge_colors, node_colors, no_node_colors, min_instances, max_pvalue, min_zscore, min_frequency)

    def GetMotif(self,sessionID, adj):
        return serverProxy.GetMotif(sessionID, adj)

    #MotifNet actions
    def SubmitJob(self, userName, jobName, motifSize, edgeFiles, directedEdgeFiles, nodeFiles, nodeFilesLabels, maxPvalue = 0.05, minInstances = 1, minZScore = 0, maxDanglingEdges = 0, onlyColored = "on"):
        retData = serverProxy.SubmitJob(userName, jobName, motifSize, edgeFiles, directedEdgeFiles, nodeFiles, nodeFilesLabels, maxPvalue, minInstances, minZScore, maxDanglingEdges, onlyColored)
        return retData

    def SubmitFanmodOutput(self):
        return "SubmitFanmodOutput"
        retData = serverProxy.SubmitFanmodOutput()
        return retData

if __name__ == "__main__":

    #print BasicQueriesCGI().GetUser("skuper")

    res = BasicQueriesCGI().GetMotifs(110, [[],1], [], [[],1], [], [[],1], [], 	0, 0.05, 0, 0)
    print len(res)
    '''
    for item in res:
        print res[item]['img_path']
    '''
    print BasicQueriesCGI().GetMotif(110,"010100110")
