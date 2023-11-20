import mimetypes
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from time import  strftime
import pathlib


class CS2610Assn1(BaseHTTPRequestHandler):

    def buildHeaders(self, code, content,f,location):
        print(f"{self.client_address[0]} . . [{strftime('%c')}] \"{self.command} {self.path} {self.request_version} {code}\"")
        ##fortesting purposes
        ##print(self.path+ " CODE: "+code+" CONTENT: "+str(content))
        if f != "" or code.startswith("4"):
            self.send_header("HTTP/1.1", code)
            self.send_header("Server", "Logan's Neat Lil Server")
            self.send_header("Date", strftime("%c"))
            self.send_header("Connection", "close")
            self.send_header("Cache-Control", "max-age=.1")
            if code !="301":
                self.send_header("Content-Type", content)
            if code == "301":
                self.send_header("Location",location)
            elif code == "200" and f != "DEBUG":
                f.seek(0, os.SEEK_END)
                fileLen = f.tell()
                self.send_header("Content-Length",str(fileLen))
                f.seek(0)

            self.end_headers()
            if code.startswith("2") or code.startswith("3"):
                if f != "DEBUG":
                    # Read until EOF into one long bytestring
                    this_is_the_rest_of_the_data_as_bytes = f.read()
                    ##self.wfile.write(b"Server: Logan's Neat Lil Server\n")
                    self.wfile.write(this_is_the_rest_of_the_data_as_bytes)
                    f.close()

    def do_GET(self):

        pathLib = pathlib.Path(self.path[1:])
        code = "301"
        ##file is found and information can be sent though accordingly
        if pathLib.is_file():
            code = "200"
            self.buildHeaders(code,mimetypes.guess_type(self.path[1:])[0],open(self.path[1:],"rb"),"")

        ##attempts to find files
        else:
            ##lowers path name to search for the path and also sets variables
            self.path = self.path.lower()
            ##f is for file
            f = ""
            ##blank location. only should be used for 301 codes
            location = ""
            ##checking for if the path is there and provides a location for it
            if self.path == "/" or self.path == "/index":
                location = "/index.html"
                f = open("index.html", "rb")

            elif self.path == "/plan":
                location = "/plan"
                f = open("plan.html", "rb")

            elif self.path == "/about" or self.path.startswith("/bio"):
                location = "/about.html"
                f = open("about.html", "rb")

            elif self.path == "/techtips+css" or self.path == "/help" or self.path == "/tips":
                location = "/techtips+css.html"
                f = open("techtips+css.html", "rb")

            elif self.path.startswith("/techtips-css"):
                location = "/techtips-css.html"
                f = open("techtips-css.html", "rb")

            ##if a file has not been opened it,

            ##sends headers if code is 301 since no file will be found
            if f != "":
                self.buildHeaders(code,"",f,location)

            ##since all else has failed, now we look into the 400 codes
            else:
                ##418 teapot
                if(self.path == "/teapot"):
                    self.buildHeaders("418","text/html","","")
                    self.wfile.write(b"""<!DOCTYPE html>
                    <html lang="en">
                      <head>
                        <meta charset="UTF-8">
                        <title>Lol teapot</title>
                      </head>
                      <body style = "background-color: grey;">
                        <h1>I'm a little teapot</h1>
                        <p>
                            Lol whatcha doin' there man? here come on back to the <a href = "index.html">Main Page</a>
                        </p>
                      </body>
                    </html>\n""")
                ##403 Forbidden
                elif (self.path == "/forbidden"):
                    self.buildHeaders("403", "text/html", "", "")
                    self.wfile.write(b"""<!DOCTYPE html>
                                    <html lang="en">
                                      <head>
                                        <meta charset="UTF-8">
                                        <title>Forbidden</title>
                                      </head>
                                      <body style = "background-color: wheat;">
                                        <h1>What you are trying to access is forbidden!</h1>
                                        <p>
                                            Woah pal! You just tried to access something you aren't supposed to. Don't make me call the FBI.
                                        </p>
                                        <p>
                                           Shame on you.
                                        </p>
                                      </body>
                                    </html>\n""")
                ##debugging
                elif (self.path == "/debugging"):
                    self.buildHeaders("200","text/html","DEBUG", "")
                    requests = ""
                    for header, value in self.headers.items():
                        requests = requests+"<li>"+header+" "+value+"</li>"
                    debugString = """
                    <!DOCTYPE html>
                    <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                                <title>Debugger</title>
                        </head>
                        <body style = "background-color: orange;">
                            <h1>Welcome to the debugger page!</h1><h3>Heres some info about the server...</h3>
                                <ul><li>server's version: """+self.server_version+"""</li>
                            <li>server's current date and time: """ +strftime("%c")+"""</li>
                            <li>client's IP address and port number: """+self.client_address[0]+" Port:"+str(self.client_address[1])+"""</li>
                        <li>The path requested by the client: """+ self.path+"""</ul>
                            <h3>Here is some HTTP information...</h3>
                                    <ul><li>HTTP request type: """+self.command+""" </li>
                                    <li>HTTP version of this request: """+self.request_version+"""</ul>
                        <ol>"""+str(requests)+"""
                            </ol>
                        </body>
                    </html>\n"""
                    self.wfile.write(bytes(debugString,"UTF-8"))
                ##404 page not found
                else:
                    self.buildHeaders("404","text/html","", "")
                    notfound = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <title>404 Error</title>
                    </head>
                    <body style = "background-color: gold;">
                    <h1>404 page not found!</h1>
                    <p>
                    It appears you tried to visit """+self.path+""" but I can't find it. Sorry about that!  <a href = "index.html">Click here to go back home</a>
                    </p>
                    
                    </body>
                    </html>\n"""

                    self.wfile.write(bytes(notfound,"UTF-8"))





if __name__ == '__main__':
    server_address = ('localhost', 8000)
    print(f"Serving from http://{server_address[0]}:{server_address[1]}")
    print("Press Ctrl-C to quit\n")
    try:
        HTTPServer(server_address, CS2610Assn1).serve_forever()
    except KeyboardInterrupt:
        print(" Exiting")
        exit(0)
