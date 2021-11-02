import sys,os
sys.path.append("../Includes")

LISTENER_IP = "127.0.0.1" #"132.72.216.162"
LISTENER_PORT = 32004

root = "/media/disk2/users/motifnet/Websites/Product/RPC-Server/"
PID_FILE_PATH = root+"Data/pid.txt" #/home/skuper/workspace/MotifNetServer/cgi-bin/Data/pid.txt"
STDOUT_FILE_PATH = root+"Data/stdout.txt" #"/home/skuper/workspace/MotifNetServer/cgi-bin/Data/stdout.txt"
STDERR_FILE_PATH = root+"Data/stderr.txt" #"/home/skuper/workspace/MotifNetServer/cgi-bin/Data/stderr.txt"
LOG_FILE_PATH = root+"Data/main.log"
DB_LOG_FILE_PATH = root+"Data/db.log"

#SESSIONS_DIR = "/home/skuper/workspace/MorifNetNew/cgi-bin/Sessions"

#DESCRIPTION_FILE = "/home/skuper/workspace/MotifNetServer/EnsgDescription.tsv"	
