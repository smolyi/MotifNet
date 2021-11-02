'''
Created on Apr 1, 2012

@author: skuper
'''

import os

#EXECUTION_FILE_PATH = "/home/skuper/workspace/Fanmod/FANMOD-command_line-source/executables/fanmod_command_line_linux"
EXECUTION_FILE_PATH = "/media/disk3/users/motifnet/MotifNetRemote/fanmod_command_line_linux" 
class FanmodRunner(object):
    '''
    Executes fanmod from command line.
    '''


    def __init__(self, inputGraphFilePath):
        '''
        Constructor
        '''
        #input
        self.inputGraphFilePath = inputGraphFilePath
        if not os.path.isfile(self.inputGraphFilePath):
            raise Exception("[%s], input file not found."%self.inputGraphFilePath)


    def runFanmod(self, outputFilePath,
                outputFileFormat = "csv",
                coloredVertices = True,
                coloredEdges = True,
                directed = True,
                dumpFile = True,


                #algorithm configurations
                sizeOfMotifs = 3,
                numberOfSubgraphs = 3,
                fullEnumeration = True,
                samplingProbabilities = [],
                #Randomization configurations
                numberOfRandmoNetworks = 10,
                reestimateSubgraphsNumber = True,
                exchangesPerEdges = 3,
                exchangeAttemptsPerEdge = 3,
                randomType = 0,
                regardVerticesColors = True,
                regardEdgesColors = True,
                executionFilePath = EXECUTION_FILE_PATH):
        print outputFilePath
        print (sizeOfMotifs,
         numberOfSubgraphs,
         fullEnumeration,
         self.inputGraphFilePath,
         directed,
         coloredVertices,
         coloredEdges,
         randomType,
         regardVerticesColors,
         regardEdgesColors,
         reestimateSubgraphsNumber,
         numberOfRandmoNetworks,
         exchangesPerEdges,
         exchangeAttemptsPerEdge,
         outputFilePath,
         outputFileFormat,
         dumpFile)
        command = executionFilePath + " %d %d %d %s %d %d %d %d %d %d %d %d %d %d %s %s %d"\
        %(int(sizeOfMotifs),
         int(numberOfSubgraphs),
         int(fullEnumeration),
         self.inputGraphFilePath,
         int(directed),
         int(coloredVertices),
         int(coloredEdges),
         int(randomType),
         int(regardVerticesColors),
         int(regardEdgesColors),
         int(reestimateSubgraphsNumber),
         int(numberOfRandmoNetworks),
         int(exchangesPerEdges),
         int(exchangeAttemptsPerEdge),
         outputFilePath,
         outputFileFormat,
         int(dumpFile) )
        
        if not fullEnumeration:
            for item in samplingProbabilities:
                command += " " + str(item)
        
        print command
        print os.system(command)

if __name__=="__main__":
    f = FanmodRunner(inputGraphFilePath = "/home/skuper/workspace/phosphoProject/src/Fanmod/graphs/mrna-php_pos-php_neg-tf.txt")
    f.runFanmod("motifs")
