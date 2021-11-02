import os.path
class Conf:
    #__db connection
    host = "netbio.bgu.ac.il"
    port = 33306
    user = "motifnet"
    password = "bgu2010"#"kOri1234"
    db = "motifNet"

    #__db
    usersTable = "users"
    sessionsTable = "Sessions"
    motifsTable = "Motifs"
    motifsColorsTable = "MotifsColors"
    subgraphsTable = "Subgraphs"
    networkTable = "Networks"

    #server
    root_path = "/media/disk2/users/motifnet/Websites/Product/RPC-Server"
    project_dir = "MotifNet"
    Sessions_dir = os.path.join(root_path,"Sessions")
    LogsDir = os.path.join(root_path,"Data")
    LogFilePath = os.path.join(LogsDir,"main.log")
    errorFilePath = os.path.join(LogsDir,"error.log")
    DAEMON_DIR = "daemon"

    #Sessions
    EdgesFilesDir = "Edges"
    NodesFilesDir = "Nodes"
    motifs_file = "motifs.csv"
    summaryFile = "summmary.txt"
    txt_file = "network.txt"
    csv_file = "output.csv"
    dump_file = "dump.txt"
    dict_file = "dict.pkl"
    labelsDict_file = "labelsDict.pkl"
    LOG_FILENAME = "user.log"
    LOG_LEVEL = 1

    #webpage
    webpageRoot = "/MotifNet"
    localRootPath = "/media/disk2/users/motifnet/Websites/Product/www"
    MotifsImagesDirPath = os.path.join(webpageRoot,"Sessions","Motifs")
    motif_img_dir = os.path.join(localRootPath,"Sessions","Motifs")
    GraphsImagesDirPath = os.path.join(webpageRoot,"Sessions","Graphs")
    GraphsDirLocation = os.path.join(localRootPath,"Sessions","Graphs")

    #cluster communication
    CLUSTER_ABSOLUTE_PATH = "/storage16/users/smolyi/MotifNet/"
    CLUSTER_JOB_CMD_FILE = "submit.py"
    CLUSTER_FO_CMD_FILE = "submitFanmodOutput.py"
    CLUSTER_QSUB_FILE = "runner.csh"
    CLUSTER_FO_QSUB_FILE = "runnerFO.csh"
    CLUSTER_QSUB_EXECUTION = "no"
    CLUSTER_SESSIONS_DIR = "Sessions"
    CLUSTER_HOST = "sge01"
    CLUSTER_USER = "smolyi"
    CLUSTER_PASSWORD = "skupeR26"

    #configurationFile
    configurationFile = "configurations.txt"
    sessionField = "sessionDir"
    jobNameField = "jobName"
    emailField = "email"
    pvalueField = "maxPvalue"
    zscoreField = "minZscore"
    colorField = "color"
    dangleField = "dangle"
    instancesField = "minOccurrences"
    networkFileField = "networkFile"
    csvFileField = "csvFile"
    dumpFileField = "dumpFile"
    dictFileField = "dictFile"
    nodeLabelsFileField = "labelsFile"
    summaryFileField = "summaryFile"
    commentsField = "comments"

    #colors
    colorDict = {}
    colorDict[1] = "black"
    colorDict[2] = "red"
    colorDict[3] = "green"
    colorDict[4] = "yellow"
    colorDict[5] = "blue"
    colorDict[6] = "cyan"
    colorDict[7] = "grey"
    colorDict[8] = "brown"
