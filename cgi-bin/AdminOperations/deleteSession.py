#!/usr/bin/python


import os, MySQLdb
 
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='delete session and all motifs, subgraphs and edges from the database.')
    parser.add_argument( 'id',type=int, help='job id.')
    parser.add_argument( '--s',dest='session', action='store_true', help='check if you want to remove session from sessions table.')

    args = parser.parse_args()
    print args
    #print args
    
    jobID = args.id
    
    con = MySQLdb.connect(host = "localhost",user = "motifnet", passwd = "bgu2010", db = "motifNet", port = 33306)
    con.autocommit(True)
    cursor = con.cursor()

    print 'fetching motifs ...'
    print  cursor.execute('SELECT adj from Motifs WHERE jobId='+str(jobID)), "motifs found:"
    res = cursor.fetchall()
    print res
    print 
    
    c = 0
    for item in res:    
        c += 1
        adj = item[0]
        qry = "DELETE FROM %s WHERE jobId="+str(jobID)+ " and adj="+ adj
        print 'deleting subgraphs of motif %s (%d of %d) ...'%(adj,c,len(res))
        print cursor.execute(qry%'Subgraphs')
    
    
    qry = "DELETE FROM %s WHERE jobId="+str(jobID)
     
    print 'deleting motifs ...'
    print cursor.execute(qry%'Motifs')
    
    print 'deleting network ...'
    print cursor.execute(qry%'Networks')
    
    if args.session:
        print 'deleting session ...'
        qry = "DELETE FROM %s WHERE id="+str(jobID)
        print cursor.execute(qry%'Sessions')
    

#print os.system("rm -rf %s"% os.path.join(Conf.Sessions_dir,str(jobID)))


