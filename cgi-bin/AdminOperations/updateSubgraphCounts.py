import MySQLdb
  

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
qry = "SELECT * from Motifs"
if jobID>=0:
    qry += " WHERE jobId='%s'"%jobID
print cursor.execute(qry)
motifs = cursor.fetchall()
print len(motifs)
for line in motifs:
    if line[-1]==10:
        qry = "SELECT count(*) FROM Subgraphs WHERE adj=%s and jobId='%s' "%(line[1],line[0])
        cursor.execute(qry)
        count = int(cursor.fetchall()[0][0])
        if count >0:
            qry = "UPDATE Motifs SET count=%d WHERE adj='%s' and jobId='%s';"%(count, line[1], line[0])
            print "updating: ",  line[-1],count, line[1], line[0]
            print qry
            print cursor.execute(qry)
		#print con.commit()
            
	else:
		print line
      
