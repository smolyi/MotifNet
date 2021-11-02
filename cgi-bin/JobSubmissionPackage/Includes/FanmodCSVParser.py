import os,sys,pickle

class Motif:
    def __init__(self,adj,pvalue,zscore,frequency):
        self.adj = str(adj)
        self.size = self.getSizeFromAdj(adj) #number of vertices
        self.pval = float(pvalue)
        self.zscore = float(zscore)
        self.freq = float(frequency)
        self.edge_colors,self.node_colors = self.getColorsFromAdj(adj)
        
    def getColorsFromAdj(self,adj):
        edges = set()
        nodes = []
        for i in range(1,self.size+1):
            row = adj[(i-1)*self.size:i*self.size]
            for j in range(1,self.size+1):
                if i!=j:edges.add(int(row[j-1]))
                if i==j:nodes.append(int(row[j-1]))
        return edges,nodes  
          
    def getSizeFromAdj(self,string):
        size = len(string)
        for i in range(3,8):
            if size == i*i : return i
        return -1
    
class CSVParser:
    """
    parse fanmod csv output file. 
    """
    def __init__(self,csvFilePath, sizeOfMotif):
        self.size = sizeOfMotif
        self.csvFilePath = csvFilePath
        self.motifs = {}
        if not os.path.isfile(self.csvFilePath):
            print "csv file not found! - [%s]"%self.csvFilePath

        
    def parse(self, summaryFilePath, MAX_PVALUE = 0.05, MIN_ZSCORE = 2 ,color = True, dangle = True):
        """
        @param MAX_PVALUE: a floating point. specifies the maximum pvalue of the output motifs images.
        @param MIN_FREQ: a floating point. specifies the minimum frequency of the output motifs images.
        @param MIN_ZSCORE: a floating point. specifies the minimum zscore of the output motifs images.
        @param color: boolean. True - to have only motifs with more then 1 color.
        @param dangle: boolean. specifies the to avoid dangling edges in the output motifs images.
        """
        proccessed = 0
        
        f = open(self.csvFilePath,'r')
        line = f.readline()
        while len(line)>0:
            split = []
            split.append( line.split(","))            
            if len(split[0])>=7: #motif found
                proccessed += 1
                for j in range (1,self.size):
                    line = f.readline()
                    line = line.split("\n")[0]
                    split.append( line.split(",")) 
            
                if len(split[1])==2 and len(split[2])==2 : #verifying its a motif
                    adj = ""
                    rows = []
                    for string in split: 
                        adj += string[1]
                        rows.append(string[1])
                    
                  
                   
                                    
                    if self.__filterParams(rows,split[0],dangle,MAX_PVALUE,MIN_ZSCORE,color):
                        if self.motifs.has_key(adj): print "duplicate adjacency matrices. %s"%adj
                        self.motifs[adj] = Motif(adj, split[0][6], split[0][5], split[0][2].replace("%", ""))
            line = f.readline() 
        self.__dumpSummary(summaryFilePath)
        return len(self.motifs), proccessed
        
        
    def parseNetworkDetails(self,targetFilePath):
        """
        reading network details from csv file to [targetFilePath]
        """
        keys = {"Network type":1,
                "Number of nodes":2,
                "Number of edges":3,
                "Number of vertex colors":4,
                "Number of edge colors":5,
                "Subgraph size":6}
        
        networkType = "-"
        nodes = 0
        edges = 0
        node_colors = 0
        edge_colors = 0
        size = 0
        
        f = open(self.csvFilePath,'r')
        buf = f.readline()
        while len(buf)>0:
            for key in keys:
                ind = buf.find(key)
                if ind >= 0: 
                    if keys[key]==1: networkType = (buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==2: nodes = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==3: edges = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==4: node_colors = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==5: edge_colors = int(buf[ind+len(key)+1:].split("\n")[0].strip())
                    elif keys[key]==6: size = int(buf[ind+len(key)+1:].split("\n")[0].strip())       
            buf = f.readline()
        f.close()
        f = open(targetFilePath,'w')
        f.write("type=%s\n"%networkType)
        f.write("nodes=%s\n"%nodes)
        f.write("edges=%s\n"%edges)
        f.write("node_colors=%s\n"%node_colors)
        f.write("edge_colors=%s\n"%edge_colors)
        f.write("size=%s\n"%size)
        f.close()
        
    def __dumpSummary(self, filePath):
        f = open(filePath,'w')
        f.write("adj\tpvalue\tzscore\tfrequency\n")
        for motif in self.motifs.values():
            f.write("%s\t%f\t%f\t%f\r\n"%(motif.adj,motif.pval,motif.zscore,motif.freq))   
    
    def __filterParams(self,rowsList, split, dangle,MAX_PVALUE,MIN_ZSCORE, color):
        ans = True
        if dangle or dangle == 0:
            
            ans = ans and self.__isDangled(rowsList, 0)

        if float(split[6])>MAX_PVALUE or float(split[5])<MIN_ZSCORE: 
            ans = ans and False
        
        if color and not self.__isColoured(rowsList): ans = ans and False
        return ans
    
    def __isDangled(self,rowsList,dangling):
        count = 0
        for i in range(0,len(rowsList)):
            neighbors = 0
            for j in range(0,len(rowsList)):
                if i!=j and (rowsList[i][j]!='0' or rowsList[j][i]!='0'):
                    neighbors += 1
            if neighbors < 2:
                count += 1
        
        if count <= dangling:
            return True
        #else:
        #    print rowsList
        return False
     
    def __isColoured(self,rowsList):
        colors = set()
        for i in range(0,len(rowsList)):
            for j in range (0,len(rowsList[i])):
                if i!=j:
                    colors.add(rowsList[i][j])
                    
        if len(colors)>1:return True
        return False
    
    def __con2string(self,con):
        string = ""
        for item in con:
            string += str(item)+","
        return string.strip(",")
    
if __name__=="__main__":
    #parser = CSVParser("/home/skuper/workspace/MotifNetServer/cgi-bin/Data/ppi_php_tf_mrna.txt.csv")
    #parser.parseCSV( summaryFilePath = "/home/skuper/workspace/MotifNetServer/cgi-bin/Data/motifs.csv" ,MAX_PVALUE=0.1,MIN_ZSCORE=0,color=False,dangle=2  )
    #parser.parseNetworkDetails("/home/skuper/workspace/MotifNetServer/cgi-bin/Data/summary.txt")
    parser = CSVParser("/home/skuper/workspace/MotifNetNew/Data/2016-04-20_12:05:13.091452-onlyPHP/fanmodResults",4)
    print parser.parse( summaryFilePath = "/home/skuper/workspace/MotifNetNew/Data/2016-04-20_12:05:13.091452-onlyPHP/summary.txt" ,MAX_PVALUE=0.05,MIN_ZSCORE=0,color=False,dangle=0  )
    