
class MotifNetSession:
    def __init__(self,ID,name,email,size,MotifCount,SubgraphsCount, nodes,edges,node_colors,edge_colors,
                  timeStamp,userid, directory = "-", comments = "-",
                  nodefiles = "", edgefiles = "", arguments = "---", status = -1):
        self.id = ID
        self.name = name
        self.email = email
        self.size = size
        self.count = MotifCount
        self.subgraphsCount = 0
        if SubgraphsCount:
            self.subgraphsCount = int( SubgraphsCount )
        self.nodes = nodes
        self.edges = edges
        self.node_colors = node_colors
        self.edge_colors = edge_colors
        self.time = str(timeStamp) 
        self.user = userid
        self.directory = directory
        self.comments = comments
        self.nodefiles = nodefiles
        if not self.nodefiles:
            self.nodefiles = ""
        self.edgefiles = edgefiles
        if not self.edgefiles:
            self.edgefiles = ""
        self.arguments = arguments
        self.status = status
        self.motifs = {}
        
    def dict(self):
        return {
        'id':self.id ,
        'name':self.name ,
        'email':self.email ,
        'size':self.size ,
        'count':self.count  ,
        'subgraphsCount':self.subgraphsCount  ,
        'nodes':self.nodes ,
        'edges':self.edges ,
        'node_colors':self.node_colors  ,
        'edge_colors':self.edge_colors  ,
        'time':str(self.time)  ,
        'user':self.user ,
        'directory':self.directory  ,
        'comments':self.comments 
         }