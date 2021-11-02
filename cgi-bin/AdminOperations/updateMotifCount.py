import MySQLdb
  
def query(jobId):
    qry = "SELECT count(*) FROM Motifs WHERE jobId='%s' "%(jobID)
    cursor.execute(qry)
    count = int(cursor.fetchall()[0][0])
    if count >0:
        qry = "UPDATE Sessions SET count=%d WHERE id='%s';"%(count, jobID)
        print "updating: ",  jobID,count
        print qry
        print cursor.execute(qry)
    #print con.commit()
                
    else:
        print "count=0"
          


jobID = -1      
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='update count.')
    parser.add_argument( 'id',type=int,default=-1, help='job id.')
    args = parser.parse_args()
    #print args
    
    jobID = args.id
   
    
con = MySQLdb.connect(host = "localhost",user = "motifnet", passwd = "bgu2010", db = "motifNet", port = 33306)
con.autocommit(True)
cursor = con.cursor()
print con, cursor

if jobID >=0:
    query(jobID)
else:
    qry = "SELECT id from Sessions"
    print cursor.execute(qry)
    sessions = map(lambda x:x[0], cursor.fetchall())
    print len(sessions)
    for jobID in sessions:
        query(jobID)
        
