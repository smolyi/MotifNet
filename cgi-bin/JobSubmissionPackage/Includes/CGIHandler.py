import os.path, sys, cgi
from conf import Conf 

class CGIHandler: 

    def __init__(self, logger = None):
        """
        class handles and process the form's files-input, copy the files to the user's directory.
        
        Parameters
        ---------
            
            filesDict: dictionary. 
                keys = string. name of the file input object in the form.
                values = string. name of the file that will be dumped.
        """
        self.logger = logger
        self.form = cgi.FieldStorage()
        
        self.__logForm(logger)   
        
        self.__getArguments()     
        self.errors = []
        
        

    def getEdgeFiles(self,targetDir):
        return self.__getFiles(targetDir,self.__createEdgesFileDict())
    def getNodeFiles(self,targetDir):
        return self.__getFiles(targetDir,self.__createNodesFileDict())
        
    def getFanmodOutputFiles(self,targetDir):
        return self.__getFiles(targetDir,self.__createOutputFormFilesDict())
    
    def __getFiles(self,targetDir,filesDict):
        filenames = []
        errors = []
        
        keys = filesDict.keys()
        keys.sort()
        for name in keys:
            try:
                filename = self.__save_uploaded_file(targetDir,name, filesDict[name])
                if filename:
                    filenames.append(filename)
                else :
                    errors.append((name,filesDict[name]))   
            except Exception as inst:
                self.logger.log(3, "[%s] is missing. Error: %s"%(name,inst))
        
        #if len(errors)>0:
        #    print "the following files were missing: %s"%errors
        return filenames
        
    def __validateEmail(self,email):
        import re
        if re.search("([^@|\s]+@[^@]+\.[^@|\s]+)",email):
            return email
        return "None"

    def __getArguments(self):
        self.user = self.form.getfirst("user")
        self.jobName = self.form.getfirst("job")
        self.email = self.__validateEmail( self.form.getfirst("email") )
        
        
        self.comments = self.form.getfirst("comments","No comments submitted")
        self.maxPvalue = float( self.form.getfirst("maxPvalue"))
        self.minOccurrences = int( self.form.getfirst("minOccurrences") )
        self.minZscore = float( self.form.getfirst("minZscore",0) )
        self.sizeOfMotif = int( self.form.getfirst("sizeOfMotif") )
        
        self.samplesForApproximation = int( self.form.getfirst("samples",10) )
        self.randomNetworks = int( self.form.getfirst("randomizedNetworks") )
        self.randomizationType = {'No regards':0,'Non-stringent':1,'Stringent':2}[self.form.getfirst("randomization")]
        self.regardEdgeColors = self.form.getfirst("edgeColors") == 'false'
        self.regardNodeColors = self.form.getfirst("vertexColors") == 'false'
        self.reestimateSubgraphNumber = self.form.getfirst("reestimate",'false') == 'true'
        self.edgeSwitch =  int( self.form.getfirst("exchangesPerEdge") )
        self.edgeSwitchAttempt = int( self.form.getfirst("exchangeAttemptsPerEdge") )
        self.fullEnumeration = self.form.getfirst("enumeration") == 'Exact' or self.form.getfirst("enumeration") == 'exact'
        
        self.avoidDanglingEdges = self.form.getfirst("dangle",0) == 'true'
        
        self.onlyColored = 0
        #if "on" == self.form.getfirst("onlyColored", "off"):
        #    self.onlyColored = 1

        self.edgesDirection =  [
                           self.form.getfirst("edgeFile1_directed","off")!="true",
                           self.form.getfirst("edgeFile2_directed","off")!="true",
                           self.form.getfirst("edgeFile3_directed","off")!="true",
                           self.form.getfirst("edgeFile4_directed","off")!="true",
                           self.form.getfirst("edgeFile5_directed","off")!="true",
                           self.form.getfirst("edgeFile6_directed","off")!="true",
                           self.form.getfirst("edgeFile7_directed","off")!="true",
                           self.form.getfirst("edgeFile8_directed","off")!="true"
                           ]
        
        self.nodeLabels =  [self.form.getfirst("nodeFile1_label",None),
                       self.form.getfirst("nodeFile2_label",None),
                       self.form.getfirst("nodeFile3_label",None),
                       self.form.getfirst("nodeFile4_label",None),
                       self.form.getfirst("nodeFile5_label",None),
                       self.form.getfirst("nodeFile6_label",None),
                       self.form.getfirst("nodeFile7_label",None),
                       self.form.getfirst("nodeFile8_label",None)]
        
        self.samplingProbabilities = []
        for i in range(int(self.sizeOfMotif) ):
            self.samplingProbabilities.append(self.form.getfirst("sample"+str(i+1),None))
                       
        
    def __save_uploaded_file (self,rootDIR, form_field,target):
        '''
        saving file from the form
        ''' 
        if not self.form.has_key(form_field):
            raise Exception("Form field is missing. %s"%form_field)        

        fileitem = self.form[form_field]
        
        if not fileitem.file or fileitem.value =="": #fileitem is empty (input field was not filled in)
            return False
        
        path = ""
        for item in target.split("/"):
            path = os.path.join(path,item)
                           
        fout = file (os.path.join(rootDIR,path), 'w')
        while 1:
            chunk = fileitem.file.read(100000)
            if not chunk: break
            fout.write (chunk)
        fout.close()
        return fileitem.filename
        
    def __createEdgesFileDict(self, NUMBER_OF_EDGE_FILES = 7):
        filesDict = {}
        for i in range (1,NUMBER_OF_EDGE_FILES+1):
            filesDict["edgeFile%d"%i] = "/%s/edgeFile%d.txt"%(Conf.EdgesFilesDir,i)
        return filesDict
    
    def __createNodesFileDict(self,NUMBER_OF_NODE_FILES = 7):
        filesDict = {}
        for i in range (1,NUMBER_OF_NODE_FILES+1):
            filesDict["nodeFile%d"%i] = "/%s/nodeFile%d.txt"%(Conf.NodesFilesDir,i)
        return filesDict

    def __createOutputFormFilesDict(self):
        filesDict = {
                     "networkFile": Conf.txt_file,
                     "csvFile": Conf.csv_file,
                     "dumpFile": Conf.dump_file,
                     "nodesMappingFile": Conf.dict_file,
                     "labelsDict": Conf.labelsDict_file
                     }
        return filesDict

    def __logForm(self, logger):
        #self.logger.log(1,str(self.form))
        for item in self.form:
            if not "File" in item or "directed" in item:
                msg = "%s: %s"%( item, self.form.getfirst(item, "undefined"))
            if "edgeFile" in item and not "directed" in item:
                msg = "%s: %s"%( item, self.form[item].filename)
            if logger:
                    logger.log(1,msg )
            else:
                print msg  
                
            
                