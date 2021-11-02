import os.path
class Conf:
    #db connection
    host = "netbio.bgu.ac.il"
    port = 33306
    user = "motifnet"
    password = "bgu2010"
    db = "motifNet"

    # DB tables
    usersTable = "users"
    sessionsTable = "Sessions"
    motifsTable = "Motifs"
    motifsColorsTable = "MotifsColors"
    subgraphsTable = "Subgraphs"
    networkTable = "Networks"

    # server
    RPC_RESTART_CMD = "python /media/disk2/users/motifnet/Websites/Product/RPC-Server/restart.py"
    root_path = "/media/disk2/users/motifnet/Websites/Product/"  #"/home/skuper/workspace/MotifNetNew/" #
    GLOBAL_INCLUDES_PATH = os.path.join(root_path,"Includes")
    #project_dir = "MotifNet"
    Sessions_dir = os.path.join(root_path,"Sessions")
    FANMOD_Sessions_dir = os.path.join(root_path,"RemoteFanmodServer","Sessions")
    LogsDir = os.path.join(root_path,"cgi-bin/Log")
    LogFilePath = os.path.join(LogsDir,"main.log")
    errorFilePath = os.path.join(LogsDir,"error.log")
    DAEMON_DIR_NAME = "daemon"

    #Sessions
    EdgesFilesDir = "Edges"
    NodesFilesDir = "Nodes"
    motifs_file = "motifs.csv"
    summaryFile = "summmary.txt"
    txt_file = "network.txt"
    csv_file = "fanmodResults.csv"
    FanmodOutputFiles = "fanmodResults"
    dump_file = "dumpFile.txt"
    dict_file = "dict.pkl"
    undict_file = "id2name-dict.pkl"
    labelsDict_file = "nodeLabelsDict.pkl"

    LOG_FILENAME = "user.log"
    LOG_LEVEL = 1

    #webpage
    webpageRoot = "/motifnet"
    localRootPath = "/media/disk2/users/motifnet/Websites/Product/www/" #"/var/www/motifnet/" #
   
    #configurationFile
    userNameField = "user"
    inputGraphField = "inputGraph"
    configurationFile = "configurations.txt"
    sessionField = "sessionDir"
    jobNameField = "jobName"
    emailField = "email"
    motifSizeField = "motifSize"
    pvalueField = "maxPvalue"
    zscoreField = "minZscore"
    colorField = "color"
    dangleField = "dangle"
    instancesField = "minOccurrences"
    networkFileField = "networkFile"
    FanmodOutputFilesField = "fanmodOutputFiles"
    csvFileField = "csvFile"
    dumpFileField = "dumpFile"
    dictFileField = "idsDictFile"
    nodeLabelsFileField = "labelsFile"
    summaryFileField = "summaryFile"
    commentsField = "comments"

    SUBGRAPHS_LIMIT = 5000000
