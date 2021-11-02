import math     

class Motif:
    def __init__(self,adj,pvalue,zscore,frequency):
        self.adj = str(adj)
        self.size = self.getSizeFromAdj(adj) #number of vertices
        self.pval = float(pvalue)
        self.zscore = float(zscore)
        self.freq = float(frequency)
        self.edge_colors,self.node_colors = self.getColorsFromAdj(adj)
        
        self.dispersity = -1
        self.minDispersity = 1
        self.maxDispersity = -1
        
        self.containsDuplicates = False
        
        self.instances = []
        
    
    def calculateStats(self):
        allgenes = set()
        for i in range(self.size):
            genesInPosI = set(map(lambda x:x[i], self.instances))
            dispersity = float( len(genesInPosI) ) / len(self.instances)
            
            if dispersity > self.maxDispersity:
                self.maxDispersity = dispersity
            if dispersity < self.minDispersity:
                self.minDispersity = dispersity
            
            allgenes = allgenes | genesInPosI
        self.dispersity = float( len(allgenes) ) / ( len(self.instances) * self.size )
        
    def getSizeFromAdj(self,string):
        root = math.sqrt(len(string))
        if root == int(root): return int(root)
        return -1
    
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
    
    def addInstance(self,toadd):
        self.instances.append(toadd)
         
    def removeDuplicates(self):
        s = set(self.instances)
        self.instances = list(s)
               
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
    
    def getAdjAsMat(self):
        mat = []
        for i in range(0,self.size):
            arr = []
            for j in range(0,self.size):
                arr.append(self.adj[i*self.size+j])
            mat.append(arr)
        return mat
    
    def __str__(self): return "%s\t%d\t%f\t%f\t%f"%(self.adj,len(self.instances),self.pval,self.zscore,self.freq)
    def __len__(self):  return len(self.instances)   
    

'''
class Motif:
    def __init__(self,adj,pvalue,zscore,frequency):
        self.adj = str(adj)
        self.size = self.getSizeFromAdj(adj) #number of vertices
        self.pval = float(pvalue)
        self.zscore = float(zscore)
        self.freq = float(frequency)
        self.edge_colors,self.node_colors = self.getColorsFromAdj(adj)
        
        self.instances = []
            
    def getSizeFromAdj(self,string):
        root = math.sqrt(len(string))
        if root == int(root): return int(root)
        return -1
    
    def addInstance(self,toadd):
        self.instances.append(toadd)
         
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
    
    def getAdjAsMat(self):
        mat = []
        for i in range(0,self.size):
            arr = []
            for j in range(0,self.size):
                arr.append(self.adj[i*self.size+j])
            mat.append(arr)
        return mat
    
    def __str__(self): return "%s\t%d\t%f\t%f\t%f"%(self.adj,len(self.instances),self.pval,self.zscore,self.freq)
    def __len__(self):  return len(self.instances)  
'''
class Node:
    def __init__(self,ID,color = None):
        self.id = str(ID)
        self.color = color
        if not self.color:self.color = 0
        
class Edge:
    node1 = None
    node2 = None
    color = 0
    direction = 0
    
    def __init__(self,node1,node2,color = 0,directional = 0,delim = '\t'):
        self.node1 = node1
        self.node2 = node2
        self.color = color
        self.delim = delim
        self.direction = directional
        
    def __str__(self):
        string = self.node1.id+self.delim+self.node2.id
        if self.node1.color: string += self.delim+str(self.node1.color)
        if self.node2.color: string += self.delim+str(self.node2.color)
        string += self.delim+str(self.color)
        if self.direction:
            string += "\n"+self.node2.id+self.delim+self.node1.id
            if self.node2.color: string += self.delim+str(self.node2.color)
            if self.node1.color: string += self.delim+str(self.node1.color)
            string += self.delim+str(self.color)
        return string
    
class Instance:
    def __init__(self,isSorted,nodes):
        self.isSorted = isSorted 
        self.nodes = nodes