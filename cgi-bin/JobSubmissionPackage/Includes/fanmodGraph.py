import pickle,os.path


class Node:
    def __init__(self,ID,color = None):
        self.id = str(ID)
        self.color = color
        
class Edge:
    node1 = None
    node2 = None
    color = 0
    direction = 0
    
    def __init__(self,node1,node2,color = 0,direction = 0,delim = '\t'):
        self.node1 = node1
        self.node2 = node2
        self.color = color
        self.delim = delim
        self.direction = direction
        
    def __str__(self):
        string = self.node1.id+self.delim+self.node2.id
        string += self.delim+str(self.node1.color)
        string += self.delim+str(self.node2.color)
        string += self.delim+str(self.color)
        if self.direction:
            string += "\n"+self.node2.id+self.delim+self.node1.id
            string += self.delim+str(self.node2.color)
            string += self.delim+str(self.node1.color)
            string += self.delim+str(self.color)
        return string
    
    
class FanmodGraph:
    """
    this object creates a fanmod graph, according to Fanmod input standards.
    @param graph_target: string - path of target file where the graph will be dumped.
    @param dict_target: string - path to a location where the dictionaries will be dumped.\
    1) that will translate the ids to their integer labels and colors.
    2) that will translate the integers back to their original ids,
    @param edges: list of strings - each string is a path to an edges file and will be colored differentially, so the color number of the edges in a file correspond to its number .\
    For instance, the edges in the first file will be colored [1]). the files must be tab delimited.
    @param nodes: list of strings - each string is a path to nodes file and will be colored differentially. all the nodes that do not appear in any of the files supplied will be colored in a different color.
    @param reverse: OPTIONAL list of booleans - for each edges file, determine whether the edges (indexes must correspond to @edges) should be bi-directional or not. DEFAULT is false for all edges. 
    """
    
    
    def __init__(self,graph_target,dict_target,edges,nodes,reverse = None):
        """
        
        Parameters
        ----------
        graph_target: string
            path of target file where the graph will be dumped.
        
        @param dict_target: string - path to a location where the dictionaries will be dumped.\
        1) that will translate the ids to their integer labels and colors.
        2) that will translate the integers back to their original ids,
        @param edges: list of strings - each string is a path to an edges file and will be colored differentially, so the color number of the edges in a file correspond to its number .\
        For instance, the edges in the first file will be colored [1]). the files must be tab delimited.
        @param nodes: list of strings - each string is a path to nodes file and will be colored differentially. all the nodes that do not appear in any of the files supplied will be colored in a different color.
        @param reverse: OPTIONAL list of booleans - for each edges file, determine whether the edges (indexes must correspond to @edges) should be bi-directional or not. DEFAULT is false for all edges. 
        """
        self.edges = set()
        self.__createNodeDict(nodes)
        self.max_node = self.getMax()
        self.loadEdges(edges,reverse)
        self.dump(graph_target)
        self.dumpDict(dict_target)
        
        #print "Finished handling graph. Graph was dumped to [%s]."%graph_target
        #print "Dictionaries are dumped to [%s]."%dict_target
    
    def __add(self,node1,node2,color,direct = 0,node_color = False): 
        id1 = self.handleNode(node1)
        id2 = self.handleNode(node2)
        if node_color:
            color1 = id1[1]
            color2 = id2[1]
        else:
            color1 = None
            color2 = None
        n1 = Node(id1[0],color1)
        n2 = Node(id2[0],color2)
        self.edges.add(Edge(n1,n2,color,direct))
        
    def dump(self,fpath):
        f = open(fpath,'w')
        for e in self.edges: f.write(str(e)+"\n")
        f.close()
        
    def dumpDict(self,target):
        pickle.dump(self.translate,  open(target[0],'w'))  
        pickle.dump(self.untranslate, open(target[1],'w'))  
    
    def loadEdges(self,files,reverse,delim = '\t'):
        edge_color = 0
        for file_path in files:
            reversible = False
            if reverse and len(reverse) >= edge_color:
                reversible = reverse[edge_color]  
            edge_color += 1 #must be increased before adding the edge, color can't be 0.
            
            f = open(file_path,'r')
            line = f.readline()
            while len(line)>0:
                line = line.split("\n")[0]
                line = line.split("\r")[0]
                split = line.split(delim) 
                if len(split)>=2:
                    self.__add(split[0], split[1], edge_color,reversible,node_color = True)
                
                line = f.readline()
            f.close()
    
    def __createNodeDict(self,files):
        node2IdLabel = {}
        undict = {}
        count = 1
        color = 0
        for file_path in files:
            f = open(file_path,'r')
            line = f.readline()
            while len(line)>0:
                line = line.split("\n")[0]
                line = line.split("\r")[0]
                line = line.split('\t')[0] #only first token is considered
                node2IdLabel[line] = [str(count),color]
                undict[str(count)] = line
                line = f.readline()
                count +=1
            f.close()
            color += 1

        self.translate =  node2IdLabel
        self.untranslate = undict
    
    def handleNode(self,node):
        if not self.translate.has_key(node):
            ind = str(len(self.translate)+1)
            self.translate[node] = [ind,int(self.max_node)+1]
            self.untranslate[ind] = node    
        return self.translate[node]
    
    def getMax(self):
        if len(self.translate) == 0:
            return -1
        return max(map( lambda x: x[1],self.translate.values() ))
        


if __name__=="__main__":
    root = "/home/skuper/workspace/MotifNetNew/Data/inputSample/"
    graph_target = root + "network.txt"
    dict_target = [root + "dict.pkl",root + "undict.pkl"]
    edges = [root + "PPI.txt",root + "PHP.txt",root + "TR.txt",root + "DE.txt"]
    nodes = [root + "Kinases.txt",root + "Phosphatases.txt"]
    reverse = [True, False, False, False]
    FanmodGraph(graph_target, dict_target, edges, nodes, reverse)
    
    
    