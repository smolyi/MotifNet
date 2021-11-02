#!/usr/bin/env python
"""
The Runner.py script initiates an RPC-server as a Daemon following the configurations that are set in Configurations.py
"""

from Daemon import Daemon
import initConfigurations
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import SocketServer
from Logger import Logger

from API.ServerState import ServerState

class SimpleThreadedXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer):
        pass

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    
class Runner(Daemon):
    def __init__(self):
        Daemon.__init__(self, pidfile=initConfigurations.PID_FILE_PATH, stdout=initConfigurations.STDOUT_FILE_PATH, stderr=initConfigurations.STDERR_FILE_PATH)

    def run(self):
        logger = Logger("server",initConfigurations.LOG_FILE_PATH)
        logger.log(2, "logger created.")
        DBlogger = Logger("DB",initConfigurations.DB_LOG_FILE_PATH)
        # Create server
        server = SimpleThreadedXMLRPCServer((initConfigurations.LISTENER_IP, initConfigurations.LISTENER_PORT),
                                    requestHandler=RequestHandler)
        server.register_introspection_functions()

        #sqlConnection = SQLConnection()
        #exceptionHandler = ExceptionHandler()
        
        logger.log(2, "registering ServerState instance.")
        server.register_instance(ServerState(logger,DBlogger))

        # Run the server's main loop
        logger.log(2, "serving ...")
        server.serve_forever()
       

if __name__ == "__main__":
    runner = Runner()
    runner.start()
