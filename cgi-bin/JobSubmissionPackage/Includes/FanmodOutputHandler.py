import os,pickle,math
from FanmodCSVParser import CSVParser
from DS import Motif

HARD_CODED_MOTIF_TABLE_FILE_NAME = "motifs.csv"
HARD_CODED_JOB_SUMMARY_FILE_NAME = "summary.txt"

class OutputHandler:
    """
    processes Fanmod's output and dumps the results in a directory and into a DB.   
    """
    def __init__(self, rootDirPath, networkFileName, csvFileName, dumpFileName, dictFileName, labelsDictFileName = None, logger = None):
        self.rootDir = rootDirPath
        self.motifs = {} 
        self.network = {}
        self.node2label = {}
        
        #files
        self.networkFile = os.path.join(self.rootDir, networkFileName)
        self.csvFile = os.path.join(self.rootDir, csvFileName)
        self.dumpFile = os.path.join(self.rootDir, dumpFileName)
        self.motifsFilePath = os.path.join(self.rootDir,HARD_CODED_MOTIF_TABLE_FILE_NAME)
        self.summaryFilePath = os.path.join(self.rootDir,HARD_CODED_JOB_SUMMARY_FILE_NAME)
        
        self.logger = logger
        
        
        try: 
            self.__log(2, "loading IDs dictionary from path - %s"%os.path.join(self.rootDir, dictFileName))
            self.id2nameDict = pickle.load(open(os.path.join(self.rootDir, dictFileName),'r'))
        except Exception as inst: 
            self.__log(3, "can't load IDs dictionary - %s"%inst)
            self.id2nameDict = None
        
        '''
        try: 
            self.labelsDict = pickle.load(open(os.path.join(self.rootDir, labelsDictFileName),'r'))
        except Exception as inst: 
            self.__log(3, "can't load labels dictionary - %s"%inst)
            self.labelsDict = None
        '''     
 
    def getNetwork(self):
        from itertools import chain
        return list( chain.from_iterable(self.network.values()) )
         
        
    def run(self, size, MIN_INSTANSES = 10, MAX_PVALUE = 0.05, MIN_ZSCORE = 2 ,color = True, dangle = True):
        self.__log(2,"Fanmod Output Handler started.")
        self.__log(1,"Params: [%s]"%str([MAX_PVALUE , MIN_ZSCORE  ,color , dangle] ))
        
        self.__log(2,"Importing network ...")
        self.parseNetwork()
        self.__log(2,"done. %d edges found."%len(self.network))
        
        
        #self.parseNetworkDetails(self.summaryFilePath)
        response = self.parseOutputCSV(size, MAX_PVALUE , MIN_ZSCORE  ,color , dangle )
        if  response > 0:

            self.__log(2,"Parsing csvFile [%s]"% self.motifsFilePath)
            
            self.parseCSV()
            self.__log(2,"done. %d motifs found."%len(self.motifs))
            
            
            self.__log(2,"Parsing dumpFile ...")
            subgraphsCount = self.parseSubgraphs(size)
            self.__log(2,"done. %d instances found."%subgraphsCount)
            
            self.__log(2,"Filtering motifs by count [%d] ..."%MIN_INSTANSES)
            self.__filterByCount(MIN_INSTANSES)
            self.__log(2,"done. %d motifs filtered."%len(self.motifs))
            
            self.__calculateStats()
            
            #self.__log(2,"Dumping data to DB ...")
            #self.dumpDataToTable(subgraphsCount > 0)
            #self.__log(2,"Done.")
            return True
        else:
            return response
        
            
    def __filterByCount(self,minInstances):
        newdict = {}
        for adj in self.motifs:
            if len( self.motifs[adj] ) >= minInstances:
                newdict[adj] = self.motifs[adj]
        self.motifs = newdict
                
    def parseSubgraphs(self,size):
            
        count = 0
        linecount = 0
        mapping = [0,1,2]
        if os.path.isfile(self.dumpFile):
            f = open(self.dumpFile,'r')
            for line in f:
                linecount += 1
                if linecount <= 2: 
                    continue
                line = line.split('\n')[0] 
                split = line.split(',')
                
                
                adj = split[0]
                toadd = split[1:size+1]
                
                #the dump file contains subgraphs of motifs that might have been filtered out by their p-value, z-score etc. in parseOutputCSV()
                if not adj in self.motifs: 
                    continue
                
                
                if self.id2nameDict : 
                    toadd = map(lambda x: self.id2nameDict[x] if x in self.id2nameDict else x, toadd)
                    
                
                ''' 
                Due to a bug in FANMOD, the subgraphs do not appear in the right order as the adjacency matrix.
                __sortInstance returns a list of all legal ordering of the subgraph.
                '''
                _combinations = self.__sortInstance(toadd, self.__getAdjAsMat(adj))
                
                if len(_combinations) == 0:
                    self.__log(3, "Error: can't find a proper order for subgraph: %s, %s"%(str(toadd),str(_combinations))) 
                    toadd = tuple(toadd)
                if len(_combinations) > 0:
                    toadd = _combinations[0]
                if len(_combinations) > 1:
                    self.motifs[adj].containsDuplicates = True
                    
                self.motifs[adj].addInstance(toadd)
                
                count += 1
            self.__log(2,"Filtering duplicates")                
            for motif in self.motifs.values():
                # in symmetrical motifs, the same subgraph could be obtained in several orders
                motif.removeDuplicates()
                
        else: 
            self.__log(3,"dump file was not found at [%s]"%self.dumpFile)                
        return count 
     
    def getSubgraphsCount(self):
        return sum(map( lambda x:len(x.instances), self.motifs.values() )) 
    
    def __sortInstance(self, inst,mat):
        import itertools
        if len(self.network)>0:
            network = self.network
            node2label = self.node2label
            ans = []
            
            for comb in itertools.permutations(inst):
                toadd = True
                for i in range(0,len(mat)):
                    if not toadd: break
                    for j in range(0,len(mat)):
                        if not toadd: break
                        if i!=j and int(mat[i][j])!=0:
                            key = "%s#%s"%(comb[i],comb[j])
                            
                            #if not [comb[i],comb[j],str(mat[i][i]) ,str(mat[j][j]),str(mat[i][j]) ] in network:
                            if not key in network or not ( comb[i], comb[j], str(mat[i][i]), str(mat[j][j]), str(mat[i][j]) ) in network[key]:
                                toadd = False 
                            #else:
                            #    print  [comb[i],comb[j],str(mat[i][i]) ,str(mat[j][j]),str(mat[i][j]) ]                                
                            '''
                            if not (node2label[comb[i]]==int(mat[i][i]) and node2label[comb[j]]==int(mat[j][j]) 
                                    and key in network and int(mat[i][j]) in network[key]): 
                                toadd = False    
                            '''

                
                if toadd:
                    ans.append(comb)
              
            return ans
        return False
     

    def __getAdjAsMat(self,adj):
        size = int( math.sqrt(len(adj)) )
        mat = []
        for i in range(0,size):
            arr = []
            for j in range(0,size):
                arr.append(adj[i*size+j])
            mat.append(arr)
            
        return mat
        
            
    def parseNetworkDetails(self,ifile):
        """
        reading network details from csv file
        """
        keys = {"type":1,
                "nodes":2,
                "edges":3,
                "node_colors":4,
                "edge_colors":5,
                "size":6}
    
        f = open(ifile,'r')
        buf = f.readline()
        while len(buf)>0:
            for key in keys:
                ind = buf.find(key)
                if ind >= 0: 
                    if keys[key]==1: self.type = (buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==2: self.nodes = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==3: self.edges = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==4: self.node_colors = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==5: self.edge_colors = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==6: self.size = int(buf[ind+len(key)+1:].split("\n")[0].strip())       
            buf = f.readline()
        f.close()
          
    def parseOutputCSV(self,size,MAX_PVALUE , MIN_ZSCORE  ,color , dangle ):
        """
        @param MAX_PVALUE: a floating point. specifies the maximum pvalue of the output motifs images.
        @param MIN_FREQ: a floating point. specifies the minimum frequency of the output motifs images.
        @param MIN_ZSCORE: a floating point. specifies the minimum zscore of the output motifs images.
        @param color: boolean. True - to have only motifs with more then 1 color.
        @param dangle: Integer. specifies the maximum number of dangling edges in the output motifs images.
        """
        if os.path.isfile(self.csvFile):
            csvParser = CSVParser(self.csvFile,size)
            found, processed = csvParser.parse(self.motifsFilePath, MAX_PVALUE, MIN_ZSCORE ,color, dangle )
            if processed == 0:
                self.__log(4, "FANMOD results file is corrupted! FANDMO run was interrupted. ")
                return -5
            if processed == 1:
                self.__log(4, "0 motif processed! FANMOD did not detect any subgraphs at all. Check your arguments. ")
                return -6
            self.__log(2,"%d motifs found. %d motifs processed. params: %s"% (found,processed, str ([MAX_PVALUE , MIN_ZSCORE  ,color , dangle])))
            #csvParser.parseNetworkDetails(self.summaryFilePath)
            return True
        else:
            self.__log(4, "FANMOD results file was not find! there was a problem in running fanmod. Perhaps an empty network was submitted ???")
            return -4
       
    def parseCSV(self):
        
        if os.path.isfile(self.motifsFilePath):
            f = open(self.motifsFilePath,'r')
            line = f.readline()
            line = f.readline()
            while len(line)>0:
                line = line.split("\n")[0]
                tokens = line.split("\t")
                
                if self.motifs.has_key(tokens[0]): 
                    self.__log(3, "duplicate adjacency matrices. %s"%tokens[0])
                
                self.motifs[tokens[0]] = Motif(tokens[0], tokens[1], tokens[2], tokens[3].replace("%", ""))
                
                line = f.readline() 
        else:
            raise IOError("csv file not found at [%s]"%self.csvFile)
    
    def parseNetwork(self):
        if os.path.isfile(self.networkFile):
            
            f = open(self.networkFile,'r')
            line = f.readline()
            while len(line)>0:
                line = line.split("\n")[0]
                line = line.split("\r")[0]
                edge = line.split("\t")
                int1 = edge[0]
                int2 = edge[1]
                
                if self.id2nameDict: #translate from FANMOD ids to node names 
                    try: 
                        int1 = self.id2nameDict[edge[0]]
                        int2 = self.id2nameDict[edge[1]]
                    except Exception as inst: 
                        self.__log(3,"error - %s"%inst)
                    
                key = "%s#%s"%(int1,int2)
                if not key in self.network:
                    self.network[key] = set()
                self.network[key].add( (int1,int2,edge[2],edge[3],edge[4]) )
                
                #self.network.append([int1,int2]+edge[2:])
                
                
                #print "edge:" + str ([int1,int2]+edge[2:])
                '''
                
                self.network[key].add(int(edge[4]))
                
                if not int1 in self.node2label: 
                    self.node2label[int1]=int(edge[2])
                elif self.node2label[int1]!=int(edge[2]):
                    raise Exception("duplicate node labeling for node '%s'. labels: [%s] , [%s]"%(int1,self.node2label[int1],int(edge[2])))
                if not int2 in self.node2label: 
                    self.node2label[int2]=int(edge[3])
                elif self.node2label[int2]!=int(edge[3]):
                    raise Exception("duplicate node labeling for node '%s'. labels: [%s] , [%s]"%(int2,self.node2label[int2],int(edge[3])))
                '''
                line = f.readline()
         
            return True
        else: 
            self.__log(3,"network file not found at [%s]"%self.networkFile)
            return False
        
        
    def __calculateStats(self):
        for motif in self.motifs.values():
            motif.calculateStats()
            
    def setLogger(self,logger):
        self.logger = logger
    def __log(self,level ,msg):
        if self.logger:
            self.logger.log(level,msg)
        else:
            print msg

    '''                  
    def __validateInput(self,MAX_PVALUE ,MIN_ZSCORE,color, dangle):    
        try: 
            float(MAX_PVALUE)
            float(MIN_ZSCORE)
            bool(color)
            int(dangle)
            return True
        except: 
            self.__log(5,"bad input!")
            return False
                     
    def __filterParams(self,graph, split, dangle,MAX_PVALUE,MIN_ZSCORE, color):
        if not self.__isDangled(graph, dangle):  return False
        try:
            if float(split[6])>MAX_PVALUE or float(split[5])<MIN_ZSCORE: 
                return False
        except: return False
        if color and not self.__isColoured(graph): return False
        return True
        
    def __isDangled(self,G,dangling):
        count = 0
        for n in G.nodes(data=False) :
            if len(set(G.successors(n))|set(G.predecessors(n))) == 1: count += 1
            if len(set(G.successors(n))|set(G.predecessors(n))) == 0: print "zero"
        if count <= dangling:return True
        return False
    def __isColoured(self,G):
        colors = self.__getColorsFromGraph(G)
        if len(colors)>1:return True
        return False
    
    def __getColorsFromGraph(self,G):
        colors = set()
        edges = G.edges(data=True)
        for e in edges:
            colors.add(e[2]['color'])
        return colors
    '''
    
if __name__=="__main__":
    import datetime
    rootDir = "/home/skuper/workspace/MotifNetNew/Data/2016-04-20_12:05:13.091452-onlyPHP/" 
    jobName = "test"
    networkFileName = "network.txt"
    csvFileName = "fanmodResults"
    dumpFileName = "fanmodResults.dump"
    dictFileName = "id2name-dict.pkl"
    labelsDictFileName = "nodeLabelsDict.pkl" 
    
    fh = OutputHandler( rootDir, networkFileName, csvFileName, dumpFileName, dictFileName,) 
    
    start = datetime.datetime.now()    
    fh.run(4,0.05,0)
    print datetime.datetime.now() - start
    """
    
    """
   
    
    