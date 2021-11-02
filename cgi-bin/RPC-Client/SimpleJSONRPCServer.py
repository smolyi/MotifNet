#!/usr/local/bin/python

from xmlrpclib import Fault
import sys, traceback
import SocketServer
import BaseHTTPServer
import os

import SimpleXMLRPCServer
import json


class SimpleJSONRPCDispatcher(SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    """Mix-in class that dispatches JSON-RPC requests.
    Based on SimpleXMLRPCDispatcher, but overrides
    _marshaled_dispatch for JSON-RPC

    This class is used to register JSON-RPC method handlers
    and then to dispatch them. There should never be any
    reason to instantiate this class directly.
    """
    def _marshaled_dispatch(self, data, dispatch_method = None):
        """Dispatches a JSON-RPC method from marshalled (JSON) data.

        JSON-RPC methods are dispatched from the marshalled (JSON) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleJSONRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the prefered means
        of changing method dispatch behavior.
        """
        rawreq = json.read(data)

        #params, method = xmlrpclib.loads(data)
        id = rawreq.get('id', 0)
        method = rawreq['method']
        params = rawreq.get('params', [])

        responseDict = {'id':id}

        # generate response
        try:
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self._dispatch(method, params)
            ## wrap response in a singleton tuple
            #response = (response,)
            #response = xmlrpclib.dumps(response, methodresponse=1)
            responseDict['result'] = response
        except Fault, fault:
            #response = xmlrpclib.dumps(fault)
            responseDict['error'] = repr(response)
        except:
            # report exception back to server
            #response = xmlrpclib.dumps(
            #    xmlrpclib.Fault(1, "%s:%s" % (sys.exc_type, sys.exc_value))
            #    )
            responseDict['error'] = "%s:%s" % (sys.exc_type, sys.exc_value)

        return json.write(responseDict)


#class SimpleXMLRPCRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
class SimpleJSONRPCRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    
    """Simple JSON-RPC request handler class.


    Handles all HTTP POST requests and attempts to decode them as
    XML-RPC requests.
    """
    def do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as JSON-RPC calls,
        which are forwarded to the server's _dispatch method for handling.
        """
        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            traceback.print_exc(file=sys.stdout)

            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)

class SimpleJSONRPCServer(SocketServer.TCPServer,
                         SimpleJSONRPCDispatcher):
    """Simple JSON-RPC server.

    Simple JSON-RPC server that allows functions and a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch JSON-RPC calls to the functions or instance
    installed in the server. Override the _dispatch method inhereted
    from SimpleJSONRPCDispatcher to change this behavior.
    """
    def __init__(self, addr, requestHandler=SimpleJSONRPCRequestHandler,
                 logRequests=1):
        self.logRequests = logRequests

        SimpleJSONRPCDispatcher.__init__(self)
        SocketServer.TCPServer.__init__(self, addr, requestHandler)

class CGIJSONRPCRequestHandler(SimpleJSONRPCDispatcher):
    """Simple handler for JSON-RPC data passed through CGI."""
    def __init__(self):
        SimpleJSONRPCDispatcher.__init__(self)

    def handle_get(self):
        """Handle a single HTTP GET request.

        Default implementation indicates an error because
        XML-RPC uses the POST method.
        """

        code = 400
        message, explain = \
                 BaseHTTPServer.BaseHTTPRequestHandler.responses[code]

        response = BaseHTTPServer.DEFAULT_ERROR_MESSAGE % \
            {
             'code' : code,
             'message' : message,
             'explain' : explain
            }
        print 'Status: %d %s' % (code, message)
        print 'Content-Type: text/html'
        print 'Content-Length: %d' % len(response)
        print
        sys.stdout.write(response)

    def handle_request(self, request_text = None):
        """Handle a single JSON-RPC request passed through a CGI post method.

        If no JSON data is given then it is read from stdin. The resulting
        JSON-RPC response is printed to stdout along with the correct HTTP
        headers.
        """
        if request_text is None and \
            os.environ.get('REQUEST_METHOD', None) == 'GET':
            self.handle_get()
        else:
            # POST data is normally available through stdin
            if request_text is None:
                request_text = sys.stdin.read()

            self.handle_jsonrpc(request_text)

    def handle_jsonrpc(self, request_text):
        """Handle a single JSON-RPC request"""

        response = self._marshaled_dispatch(request_text)

        print 'Content-Type: text/json'
        print 'Content-Length: %d' % len(response)
        print
        sys.stdout.write(response)






