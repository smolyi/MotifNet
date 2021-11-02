import time


class Session:
    """
    a simple Session object that stores session data
    """
    def __init__(self,sessionid,sessionData = None):
        self.sessionID = sessionid
        
        self.__Data = sessionData
        self.__lastUsed = time.time() 
    
    def getData(self):
        self.__updateTime()
        return self.__Data
    
    def setData(self,DataObject):
        self.__updateTime()
        self.__Data = DataObject
    
    def lastUsed(self):
        return self.__lastUsed
    
    def __updateTime(self):
        self.__lastUsed = time.time()
