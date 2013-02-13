# -*- coding: utf-8 -*-
"""
SDM-Aleph server.

@author: Anže Vavpetič, 2011 <anze.vavpetic@ijs.si>
"""
from webServices.serverBase import Server
from webServices.common import cmdlServer

import sdmaleph_service as sdm_aleph

if __name__ == "__main__":
    logFname, port = cmdlServer()

    SERVICE_MODULES = [sdm_aleph]
    SERVICE_LIST = [x.getService(newPort=port) for x in SERVICE_MODULES]
    srv = Server(SERVICE_LIST, logFname, port)
    srv.serveForever()
