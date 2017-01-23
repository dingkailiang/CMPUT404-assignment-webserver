#  coding: utf-8 
import SocketServer,os.path

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

# a class for generating and managing header for http response
class Header():
    category = ["status","Content-Type"]
    def __init__(self):
        self.content = {}

    def __repr__(self):
        response = "HTTP/1.1 "
        for c in Header.category:
            if c != "status":
                response += c
                response += ": "
            response += self.content[c]
            response += "\r\n"
        response += "\r\n"
        return response

    def __setitem__(self,key,value):
        if key in Header.category:
            self.content[key] = value

class MyWebServer(SocketServer.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        if not self.data:
            return
        print ("Got a request of: %s\n" % self.data)
        
        # set variables
        method,path = self.data.split()[0].upper(),"./www"+self.data.split()[1]
        header = Header()
        header["Content-Type"] = "text/plain"
        body = ""

        # check if the request try to access upper than ./www
        path = simplify(path)
        if not path:
            header["status"] = "404 Not Found"

        # check if the request method is GET
        elif method != "GET":
            header["status"] = "405 Method Not Allowed"

        # check if the request ask for a file
        elif os.path.isfile(path):
            header["status"] = "200 OK"
            header["Content-Type"] = "text/"+path.split(".")[-1]
            fp = open(path)
            body = fp.read()
            fp.close()

        # check if the request ask for a dirctory, return index page if exist
        elif os.path.isdir(path) and os.path.isfile(path+"index.html"):
            header["status"] = "200 OK"
            header["Content-Type"] = "text/html"
            fp = open(path+"index.html")
            body = fp.read()
            fp.close()

        # otherwise, response 404 Not Found error
        else:
            header["status"] = "404 Not Found"

        self.request.sendall(repr(header)+body)

# simplify the path for the case it contains /..
# return false if the final path is upper than ./www
# otherwise return the final path
def simplify(path):
    if path[0:5] != "./www":
        return False
    if "/.." not in path:
        return path
    plist = path.split("/")
    for i in range(len(plist)):
        if plist[i] == "..":
            plist[i] = None
            plist[i-1] = None
            break
    path = ""
    for i in range(len(plist)):
        if plist[i] is not None:
            path += plist[i]
            if i != len(plist[i])-1:
                path += "/"
    return simplify(path)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
