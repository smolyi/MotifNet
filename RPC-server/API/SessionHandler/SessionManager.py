import Session
import SessionsCleaner

class SessionManager:
        def __init__(self,runGarbageCollector = False):
            self.Sessions = {}
            self.sessionCleaner = SessionsCleaner.SessionsCleaner(self)
            
            if runGarbageCollector:
                self.runCleaner()
            
        def getSession(self,sessionID):
            if  sessionID in self.Sessions:
                return self.Sessions[sessionID].getData()
            return False
        
        def newSession(self, sessionID, sessionDATA = None):
            self.Sessions[sessionID] = Session.Session(sessionID,sessionDATA)
        
        def setSessionData(self, sessionID, sessionDATA ):
            if  sessionID in self.Sessions:
                return self.Sessions[sessionID].setData(sessionDATA)
            return False
                
        def isInSessions(self, sessionID):
            return self.Sessions.has_key(sessionID)
            
        def removeSession(self, sessionID):
            if not self.Sessions.has_key(sessionID):
                return False
            else:
                self.Sessions.pop(sessionID)
                return True
        
        def runCleaner(self):
            self.sessionCleaner.start()
        #def stopCleaner(self):
        #    self.sessionCleaner.stop()
            
class SessionManagerSingleton:

    __instance = None

    def __init__(self):

        """ Create singleton instance """
        # Check whether we already have an instance
        if SessionManagerSingleton.__instance is None:
            # Create and remember instance
            print "Creating SessionHandler singleton"
            SessionManagerSingleton.__instance = SessionManager()

        # Store instance reference as the only member in the handle
        self.__dict__['_SessionManagerSingleton__instance'] = SessionManagerSingleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)