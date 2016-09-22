#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

PID_FILE_PARENT_DIR = "/var/run/"
IMITATORS_LOG_PARENT_DIR = "/tmp/"


def process_command(daemon):
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
