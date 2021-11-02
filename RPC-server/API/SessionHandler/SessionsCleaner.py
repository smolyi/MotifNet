__author__ = 'omer'


import threading
import time

class SessionsCleaner(threading.Thread):
    
    def __init__(self, sessionManager, RUNNING_TIME = 1800, DELETION_THRESHOLD = 3600):
        self.runningTime = RUNNING_TIME
        self.deletionThreshold = DELETION_THRESHOLD
        self.SessionManager = sessionManager
        self._waitevent = threading.Event()
        threading.Thread.__init__(self, name="GarabageCollector")

    def run(self):

        while True:
            self._waitevent.wait(self.runningTime)
            deleteSet = set([])
            for sessionid,sessionInst in self.SessionManager.Sessions.iteritems():
                if time.time()-sessionInst.lastUsed() > self.deletionThreshold:
                    deleteSet.add(sessionid)

            for k in deleteSet:
                self.SessionManager.removeSession(k)

          

