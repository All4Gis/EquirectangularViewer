import SimpleHTTPServer
import SocketServer
import os
from qgis.core import *
import threading
import time

from PyQt4.QtCore import *

from EquirectangularViewer import config


try:
    import sys
    from pydevd import *
except:
    None
    
server = None

def openWebApp(folder):
    SocketServer.TCPServer.allow_reuse_address = True
    global server
    if server is None:
        os.chdir(folder) 
        server = SocketServer.TCPServer(("", config.PORT), SimpleHTTPServer.SimpleHTTPRequestHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

def shutdown():
    global server
    if server:
        server.shutdown()
        server = None
