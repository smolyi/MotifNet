import MySQLdb
from Logger import Logger
from conf import Conf
import json 

class Motif:
    def __init__(self,adj,size,pvalue,zscore,frequency,img_file_name):
        self.adj = str(adj)
        self.size = int(size) #number of vertices
        self.pval = float(pvalue)
        self.zscore = float(zscore)
        self.freq = float(frequency)
        self.img_path = img_file_name
        self.instances = []
            
    
    def addInstance(self,toadd):
        self.instances.append(toadd)
    def __len__(self):  return len(self.instances)  
    

class MotifJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Motif):
            return super(MotifJSONEncoder, self).default(obj)
        return obj.__dict__
'''  
import json       
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Motif):
            return super(MyEncoder, self).default(obj)
        return obj.__dict__
m = Motif("adj", "0", "0", "0", "0", 'img_file_name')
m.addInstance([1,2,3])
print json.dumps(m,skipkeys = True, cls=MyEncoder)
  
     
    def getAdjAsMat(self):
        mat = []
        for i in range(0,self.size):
            arr = []
            for j in range(0,self.size):
                arr.append(self.adj[i*self.size+j])
            mat.append(arr)
        return mat
    
    def __str__(self): return "%s\t%d\t%f\t%f\t%f"%(self.adj,len(self.instances),self.pval,self.zscore,self.freq)
    
     
    
    def getColorsFromAdj(self,adj):
        edges = set()
        nodes = []
        for i in range(1,self.size+1):
            row = adj[(i-1)*self.size:i*self.size]
            for j in range(1,self.size+1):
                if i!=j:edges.add(int(row[j-1]))
                if i==j:nodes.append(int(row[j-1]))
        return edges,nodes
    
    def has_edge_color(self,color):
        if self.edge_colors:return (color in self.edge_colors)
        return False
    def has_node_color(self,color):
        if self.node_colors:return (color in self.node_colors)
        return False
        
    def getNodesFrequencyDict(self):
        size = len(self)
        instancesDict = {}
        for ins in self.instances:
            for node in ins:
                if not instancesDict.has_key(node):instancesDict[node] = 0
                instancesDict[node] += 1
        for node in instancesDict: instancesDict[node] = float(instancesDict[node])/size
        _list = map(lambda x: (x, instancesDict[x]), instancesDict.keys())
        _list.sort( key=lambda x:x[1], reverse=True)
        return _list
    def getEdgesFrequencyTable(self,sort = -1):
        instancesDict = {}
        for ins in self.instances:
            pos = 0
            for i in range(0,self.size):
                for j in range(0,self.size):
                    if i!=j:
                        edge = "%s,%s"%(ins[i],ins[j])
                        if int(self.adj[i*self.size+j])>0:
                            if not instancesDict.has_key(edge): instancesDict[edge] = [0]*(int(math.factorial(self.size))+1)
                            instancesDict[edge][pos] += 1
                            instancesDict[edge][int(math.factorial(self.size))] += 1
                        pos += 1
                            
        for edge in instancesDict: 
            for i in range (0,len(instancesDict[edge])):
                instancesDict[edge][i] = float(instancesDict[edge][i])/len(self)
                
        _list = map(lambda x: (x, instancesDict[x]), instancesDict.keys())
        _list.sort( key=lambda x:x[1][sort], reverse=True)
        return _list
    def getNodesFrequencyTable(self,sort = -1):
        instanceDict = {}
        for ins in self.instances:
            for i in range (0,self.size):
                if not instanceDict.has_key(ins[i]): instanceDict[ins[i]] = [0]*(self.size+1)
                instanceDict[ins[i]][i] += 1
                instanceDict[ins[i]][self.size] += 1
                
        for node in instanceDict: 
            for i in range (0,len(instanceDict[node])):
                instanceDict[node][i] = float(instanceDict[node][i])/len(self)
                
        _list = map(lambda x: (x, instanceDict[x]), instanceDict.keys())
        _list.sort( key=lambda x:x[1][sort], reverse=True)
        return _list
    '''
    

  
class Session:
    def __init__(self,ID,name,email,size,count,nodes,edges,node_colors,edge_colors,_type, timeStamp, directory = "-", comments = "-"):
        self.id = ID
        self.name = name
        self.email = email
        self.size = size
        self.count = count
        self.nodes = nodes
        self.edges = edges
        self.node_colors = node_colors
        self.edge_colors = edge_colors
        self.type = _type
        self.directory = directory
        self.comments = comments
        self.time = timeStamp
        
class SessionJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Session):
            return super(SessionJSONEncoder, self).default(obj)
        return obj.__dict__  
 
#m = Session("ID", 'name', 'email', 'size', 'count', 'nodes', 'edges', 'node_colors', 'edge_colors', '_type', 'timeStamp', 'directory', 'comments')
#print json.dumps(m,skipkeys = True, cls=SessionJSONEncoder)
class Query:
    def __init__(self, host = Conf.host,user = Conf.user, passwrd = Conf.password, db=Conf.db, port = Conf.port):
        self.logger = Logger("query",Conf.LogFilePath)
        self.logger.log(2, "connecting to db..")
        con = MySQLdb.connect(host = host,user = user, passwd = passwrd, db = db, port = port)
        self.cursor = con.cursor()
        self.logger.log(2, "done.")
        
    def queryMotifs(self,
                    jobId,
                    proteins = [[],[]],
                    proteins_world = [],
                    edge_colors = [[],[]],
                    no_edge_colors = [],
                    node_colors = [[],[]],
                    no_node_colors = [],
                    min_instances = 1, 
                    max_pvalue = 1, 
                    min_zscore = 0,
                    min_frequency = 0.0):
        """
        query 
        @param adj: string - adjacency matrix 
        @param proteins: a tuple, 
            proteins[0] - list of strings(proteins) 
            proteins[1] - integer. 
        @param edge_colors: a tuple, 
            edge_colors[0] - list of booleans(edge_colors in query) 
            edge_colors[1] - boolean. 
        @param node_colors: a tuple, 
            node_colors[0] - list of booleans(node_colors in query) 
            node_colors[1] - boolean. 
        """
        self.logger.log(2,"proteins: %s,%s"%(proteins,proteins_world))
        self.logger.log(2,"nodes: %s,%s"%(node_colors ,no_node_colors))
        self.logger.log(2,"edges: %s,%s"%(edge_colors ,no_edge_colors))
        self.logger.log(2,"stats: %s,%s,%s,%s"%(min_instances,max_pvalue,min_zscore,min_frequency))
        '''
        self.cursor.execute("SELECT size from %s WHERE id=%s"%(Conf.sessionsTable,jobId))
        res = self.cursor.fetchall()
        if len(res)==0:
            raise Exception("jobId '%s' was not found."%jobId)
        '''
        
        qry = "SELECT %s.adj,pvalue,zscore,freq,imageFile "%Conf.motifsTable
        qry += " from %s  JOIN %s ON %s.adj=%s.adj  LEFT JOIN %s ON %s.adj=%s.adj AND %s.jobId=%s.jobId WHERE %s.jobId=%s AND pvalue<=%f AND zscore>=%f AND freq>=%f AND "%(
          Conf.motifsTable,
          Conf.motifsColorsTable,
          Conf.motifsTable,
          Conf.motifsColorsTable,
          Conf.subgraphsTable,
          Conf.motifsTable,
          Conf.subgraphsTable,
          Conf.motifsTable,
          Conf.subgraphsTable,
          Conf.motifsTable,
          jobId,
          max_pvalue, 
          min_zscore,
          min_frequency  )

        edges_qry = ""
        nodes_qry = ""
        protein_qry = ""
        no_edges_qry = ""
        no_nodes_qry = ""
        
        if self.__atleastOne(edge_colors[0]): edges_qry = self.__generateTupleQueryString(edge_colors[0], "edgeColor",(edge_colors[1]),1)
        if self.__atleastOne(node_colors[0]): nodes_qry = self.__generateTupleQueryString(node_colors[0], "nodeColor",(node_colors[1]),0)
        if self.__atleastOne(no_edge_colors): no_edges_qry = self.__generateTupleQueryString(no_edge_colors, "edgeColor",False,1, positive = False)
        if self.__atleastOne(no_node_colors): no_nodes_qry = self.__generateTupleQueryString(no_node_colors, "nodeColor",False,0, positive = False)
        if self.__atleastOne(proteins[0]) and self.__hasSubgraphs(jobId): protein_qry = " (%s)"%self.__generateProteinsQueryString(proteins[0],int(proteins[1]),3)  
        
        if edges_qry: qry += " (%s) AND "%edges_qry
        if nodes_qry: qry += " (%s) AND "%nodes_qry
        if no_edges_qry: qry += " (%s) AND "%no_edges_qry
        if no_nodes_qry: qry += " (%s) AND "%no_nodes_qry
        if protein_qry: qry += " (%s)  "%protein_qry
        
        qry = qry.strip("AND ").strip("WHERE")
        self.logger.log(2,qry)
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
        self.logger.log(2,"%d subgraphs found."%len(res))
        
        motifsDict = {}
        for inst in res:
            if not motifsDict.has_key(inst[0]): 
                motifsDict[inst[0]] = Motif(str(inst[0]), self.__getSizeFromAdj(str(inst[0])), inst[1], inst[2], inst[3], inst[4])
        
        filter_subgraphs_by_proteins = False
        if filter_subgraphs_by_proteins:
            subgraphs = self.__querySubgraphs(jobId,motifsDict,proteins)
        else:
            subgraphs = self.__querySubgraphs(jobId,motifsDict)
            
        ans = {}
        for adj in motifsDict:
            motif = motifsDict[adj]
            if (len(motif)>=min_instances or not subgraphs):
                ans[adj] = motifsDict[adj]

        self.logger.log(2,"%d motifs found on total."%len(motifsDict)) 
        self.logger.log(2,"%d motifs found after elimination."%len(ans))  
        return ans
     
                                        
    def queryMotifByAdj(self,jobId,adj):
        '''
        query specific motif according to adjacency matrix
        
        Return
        ------
            Motif instance if motif exists. or None otherwise.
        '''
        size = self.__getSizeFromAdj(adj)
        qry = "SELECT %s.adj,pvalue,zscore,freq,imageFile"%Conf.motifsTable
        for i in range(1,size+1):
            qry += ",node%d"%i
        qry += " from %s JOIN %s ON %s.adj=%s.adj AND %s.jobId=%s.jobId WHERE %s.jobId=%s AND"%(Conf.motifsTable,Conf.subgraphsTable,Conf.motifsTable,Conf.subgraphsTable,Conf.motifsTable,Conf.subgraphsTable,Conf.motifsTable,jobId)
        qry += " %s.adj=\'%s\' "%(Conf.motifsTable,adj)
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
        
        if len(res)>=1:
            motif = Motif(res[0][0], self.__getSizeFromAdj(str(res[0][0])), res[0][1], res[0][2], res[0][3], res[0][4])
            for item in res:
                motif.addInstance(item[5:])
            return motif
        elif len(res)==0:
            return Exception("0 motifs were found for adj '%s' and jobId '%s' ."%(adj,jobId))
     
    def createUser(self,username,email,institution):
        res = self.queryUser(username)
        if len(res)>0:
            return ["User already exists."]
        qry = "INSERT into %s (name,email,institution) VALUES ('%s','%s','%s')  " %( Conf.usersTable,
                                                                                  MySQLdb.escape_string(username),
                                                                                   MySQLdb.escape_string(email),
                                                                                    MySQLdb.escape_string(institution))
        self.logger.log(2,qry)
        self.cursor.execute(qry)
        return self.queryUser(username)
        
    
    def queryUser(self,username):
        """
        query user details
        
        return
        ------
            set of integers that represent edge colors.
        """
        qry = "SELECT * from %s WHERE name='%s'  " %( Conf.usersTable, MySQLdb.escape_string(username))
        self.logger.log(2,qry)
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
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
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
        s = set()
        for inst in res: s.add(inst[0])
        return s
       
        
    def queryAllSessions(self,user = None):
        """
        query all sessions in db.
        
        return
        ------
            list of Sessions.
        """
        qry = "SELECT id,name,email,size,count,nodes,edges,node_colors,edge_colors,type,time,comments from %s "%(Conf.sessionsTable)
        if user!=None:
            qry += "WHERE user='%s'"%user
        
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
        ans = []
        for inst in res:
            ans.append(Session(inst[0], inst[1], inst[2], inst[3], inst[4], inst[5], inst[6], inst[7], inst[8], inst[9], str(inst[10]),comments = inst[11]))
        return ans
    
    def deleteSession(self,jobId):
        """
        delete session from db according to jobId
        """
        qry = "DELETE FROM %s WHERE jobId="%Conf.subgraphsTable+str(jobId)
        self.cursor.execute(qry)
      
    
    
    def querySession(self,jobId):
        """
        query session data according to jobId
        
        return
        ------
            Session instance.
        """
        qry = "SELECT id,name,email,size,count,nodes,edges,node_colors,edge_colors,type,time,directory,comments from %s WHERE id=%s"%(Conf.sessionsTable, jobId)
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
        if len(res) < 1: raise Exception("no session found with jobId - %s"%jobId)
        elif len(res) > 1: raise Exception( "%d sessions found with jobId - %s"%(len(res),jobId))
        return Session(res[0][0],res[0][1],res[0][2],res[0][3],res[0][4],res[0][5],res[0][6],res[0][7],res[0][8],res[0][9],res[0][10],res[0][11],res[0][12])
    
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
            self.cursor.execute(qry)
            res = self.cursor.fetchall()
            
            if len(res)>0:
                for inst in res:
                    if inst[1] in motifsDict: 
                        motifsDict[inst[1]].addInstance(inst[3:])
                return True
            else:
                return False
           
    def __hasSubgraphs(self,jobId):
        qry = "SELECT count(*) from %s WHERE jobId=%s"%(Conf.subgraphsTable, jobId)
        self.cursor.execute(qry)
        res = self.cursor.fetchall()
        if res[0][0] > 0: return True
        else: return False
        
    def __generateTupleQueryString(self,_tuple,field,atleastOne,strart_ind,positive = True):
        qry = ""
        self.logger.log(1,str(_tuple))
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
    