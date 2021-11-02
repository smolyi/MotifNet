import initConfigurations
import os

if os.path.isfile(initConfigurations.PID_FILE_PATH):
    f = open(initConfigurations.PID_FILE_PATH)
    pid = int(f.readline())
    f.close()
    os.system("kill %d"%pid)
    os.remove(initConfigurations.PID_FILE_PATH)
else:
    print "pid file not found"