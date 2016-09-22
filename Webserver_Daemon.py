#!/usr/bin/python
# -*- coding: utf-8 -*-

from Daemonizer import common
from Daemonizer import Daemonizer
from WebServer import webserver
from twisted.internet import reactor

class WebServerDaemon(Daemonizer):
  def run(self):
    print('Server Started')
    zmq_port = 5511
    self.webServer = webserver.WebServer(str(zmq_port))
    reactor.addSystemEventTrigger('before', 'shutdown', self.webServer.disconnect)
    reactor.run()

if __name__ == "__main__":
    pid_file = common.PID_FILE_PARENT_DIR + "webserver_daemon.pid"
    cout_log = common.IMITATORS_LOG_PARENT_DIR + 'webserver_daemon_cout'
    cerr_log = common.IMITATORS_LOG_PARENT_DIR + 'webserver_daemon_cerr'
    daemon = WebServerDaemon(pid_file, '/dev/null', cout_log, cerr_log)
    common.process_command(daemon)
