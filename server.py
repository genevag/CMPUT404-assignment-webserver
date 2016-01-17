#  coding: utf-8 
import SocketServer
import mimetypes
import urllib2
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


'''
----- PROBLEM -----
127.0.0.1:8080/deep   doesn't render the css b/c it gets /deep.css instead of /deep/deep.css
'''

class MyWebServer(SocketServer.BaseRequestHandler):
    
    def handle(self):
        print '\n --------------------------------', '\n'
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        requestType, urlEndpoint, other = self.data.split(' ', 2)
        print 'requestType : ' + requestType
        print 'urlEndpoint : ' + urlEndpoint, '\n'

        # normalize file path : changes "/www/deep/../base.css" to "/www/base.css"
        print "Input Path : " + os.getcwd() + '/www' + urlEndpoint
        path = os.path.normpath(os.getcwd() +  '/www' + urlEndpoint)
        print "Normalized Path : " + path + '\n'



        # ------------------------------------------- #
        # ----- Validate directory to restricted access only ----- #
        # forbidden - restrict access to www directory only and not higher directories
        if (path != os.getcwd() + '/www') and (os.getcwd() + '/www/' not in path):
            self.request.send("HTTP/1.1 403\r\n")
            return
        # ------------------------------------------- #



        # ------------------------------------------- #
        # ------ Here, access is allowed ------ #


        # --- Valid/Existing Path & Valid/Existing File --- #
        # ----- Validate path & file & send 200 response ----- #
        if os.path.exists(path) and os.path.isfile(path):
            page = urllib2.urlopen('file://' + path)
            self.request.send('HTTP/1.1 200 OK\r\n')
            self.request.send(str(page.headers) + '\r\n\r\n')
            self.request.send(page.read())
        # ------------------------------------------- #



        # --- In the allowed "/www" directory & path is a directory, not a file --- #
        # ----- path is '/' or '/deep' --> redirect to index.html file for that directory ----- #
        elif os.path.exists(path) and os.path.isdir(path):
            newUrlEndpoint = os.path.normpath(urlEndpoint + '/index.html')
            newPath = os.path.normpath(os.getcwd() +  '/www/' + newUrlEndpoint)

            print "newUrlEndpoint : " + newUrlEndpoint
            print "newPath : " + newPath

            # self.request.send('HTTP/1.1 301 Moved Permanently\r\n')
            # self.request.send('Location: ' + newUrlEndpoint)

            page = urllib2.urlopen('file://' + newPath)
            self.request.send('HTTP/1.1 200 OK\r\n')
            self.request.send(str(page.headers) + '\r\n\r\n')
            self.request.send(page.read())
        # ------------------------------------------- #



        # ----- Bad path or non-existing file, send 404 response ---- #
        else:
            self.request.send("HTTP/1.1 404\r\n")
        # ------------------------------------------- #




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

    print 'Serving on : ' + str(HOST) + ":" + str(PORT)