# -*- coding: utf-8 -*-
# The above encoding declaration is required and the file must be saved as UTF-8

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from string import Template
import argparse
import os

import jpegserver

class StatusServer(Resource):

    def loadHtml(self):
      try:
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        filename = '/template.html'
        file = open(self.project_dir+filename, 'r')
        self._template = Template(file.read())
      except IOError:
        print 'Error: template html file %s does not exist and generation impossible' % filename

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        clientIP = str(request.getHost().host)
        return self._template.safe_substitute(host_addr=clientIP)

class WebServer:
    def __init__(self, zmq_port):
      self.imageServer = jpegserver.VideoServer(zmq_port)
      self.root = StatusServer()

      self.root.loadHtml()
      self.factory = Site(self.root)
      self.listeningEndpoint = reactor.listenTCP(8080, self.factory)

    def disconnect(self):
      self.listeningEndpoint.stopListening()
      self.imageServer.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple converter to show received by 0mq images on localhost:8080')
    parser.add_argument('zmq_port', help='zmq_port')

    args = parser.parse_args()

    server = WebServer(args.zmq_port)
    reactor.addSystemEventTrigger('before', 'shutdown', server.disconnect)
    reactor.run()
