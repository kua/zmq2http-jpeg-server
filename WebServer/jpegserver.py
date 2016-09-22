#! /usr/bin/python

import mimetypes
from twisted.web import server, resource
from twisted.internet import reactor, defer
import threading

from txzmq import ZmqEndpoint, ZmqFactory, ZmqSubConnection

STR404 = '<html><head><title>404 - Not Found</title></head><body><h1>404 - Not Found</h1></body></html>'

class ImageResource(resource.Resource):
    isLeaf = True

    def __init__(self):
        self.deferred = None
        self.fps = 0
        self.timeout()

    def timeout(self):
        print "Fps: %d" % self.fps
        self.fps = 0
        self.timer = threading.Timer(1, self.timeout)
        self.timer.start()

    def cancelTimer(self):
      self.timer.cancel()

    def imageReceived(self, *args):
        data = args[0]
        if self.deferred is not None:
          self.deferred.callback(data)
          self.deferred = None

    def replyImage(self, request, data):
        try:
          contentType, junk = mimetypes.guess_type(request.path)
          request.setHeader('Content-Type', contentType if contentType else 'text/plain')
          request.write(data)
          request.finish()
          self.fps += 1
        except RuntimeError as ex:
          print '\nError:', ex
          self.replyError(request)

    def replyError(self, request):
        request.setResponseCode(404)
        request.write(STR404)
        request.finish()

    def render_GET(self, request):
        try:
          self.processRequest(request)
        except Exception as ex:
          print '\nError:', ex
          self.replyError(request)
        return server.NOT_DONE_YET

    def responseCanceled(self, error):
        self.deferred = None

    def processRequest(self, request):
        request.notifyFinish().addErrback(self.responseCanceled)
        self.deferred = defer.Deferred()
        self.deferred.addCallback(lambda data: self.replyImage(request, data))

class VideoServer:
    def __init__(self, zmq_port):
      server_port = str(8001)
      self.resource = ImageResource()
      self.site = server.Site(self.resource)
      self.zmqFactory = ZmqFactory()
      self.zmqEndpoint = ZmqEndpoint('connect','tcp://127.0.0.1:' + zmq_port)
      self.zmqSubscriber = ZmqSubConnection(self.zmqFactory, self.zmqEndpoint)
      self.zmqSubscriber.subscribe("")
      self.zmqSubscriber.gotMessage = self.resource.imageReceived
      self.resourceEndpoint = reactor.listenTCP(int(server_port), self.site)

    def disconnect(self):
      self.resourceEndpoint.stopListening()
      self.resource.cancelTimer()
