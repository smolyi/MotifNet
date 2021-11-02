#!/usr/bin/python

import sys, traceback


try:
    from BasicQueriesCGI import *
    from SimpleJSONRPCServer import CGIJSONRPCRequestHandler

    handler = CGIJSONRPCRequestHandler()
    handler.register_instance(BasicQueriesCGI())
    handler.register_introspection_functions()
    handler.handle_request()
except:
    print "content-type:text/html \n\n"
    traceback.print_exc(file=sys.stdout)
