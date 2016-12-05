#!/usr/bin/python

from celery import Celery
from celery.task.control import discard_all
from queuelib import FifoDiskQueue
from config_host import *
import Queue
import datetime
import os
import shelve
import pickle

if __name__ == "__main__":
  #discard_all()
  print "init called"
  counter_state = shelve.open(build_dir + "/counter_state")
  counter_state['counter'] = 1
  counter_state.close()
  print "counter_state inited"
  workq_state = shelve.open(build_dir + "/workq_state")
  workq_state['workq'] = []
  workq_state.close()
  print "workq state inited"
  readyq = FifoDiskQueue(build_dir + "/readyq")
  readyq.close()
  del readyq
  print "readyq inited"
  doneq = FifoDiskQueue(build_dir + "/doneq")
  doneq.close()
  del doneq
  print "doneq inited"
  print "init done"

