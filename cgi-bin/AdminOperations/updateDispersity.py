import MySQLdb, math
  
def getSizeFromAdj(self,string):
    root = math.sqrt(len(string))
    if root == int(root): 
        return int(root)
    return -1

def calculateStats(size,instances):
    print "number of instances: ", len(instances)
    dispersity = -1
    minDispersity = 1
    maxDispersity = -1
    
    allgenes = set()
    for i in range(size):
        genesInPosI = set(map(lambda x:x[i], instances))
        tdispersity = float( len(genesInPosI) ) / len(instances)
        print len(genesInPosI), tdispersity
        if tdispersity > maxDispersity:
            maxDispersity = tdispersity
        if tdispersity < minDispersity:
            minDispersity = tdispersity
        
        allgenes = allgenes | genesInPosI
    dispersity = float( len(allgenes) ) / ( len(instances) * size )
    return dispersity, minDispersity, maxDispersity

def update(jobId):
    qry = "SELECT * FROM Subgraphs WHERE jobId='%s' "%(jobID)
    cursor.execute(qry)
    res = cursor.fetchall()
    for adj in set(map(lambda x:x[2], res )):
        print adj
        dispersity, minDispersity, maxDispersity = calculateStats(3, map(lambda x: x[4:], filter (lambda x: x[2]==adj,res)) )
        qry = "UPDATE Motifs SET dispersity='%f',  minDispersity='%f', maxDispersity='%f' WHERE jobId='%s' and adj='%s';"%(dispersity,minDispersity,maxDispersity, jobID, adj)
        print qry
        print cursor.execute(qry)
    #print con.commit()
                
   


jobID = -1      
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='update count.')
    parser.add_argument( 'id',type=int, help='job id.')
    args = parser.parse_args()
    #print args
    
    jobID = args.id
   
    
con = MySQLdb.connect(host = "localhost",user = "motifnet", passwd = "bgu2010", db = "motifNet", port = 33306)
con.autocommit(True)
cursor = con.cursor()
print con, cursor

if jobID >=0:
    update(jobID)
    
