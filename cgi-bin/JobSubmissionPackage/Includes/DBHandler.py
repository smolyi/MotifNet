import os,pickle,traceback
from conf import Conf 
import MySQLdb,time

 
class DBHandler:
    """
    This module communicates with motifnet database
    @param userName: string specifies the user name (must be unique).
    @param jobName: string specifies the job name (must be unique).
    """
    def __init__(self, logger = None):
        self.logger = logger
                
        #db connection
        self.__log(1,"connecting to DB ...")
        try:
            self.con = MySQLdb.connect(host = Conf.host, port=Conf.port, user = Conf.user, passwd = Conf.password, db=Conf.db)
            self.__log(1,self.con)
        except Exception as inst:
            self.__log(5, "failed to connect to database.")
            self.__log(5, inst)
            raise Exception("failed to connect to database.")
        self.cursor = self.con.cursor()  
        
    def __reconnect(self):
        self.__log(1,"reconnecting to DB ...")
        self.close()
        try:
            self.con = MySQLdb.connect(host = Conf.host, port=Conf.port, user = Conf.user, passwd = Conf.password, db=Conf.db)
            self.__log(1,self.con)
        except Exception as inst:
            self.__log(5, "failed to connect to database.")
            self.__log(5, inst)
            raise Exception("failed to connect to database.")
        self.cursor = self.con.cursor()  
        
    def close(self):
        try:
            self.cursor.close()
            self.con.close()
        except Exception as inst:
            self.__log(4, "failed to close database.")
            self.__log(4, inst)
        
    def loadSession(self, userName, jobName, motifSize, rootDirName, email = "", comments = "", arguments = "---"):
        userName = MySQLdb.escape_string(userName)
        jobName = MySQLdb.escape_string(jobName)
        email = MySQLdb.escape_string(email)
        comments = MySQLdb.escape_string(comments)

        try :
            qry = "INSERT INTO %s (directory,name,size,email,comments,user, arguments) VALUES (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')"\
            %(Conf.sessionsTable, 
              MySQLdb.escape_string(rootDirName), MySQLdb.escape_string(jobName),motifSize, MySQLdb.escape_string(email),
               MySQLdb.escape_string(comments), MySQLdb.escape_string(userName), MySQLdb.escape_string(arguments) )
            self.__executQry(qry)
                  
            qry = "SELECT id FROM %s WHERE directory='%s'"%(Conf.sessionsTable,MySQLdb.escape_string(rootDirName))
            self.cursor.execute(qry)
            res = self.cursor.fetchall()
            if len(res)!=1:
                self.__log(4,"ERROR: %d sessions found."%len(res))
                raise Exception("error fetching job id. %d sessions found"%len(res))
                
            self.jobId = res[0][0]
            return self.jobId
            
        except Exception as inst:
            self.__log(5, "%s , %s."%(inst, qry))  
            return -1
       
       
    def updateSession(self, jobId ,motifs, network, status = 1):
        self.__log(1,"updating session details [jobId=%s ]"%jobId)
        numberofMotifs = len(motifs)
        #numberofSubgraph = sum(map(lambda x:len(x.instances), motifs ) )
        numberofNodes = len( set( map(lambda x: x[0], network) + map(lambda x: x[1], network) ) )
        numberofEdge = len(network)
        numberofNodeColors = len( set( map(lambda x: x[2], network) + map(lambda x: x[3], network) ) )
        numberofEdgeColors = len( set( map(lambda x: x[4], network)  ) )

        qry = "update %s SET count='%d', nodes='%d', edges='%d', node_colors='%d', edge_colors='%d', status='%d' WHERE id='%s' "%(Conf.sessionsTable,
                                                                                                                  numberofMotifs,
                                                                                                                  numberofNodes,
                                                                                                                  numberofEdge,
                                                                                                                  numberofNodeColors,
                                                                                                                  numberofEdgeColors,
                                                                                                                  status, jobId)
        self.__executQry(qry)

    def updateSessionStatus(self, jobId ,status):
        self.__log(1,"updating session status [jobId=%s] "%jobId)
        
        qry = "update %s SET status='%d' WHERE id='%s' "%(Conf.sessionsTable,
                                                          status,
                                                           jobId)
        self.__executQry(qry)

    def updateSessionNetwork(self, jobId ,nodes, edges):
        self.__log(1,"updateSessionNetwork [jobId=%s] "%jobId)
        
        qry = "update %s SET nodes='%d', edges='%d'  WHERE id='%s' "%(Conf.sessionsTable,
                                                          nodes,edges,
                                                           jobId)
        self.__executQry(qry)

        
    def loadNetworkFiles(self, jobId, nodefiles , edgefiles):
        self.__log(1,"loading network file names to DB [jobId=%s] ..."%jobId)
        
        qry = "UPDATE %s SET nodefiles='%s', edgefiles='%s' WHERE id='%s' "\
        %(Conf.sessionsTable,",".join(nodefiles), ",".join(edgefiles),jobId)
       
        self.__executQry(qry.strip(", "))        
        
        
    def loadNetwork(self, network, jobId = None):
        
        jobId = self.__jobID(jobId)
        self.__log(1,"loading network to DB [jobId=%s] ..."%jobId)
        
        if len(network)>0:
            keys = "jobId,node1,node2,nodeColor1,nodeColor2,edgeColor"
            qry = "INSERT INTO %s (%s) VALUES "%(Conf.networkTable,keys)
         
            for edge in network:
                int1 = edge[0]
                int2 = edge[1]
                qry += " (%s,'%s','%s',%d,%d,%d), "%(jobId, MySQLdb.escape_string(int1),MySQLdb.escape_string(int2),int(edge[2]),int(edge[3]),int(edge[4]))

            self.__executQry(qry.strip(", "))
            return True
        else: 
            self.__log(3,"network is empty")
            return False
            
    

        
          
    def loadMotifs(self,motifs, subgraphs, numberOfEdgeColors = 7, numberOfNodeColors=16, jobId = None):
        MOTIF_SUCCESS = True
        SUBGRAPHS_SUCCESS = True
        
        jobId = self.__jobID(jobId)
        self.__log(1,"loading motifs to DB [jobId=%s ..."%jobId)

        if len(motifs)==0:
            self.__log(3,"no motifs found.")
            return False
        
        keys = "jobId, adj, pvalue, zscore, freq, count"
        keys += ", dispersity, minDispersity, maxDispersity, duplicates"
        motifsQry = "INSERT INTO %s (%s) VALUES"%(Conf.motifsTable,keys)
        
        '''
        keys = "adj "
        for i in range (1,numberOfEdgeColors+1):  keys += ",edgeColor%d "%i
        for i in range (0,numberOfNodeColors):  keys += ",nodeColor%d "%i
        motifsColorsQry = "INSERT INTO %s (%s) VALUES "%(Conf.motifsColorsTable,keys)
        '''
        
        
        size = -1
        for motif in motifs.values():
            size = motif.size
            
            vals = "\'%s\', \'%s\', %f, %f, %f, %d"%(jobId, motif.adj,motif.pval,motif.zscore,motif.freq, len(motif.instances))
            vals += ", %f, %f, %f, %d"%(motif.dispersity,motif.minDispersity,motif.maxDispersity,motif.containsDuplicates)
            motifsQry += "(%s), "%(vals) 
        
            '''
            vals = "\'%s\' "%( motif.adj)
            for i in range (1,numberOfEdgeColors+1):  
                if motif.has_edge_color(i):vals += ",1"
                else: vals += ",0"
            for i in range (0,numberOfNodeColors):  
                if motif.has_node_color(i):vals += ",1"
                else: vals += ",0"
            motifsColorsQry += "(%s), "%(vals) 
            '''
        
        self.__log(2, "dumping motifs ...")
        MOTIF_SUCCESS = MOTIF_SUCCESS and self.__executQry(motifsQry.strip(", "))
            
        '''             
        self.__log(2, "dumping motif colors ...")   
        self.__executQry(motifsColorsQry.strip(", ")+ "ON DUPLICATE KEY UPDATE adj=adj")
        '''
        
        #instances
        if subgraphs:
            keys = "jobId, adj,sorted"
            for i in range (1,size+1):keys += ", node%d"%i
            subgraphsQry = "INSERT INTO %s (%s) VALUES "%(Conf.subgraphsTable,keys)
            self.__log(1, subgraphsQry)
            counter = 0
            for motif in motifs.values():
                for inst in motif.instances:
                    counter += 1
                    vals = "%s, %s"%(jobId,motif.adj)
                    
                    '''
                    sortedInstances = self.__sortInstance(inst,motif.getAdjAsMat())
                    vals += ",%d"%len(sortedInstances)
                    if len(sortedInstances) >= 1:
                        inst = sortedInstances[0]
                    '''
                    vals += ",0"
                    for i in range (1,size+1):
                        vals += ",'%s'"%MySQLdb.escape_string(inst[i-1])
                    subgraphsQry += "(%s), "%(vals) 
                    if counter%100000==0:
                        self.__log(2, "dumping subgraphs ...")
                        SUBGRAPHS_SUCCESS = SUBGRAPHS_SUCCESS and self.__executQry(subgraphsQry.strip(", "))
                        subgraphsQry = "INSERT INTO %s (%s) VALUES "%(Conf.subgraphsTable,keys)
            self.__log(2, "dumping subgraphs ...")
            SUBGRAPHS_SUCCESS = SUBGRAPHS_SUCCESS and self.__executQry(subgraphsQry.strip(", "))
      
        else: 
            self.__log(3,"no subgraphs found. could be a bug or user did not supply dump file.")
        return MOTIF_SUCCESS, SUBGRAPHS_SUCCESS
        
    def __log(self,level ,msg):
        if self.logger:
            self.logger.log(level,msg)
        else:
            print msg
    
    def __jobID(self,jobId):
        if not jobId:
            jobId = self.jobId
            if not jobId:
                self.__log(5, "no job ID specified.")
                raise Exception("no job ID specified.")
        return jobId

    def __executQry(self,qry, rerun = True):
        #self.__log(1, qry[0:100])
        try : 
            self.cursor.execute("BEGIN")
            self.cursor.execute(qry)
            self.cursor.execute("COMMIT")
            self.con.commit()
            return True
        
        except Exception as inst:
            self.__log(1, qry[0:100])
            self.__log(4, inst)
            if rerun:
                time.sleep(10)
                self.__reconnect()
                return self.__executQry(qry,False)
            return False
            #self.__log(4, qry[0:100])
            #self.__log(4, traceback.extract_stack())
                   
if __name__=="__main__":
    rootDir = "somerootdir223332" 
    jobName = "test1" 
    email = "ilansmoly@gmail.com"
    network = [('ilan','smoly',1,3,3),('ilan','smoly',1,1,2),]
    print len( set( map(lambda x: x[2], network) + map(lambda x: x[3], network) ) )

    #fh = DBHandler()    
    #print fh.loadSession()
    