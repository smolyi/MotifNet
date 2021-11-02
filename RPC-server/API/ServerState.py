#from Configuration import *
#from Serialization import *
import os,traceback
from conf import Conf
from DBConnection import DBConnection
from SessionHandler.SessionManager import SessionManagerSingleton,SessionManager
from Query import Query
 

class ServerState:
    """
    class holds the RPC server's state at any given time.
    this include:

    1) Sessions in use at this moment
    2) live SQL connection


    Attributes
    ----------
        SessionManager : SessionManager
        sqlConnection : SQLConnection


    """


    def __init__(self,logger = None, DBlogger = None):
        self.sqlConnection = DBConnection(Conf.host,Conf.user,Conf.password,Conf.port,Conf.db ,DBlogger)
        self.sessionsManager = SessionManager() #SessionManagerSingleton()
        self.queryInterface = Query(self.sqlConnection)
        self.logger = logger


    """
    Administrators actions
    """
    def CreateUser(self, userName, email, institution):
        self.__safelog(2, "creating user with params - %s"%[userName, email, institution])
        return self.queryInterface.createUser(userName, email, institution)
       
    def DeleteSession(self,sessionID):
        self.__safelog(2, "deleting session - %s"%[sessionID])
        try:
            self.queryInterface.deleteSession(sessionID)
            return True
        except Exception as inst:
            self.__safelog(4, "Error - %s"%[inst])
            return False
    
    def DeleteUser(self,userId):
        self.__safelog(2, "deleting user - %s"%[userId])
        raise Exception("deleteUser is not implemented!")


    """
    Session Action
    """
    def GetUser(self,userName):
        self.__safelog(2, "retrieving user - %s"%[userName])
        return self.queryInterface.queryUser(userName)

    def GetSessions(self, userName):
        self.__safelog(2, "retrieving all sessions for user - %s"%[userName])
        try: 
            res =  self.queryInterface.queryAllSessions(userName)
            self.__safelog(2, "%d items"% len(res))
            return res
        except Exception as inst:
            self.__safelog(4, inst)
            
    def GetSessionsById(self, userId):
        self.__safelog(2, "retrieving all sessions for user id - %s"%[userId])
        return self.queryInterface.queryAllSessionsById(userId)


    def LoadSession(self, sessionID):
        self.__safelog(2, "retrieving session - %s"%[sessionID])
        if not self.sessionsManager.isInSessions(sessionID):
            self.__safelog(2, "session is not in memory. querying database ...")
            sessionData = self.queryInterface.querySession(sessionID)
            if not sessionData:
                self.__safelog(4, "error querying DB - %s"%sessionData)
                return False
            self.sessionsManager.newSession(sessionID,  sessionData)
            self.__safelog(2, "new session added to memory.  - %s"%[sessionID])
        return self.sessionsManager.getSession(sessionID)

    
    def GetMotifs(self, sessionID):
        try:
            self.__safelog(1, "querying motifs with params - %s"%[sessionID])
            if self.LoadSession(sessionID):
                session = self.sessionsManager.getSession(sessionID)
                if not session:
                    self.__safelog(4, "session is not in memory - %s"%sessionID)
                self.__safelog(2, "session found. querying motifs in database ...")
                #session.lastQuery = (proteins, proteins_world, edge_colors, no_edge_colors, node_colors, no_node_colors, min_instances, max_pvalue, min_zscore, min_frequency)
                session.motifs = self.queryInterface.queryMotifs(sessionID)
                self.__safelog(2, "new motifs list of size [%d] was added to memory to session  - %s"%(len(session.motifs),sessionID))

                return session
            self.__safelog(4, "error loading session into memory.")
            return False
        except Exception as inst:
            self.__safelog(4, inst)
            self.__safelog(4, traceback.format_exc().__str__())
            
    def GetMotifsold(self, sessionID):
        try:
            self.__safelog(1, "querying motifs with params - %s"%[sessionID])
            if self.LoadSession(sessionID):
                session = self.sessionsManager.getSession(sessionID)
                if not session:
                    self.__safelog(4, "session is not in memory - %s"%sessionID)
                self.__safelog(2, "session found. querying motifs in database ...")
                #session.lastQuery = (proteins, proteins_world, edge_colors, no_edge_colors, node_colors, no_node_colors, min_instances, max_pvalue, min_zscore, min_frequency)
                session.motifs = self.queryInterface.queryMotifs(sessionID)
                self.__safelog(2, "new motifs list of size [%d] was added to memory to session.  - %s"%(len(session.motifs),sessionID))

                # no need for this - graphs are now created on the client side
                # ============================================================
                # self.__safelog(2, "creating motifs images ...")
                # session = self.__createMotifsImages(session)
                # self.sessionsManager.setSessionData(sessionID,session)
                # self.__safelog(2, "done." )

                return session
            self.__safelog(4, "error loading session into memory.")
            return False
        except Exception as inst:
            self.__safelog(4, inst)
            self.__safelog(4, traceback.format_exc().__str__())

    def GetMotif(self,sessionID, adj):
        self.__safelog(2, "querying motif with params - %s"%[sessionID, adj])
        '''
        if not self.LoadSession(sessionID):
            self.__safelog(4, "session [%s] is not in memory"%sessionID)
            raise Exception("session [%s] is not in memory"%sessionID)
        session = self.sessionsManager.getSession(sessionID)
        if not adj in session.motifs:
            self.__safelog(3, "motif [%s] is not in sessions's memory."%adj)
            raise Exception("motif [%s] is not in sessions's memory."%adj)
        motif = session.motifs[adj]
        if len(motif.instances)==0:
            self.__safelog(3, "motif [%s] has no subgraphs. querying subgraphs ..."%adj)
        '''
        try:
            motifTMP = self.queryInterface.queryMotifByAdj( sessionID, adj)
            motif = motifTMP
        except Exception as inst:
            self.__safelog(3, "failed [%s] "%inst)

        return motif

    def GetAllMotifs(self, sessionID):
        self.__safelog(2, "querying all subgraphs and motifs from jobID - %s" % [sessionID])
        allMotifs = self.queryInterface.querySubgraphs(sessionID)
        return allMotifs

    def GetAllGenes(self, sessionID):
        self.__safelog(2, "querying all genes from jobID - %s" % [sessionID])
        allGenes = self.queryInterface.queryAllJobGenes(sessionID)
        return allGenes

    def GetGenes(self, sessionID, gene):
        self.__safelog(2, "querying genes from jobID - %s" % [sessionID])
        genes = self.queryInterface.queryJobGenes(sessionID, gene)
        return genes

    #Submission actions
    def SubmitJob(self, userName, jobName, motifSize, edgeFiles, directedEdgeFiles, nodeFiles, nodeFilesLabels, maxPvalue = 0.05, minInstances = 1, minZScore = 0, maxDanglingEdges = 0, onlyColored = "on"):
        self.__safelog(2, "SubmitJob not implemented")
        raise Exception("SubmitJob not implemented")

    def SubmitFanmodOutput(self):
        self.__safelog(2, "SubmitFanmodOutput not implemented")
        raise Exception("SubmitFanmodOutput not implemented")

    def __buildJobDir(self):
        self.__safelog(2, " __buildJobDir not implemented")
        raise Exception(" __buildJobDir not implemented")

  

    #infra
    def __safelog(self,level,msg):
        if self.logger: self.logger.log(level,msg)

if __name__ == "__main__":
    s = ServerState()
    print s.GetUser("ilan")
