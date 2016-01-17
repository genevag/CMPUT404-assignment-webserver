#  coding: utf-8 
import SocketServer
import mimetypes
import os
from datetime import datetime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#           2016 Geneva Giang
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

    def formulate200Response(self, path):
        file = open(path, "r")
        body = file.read()
        file.close()

        # Get headers
        header = self.httpVersion + " 200 OK\r\n"

        mimetype, encoding = mimetypes.guess_type(path)
        length = os.path.getsize(path)
        lastModifiedTime = os.path.getmtime(path)

        # format taken from : phihag on http://stackoverflow.com/questions/10175134/last-modified-of-file-downloaded-does-not-match-its-http-header  01-16-2016
        formatWanted = "%a, %d %b %Y %H:%M:%S GMT"

        lastModifiedDate = datetime.fromtimestamp(lastModifiedTime).strftime(formatWanted)

        contentType = "Content-type: " + mimetype + '\n'
        contentLength = "Content-length: " + str(length) + '\n'
        lastModified = "Last-modified: " + lastModifiedDate
        header = header + contentType + contentLength + lastModified + "\r\n\r\n"

        response = header + body
        return response

    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        if self.data.find('\n') == -1:
            info = self.data
        else:
            info, others = self.data.split('\n', 1)
        requestType, urlEndpoint, self.httpVersion = info.split(' ', 2)

        # normalize file path : changes "/www/deep/../base.css" to "/www/base.css"
        path = os.path.normpath(os.getcwd() +  '/www' + urlEndpoint)


        # -- Validate directory to restricted access to allowed directory only -- #
        # forbidden - restrict access to www directory only and not higher directories
        if (path != os.getcwd() + '/www') and (os.getcwd() + '/www/' not in path):
            self.request.send(self.httpVersion + " 404 Not Found\r\n")

        # -- Valid/Existing Path & Valid/Existing File -- #
        # ----- Validate path & file & send 200 response ----- #
        elif os.path.exists(path) and os.path.isfile(path):
            response = self.formulate200Response(path)
            self.request.send(response)



        # --- In the allowed "/www" directory & path is a directory, but not a file --- #
        # ----- Validate path & directory & send 301 redirect response ----- #
        # ----- path is '/' or '/deep' --> redirect to index.html file for that directory ----- #
        elif os.path.exists(path) and os.path.isdir(path):
            if urlEndpoint[-1] == '/':
                newUrlEndpoint = os.path.normpath(urlEndpoint + 'index.html')
            else:
                newUrlEndpoint = os.path.normpath(urlEndpoint + '/index.html')

            self.request.send(self.httpVersion + ' 301 Moved Permanently\r\n')
            self.request.send('Location: ' + newUrlEndpoint + '\r\n\r\n')


        # -- Non-existing path or non-existing file, send 404 response -- #
        else:
            self.request.send(self.httpVersion + " 404 Not Found\r\n")




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

    print 'Serving on : ' + str(HOST) + ":" + str(PORT)