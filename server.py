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


class MyWebServer(SocketServer.BaseRequestHandler):
    
    def handle(self):
        print '\n --------------------------------', '\n'
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        requestType, urlEndpoint, other = self.data.split(' ', 2)
        print 'requestType : ' + requestType
        print 'urlEndpoint : ' + urlEndpoint, '\n'

        path = os.path.normpath(os.getcwd() +  '/www' + urlEndpoint)

        if urlEndpoint != '/' and urlEndpoint != '/deep' and urlEndpoint != '/deep/':
            print 'Path : ' + path, '\n'
            # req = open('www' + urlEndpoint, 'r')

            # forbidden - restrict access to www directory only and not higher directories
            if '..' in urlEndpoint:
                self.request.send("HTTP/1.1 403\r\n")
                return

            if os.path.exists(path):
                page = urllib2.urlopen('file://' + path)
            else:
                print 'file path not exists'
                self.request.send("HTTP/1.1 404\r\n")
                return

            self.request.send('HTTP/1.1 200 OK\r\n')
            self.request.send(str(page.headers))
            self.request.send(page.read())

        else:
            path = os.path.normpath(path + '/index.html')
            print 'Path : ' + path, '\n'
            
            page = urllib2.urlopen('file://' + path)
            self.request.send('HTTP/1.1 200 OK\r\n')
            self.request.send(str(page.headers))
            self.request.send(page.read())

        print '\n --------------------------------', '\n'



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

    print 'Serving on : ' + str(HOST) + ":" + str(PORT)