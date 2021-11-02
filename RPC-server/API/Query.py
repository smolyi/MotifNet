import MySQLdb

from Logger import Logger
from conf import Conf
import json
from MotifNetSession import MotifNetSession

class Motif:
    def __init__(self,adj,size,pvalue,zscore,frequency, count, disp = -1, mindisp = -1, maxdisp = -1, duplicate = 0):
        self.adj = str(adj)
        self.size = int(size) #number of vertices
        self.pval = float(pvalue)
        self.zscore = float(zscore)
        self.freq = float(frequency)
        self.instances = []
        self.count = count

        self.dispersity = disp
        self.minDispersity = mindisp
        self.maxDispersity = maxdisp
        
        self.duplicate = duplicate



    def addInstance(self,toadd):
        self.instances.append(toadd)
    def __len__(self):  return len(self.instances)
    def clone(self):
        m = Motif(self.adj,self.size, self.pval, self.zscore, self.freq, self.count, self.img_path)
        m.instances = self.instances
        return

class MotifJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Motif):
            return super(MotifJSONEncoder, self).default(obj)
        return obj.__dict__


class Query:
    def __init__(self, sqlConnection ):
        self.logger = Logger("query",Conf.LogFilePath)
        self.sqlConnection = sqlConnection

    def queryMotifs(self, jobId):
              
        self.logger.log(2,"jobId: %s"%(jobId))
        qry = "SELECT adj,pvalue,zscore,freq,count,dispersity, minDispersity, maxDispersity, duplicates  from %s WHERE jobId=%s"%(Conf.motifsTable,jobId)
        self.logger.log(2,qry)
        res = self.sqlConnection.query(qry)
        self.logger.log(2,"%d motifs found."%len(res))


        motifsDict = {}
        for inst in res:
            if not motifsDict.has_key(inst[0]):
                motifsDict[inst[0]] = Motif(str(inst[0]), self.__getSizeFromAdj(str(inst[0])), inst[1], inst[2], inst[3], inst[4], inst[5], inst[6], inst[7], inst[8])
            else:
                self.logger.log(3, "duplicate entries in motifs table - "+ inst[0])

        return motifsDict



    def queryMotifByAdj(self,jobId,adj):
        '''
        query specific motif according to adjacency matrix

        Return
        ------
            Motif instance if motif exists. or None otherwise.
        '''
        size = self.__getSizeFromAdj(adj)
        qry = "SELECT adj,pvalue,zscore,freq,count from %s WHERE jobId=%s AND adj=%s"%(Conf.motifsTable,jobId, adj)
        self.logger.log(1,qry)
        res = self.sqlConnection.query(qry)
        if len(res)>=1:
            motif = Motif(res[0][0], self.__getSizeFromAdj(str(res[0][0])), res[0][1], res[0][2], res[0][3], res[0][4])
            qry = "SELECT * from %s WHERE jobId=%s AND adj=%s"%(Conf.subgraphsTable,jobId, adj)
            self.logger.log(1,qry)
            res = self.sqlConnection.query(qry)

            if len(res)>=1:
                for item in res: 
                    a = list(item[5:4+size])
                    #a.reverse() #change the order of the elements because FANMOD's bug
                    motif.addInstance( item[4:4+size])

            elif len(res)==0:
                self.logger.log(4, "no subgraphs found for adj '%s' and jobId '%s' ."%(adj,jobId))

            return motif
        else:
            self.logger.log(4, "no motif found for adj '%s' and jobId '%s' ."%(adj,jobId))
        return None

    def querySubgraphs(self, jobId):
        from itertools import groupby, chain
        import math
        
        def get_adj(row): 
            """
            the mysql database automatically converts the id to integers 
            so we need to add zeros at the beginning in case they were lost
            """
            size = len(filter( lambda x: x!='-', row[1:] ))
            res = str(row[0])
            for i in range(len(row[0]),size*size):
                res = "0"+res 
            return res

        qry = "SELECT adj, node1, node2, node3, node4, node5, node6, node7, node8 " \
            "FROM %s " \
            "WHERE jobId=%s " \
            "ORDER BY adj " % (Conf.subgraphsTable, jobId)

        self.logger.log(1, qry)
        res = self.sqlConnection.query(qry)
        self.logger.log(1, str(res))
        
        return  {key: list(set(list(chain(*list(value))))) for (key, value) in groupby(res, get_adj)}

    def queryAllJobGenes(self, jobId):
        from itertools import groupby, chain

        q = "SELECT node1 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node2 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node3 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node4 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node5 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node6 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node7 FROM {0} WHERE jobId={1} "\
        "UNION SELECT node8 FROM {0} WHERE jobId={1} "\
        .format(Conf.subgraphsTable, jobId)

        self.logger.log(1, q)
        res = self.sqlConnection.query(q)
        return list(chain(*res))

    def queryJobGenes(self, jobId, gene):
        from itertools import groupby, chain

        q = "SELECT node1 FROM {0} WHERE jobId={1} AND node1 LIKE  '%{2}%' " \
            "UNION " \
            "SELECT node2 FROM {0} WHERE jobId={1} AND node2 LIKE '%{2}%' " \
            "UNION "\
            "SELECT node3 FROM {0} WHERE jobId={1} AND node3 LIKE '%{2}%' "\
            "UNION " \
            "SELECT node4 FROM {0} WHERE jobId={1} AND node4 LIKE '%{2}%' " \
            "UNION "\
            "SELECT node5 FROM {0} WHERE jobId={1} AND node5 LIKE '%{2}%' "\
            "UNION " \
            "SELECT node6 FROM {0} WHERE jobId={1} AND node6 LIKE '%{2}%' " \
            "UNION "\
            "SELECT node7 FROM {0} WHERE jobId={1} AND node7 LIKE '%{2}%' "\
            "UNION " \
            "SELECT node8 FROM {0} WHERE jobId={1} AND node8 LIKE '%{2}%' " \
            " ORDER BY node1 LIMIT 100".format(Conf.subgraphsTable, jobId, gene)

        self.logger.log(1, q)
        res = self.sqlConnection.query(q)
        return list(chain(*res))


    def createUser(self,username,email,institution):
        res = self.queryUser(username)
        if len(res)>0:
            return False
        qry = "INSERT into %s (name,email,institution) VALUES ('%s','%s','%s')  " %( Conf.usersTable,
                                                                                  MySQLdb.escape_string(username),
                                                                                   MySQLdb.escape_string(email),
                                                                                    MySQLdb.escape_string(institution))
        self.logger.log(2,qry)
        self.sqlConnection.execute(qry)
        return True


    def queryUser(self,username):
        """
        query user details

        return
        ------
            set of integers that represent edge colors.
        """
        qry = "SELECT * from %s WHERE name='%s'  " %( Conf.usersTable, MySQLdb.escape_string(username))
        self.logger.log(2,qry)
        res = self.sqlConnection.query(qry)
        if len(res)>1:
            raise Exception("duplicate user names - %s"%username)
        if len(res)==0:
            return [];
        return res[0]

    def queryEdge(self,jobId,int1,int2):
        """
        query all edge colors of the edge between int1 and int2

        return
        ------
            set of integers that represent edge colors.
        """
        qry = "SELECT edgeColor from %s WHERE jobId=%s AND node1='%s' AND node2='%s' " %( Conf.networkTable, jobId, MySQLdb.escape_string(int1),MySQLdb.escape_string(int2))
        self.logger.log(2,qry)
        res = self.sqlConnection.query(qry)
        s = set()
        for inst in res: s.add(inst[0])
        return s


    def queryAllSessions(self,userName = None):
        """
        query all sessions in db.

        return
        ------
            list of Sessions.
        """
        qry = "SELECT tb1.id, name, email, size, tb1.count DIV 1, nodes, edges, node_colors, edge_colors, time, comments, sum(tb2.count), nodefiles, edgefiles, arguments, status " \
              "FROM {0} AS tb1 LEFT JOIN {1} AS tb2 " \
              "ON tb1.id = tb2.jobId "\
            .format(Conf.sessionsTable, Conf.motifsTable)
        if userName is not None:
            qry += "WHERE tb1.user='%s' " % userName

        qry += "GROUP BY tb1.id"

        res = self.sqlConnection.query(qry)
        ans = []
        for inst in res:
            ans.append(MotifNetSession(inst[0], inst[1], inst[2], inst[3], inst[4],inst[11],
                                        inst[5], inst[6], inst[7], inst[8], str(inst[9]),
                                        userName, "directory not supported",inst[10],  inst[12], inst[13], inst[14], inst[15]))
           
        return ans


    def deleteSession(self,jobId):
        """
        delete session from db according to jobId
        """
        #raise Exception("deleteSession is not implemented!")
        qry = "DELETE FROM %s WHERE jobId="+str(jobId)
        self.sqlConnection.execute(qry%Conf.subgraphsTable)
        self.sqlConnection.execute(qry%Conf.motifsTable)
        self.sqlConnection.execute(qry%Conf.networkTable)
        
        qry = "DELETE FROM %s WHERE id="+str(jobId)
        self.sqlConnection.execute(qry%Conf.sessionsTable)
        

    def querySession(self,jobId):
        """
        query session data according to jobId

        return
        ------
            Session instance.
        """
        qry = "SELECT tb1.id, name, email, size, tb1.count DIV 1, nodes, edges, node_colors, edge_colors, time, comments, sum(tb2.count), nodefiles, edgefiles, arguments, status  " \
              "FROM {0} AS tb1 INNER JOIN {1} AS tb2 " \
              "ON tb1.id = tb2.jobId "\
              "WHERE tb1.id='{2}'".format(Conf.sessionsTable, Conf.motifsTable,jobId)
              
        #qry = "SELECT id,name,email,size,count,nodes,edges,node_colors,edge_colors,time,user,directory,comments from %s WHERE id=%s"%(Conf.sessionsTable, jobId)
        self.logger.log(1,qry)
        res = self.sqlConnection.query(qry)
        if len(res) != 1:
            self.logger.log(3, "%d sessions found with jobId - %s"%(len(res),jobId))
            return False
        inst = res[0]
        return MotifNetSession(inst[0], inst[1], inst[2], inst[3], inst[4],inst[11],
                                        inst[5], inst[6], inst[7], inst[8], str(inst[9]),
                                        "userName", "directory not supported",inst[10],  inst[12], inst[13], inst[14], inst[15])
        
        #return MotifNetSession(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4],res[0][5],res[0][6],res[0][7],res[0][8],res[0][9],res[0][10],res[0][11],res[0][12])

    def __querySubgraphs(self,jobId,motifsDict,proteins = None):
        """
        query subgraphs from db and insert them into motifs in motifsDict.
        """
        adjSet = set( motifsDict.keys())
        if len(adjSet)>0:
            qry = "SELECT * from %s WHERE jobId=%s AND ("%(Conf.subgraphsTable,jobId)
            for adjacency in adjSet: qry += " adj=\'%s\' OR"%(adjacency)
            qry = qry.strip("OR") + ")"
            if proteins:
                qry += "AND (%s)" % self.__generateProteinsQueryString(proteins[0], int(proteins[1]), 3)
            self.logger.log(1, qry)
            res = self.sqlConnection.query(qry)

            if len(res)>0:
                for inst in res:
                    if inst[1] in motifsDict:
                        motifsDict[inst[1]].addInstance(inst[3:])
                return True
            else:
                return False

    def __hasSubgraphs(self,jobId):
        qry = "SELECT count(*) from %s WHERE jobId=%s"%(Conf.subgraphsTable, jobId)
        res = self.sqlConnection.query(qry)
        if res[0][0] > 0: return True
        else: return False

    def __generateTupleQueryString(self,_tuple,field,atleastOne,strart_ind,positive = True):
        qry = ""
        for item in _tuple:
            if item:
                if positive: qry += " %s%d=1"%(field,strart_ind)
                else: qry += " %s%d!=1"%(field,strart_ind)
                if atleastOne: qry += " OR"
                else: qry += " AND"
            strart_ind += 1
        if atleastOne: qry = qry.strip("OR")
        else: qry = qry.strip("AND")
        return qry

    def __generateProteinsQueryString(self,proteins,function,nodes_num):
        qry = ""
        for protein in proteins:
            if protein:
                protein = MySQLdb.escape_string(protein)
                qry += " ("
                for i in range(1,nodes_num+1):
                    qry += "node%d=\'%s\' OR "%(i,protein)
                qry = qry.strip(" OR ")
                if function: qry += ") OR"
                else : qry += ") AND"
        if function: qry = qry.strip(" OR")
        else: qry = qry.strip(" AND")
        return qry
    '''
    if function==3:
            for i in range(1,nodes_num+1):
                qry += "("
                for protein in proteins:
                    if protein:
                        protein = MySQLdb.escape_string(protein)
                        qry += " node%d=\'%s\' OR"%(i,protein)
                qry = qry.strip(" OR")+") AND"
            qry = qry.strip("AND")
        else:
    '''

    def __getSizeFromAdj(self,string):
        import math
        root = math.sqrt(len(string))
        if root == int(root): return int(root)
        return -1
    def __atleastOne(self,container):
        for inst in container:
            if inst: return True
        return False
