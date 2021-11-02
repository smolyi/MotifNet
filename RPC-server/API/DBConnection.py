import MySQLdb
from Logger import Logger

class DBConnection:
    """
    This is a singleton class that would be the interface to the MySQL database.
    It wraps MySQLdb in a simple manner that allows a proper usage of the SQL db without closing connection every time.
    This makes querying faster because the connection remains alive at any time.
    If the connection is lost - it will automatically be renewed.
    It does not handle SQL exceptions !!! you should handle them out side this class.
    
    everytime an exception occur it will try to reconnect and execute query again. 
    if the exception repeat - it will be raised.
    """

    class __impl:
        def __init__(self,host, user, passwrd,port, db, logger = None ):
            self.logger = logger
            self.host = host
            self.user = user
            self.passwrd = passwrd
            self.port = port
            self.db = db
            self.__db = None
            self.__dbc = None
            self.__connect()
                
        def __connect(self):  
            try:    
                self.__db = MySQLdb.connect(self.host,
                                          self.user,
                                          self.passwrd,
                                          self.db,
                                          self.port)
                self.__db.autocommit = False
                self.__dbc = self.__db.cursor()
                self.safelog(2, "Connected to server: %s"%str([self.host,
                                          self.user,
                                          self.passwrd,
                                          self.db,
                                          self.port]))
            except :
                self.safelog(5, "Failed to connect to server")
        def execute(self, query):
            """
            execute a query in the database.

            Parameters
            ----------
                query : string
                    the query to execute.

            """
            try:
                self.safelog(2, "Executing query: %s"%query)
                self.__dbc.execute(query)
            except Exception as inst :
                self.safelog(4, "Failed to execute query: %s"%inst)
                self.reconnect()
                self.__dbc.execute(query)
                
             
        def query(self, query):
            """
            execute a query in the database and fetch response.

            Parameters
            ----------
                query : string
                    the query to execute.

            Return
            ------
                The rows of the table in tuples.
            """
            try:
                self.safelog(2, "Executing query: %s"%query)
                self.__dbc.execute(query)
                rows = self.__dbc.fetchall()
                self.safelog(2, "%d items retrieved. "%len(rows))
                return rows
            except Exception as inst:
                self.safelog(4, "Failed to execute query: %s"%inst)
                self.reconnect()
                self.__dbc.execute(query)
                rows = self.__dbc.fetchall()
                return rows
            
        def reconnect(self):    
            self.__db.close()
            self.__connect()
            
        def close(self):
            self.__db.close()
            
        def safelog(self,level,msg):
            if self.logger: self.logger.log(level,msg)
    __instance = None

    def __init__(self,host, user, passwd,port, db, logger = None ):

        """ Create singleton instance """
        # Check whether we already have an instance
        if DBConnection.__instance is None:
            # Create and remember instance
            print "Creating SQL singleton"
            DBConnection.__instance = DBConnection.__impl(host, user, passwd,port, db,logger)

        # Store instance reference as the only member in the handle
        self.__dict__['_DBConnection__instance'] = DBConnection.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
