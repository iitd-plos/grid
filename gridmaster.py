from celery import Celery
#from queuelib import FifoDiskQueue
from config_host import *
import Queue
import datetime
import os
import shelve
#import pickle

gridmaster_host = os.environ['GRIDMASTER_HOST']
#print "gridmaster_host = " + gridmaster_host
app = Celery('gridmaster', backend='rpc://', broker='pyamqp://guest@' + gridmaster_host + '//')

@app.task
def init():
  state = shelve.open(build_dir + "/state")
  state['counter'] = 1
  state['readyq'] = []
  state['workq'] = []
  state['doneq'] = []
  state.close()

@app.task
def submit(task):
  state = shelve.open(build_dir + "/state")
  print "submitting \"" + task + "\" at counter " + str(state['counter'])
  readyq = state['readyq']
  readyq.append((state['counter'], task))
  state['counter'] += 1
  state['readyq'] = readyq
  state.close()

@app.task
def getwork(workername):
  curtime = datetime.datetime.now()
  mycounter = 0
  task = ""
  state = shelve.open(build_dir + "/state")
  readyq = state['readyq']
  workq = state['workq']
  if len(readyq) > 0:
    (mycounter, task) = readyq.pop(0)
    workq.append((mycounter, workername, curtime, task))
    print "getwork returned \"" + task + "\" at mycounter " + str(mycounter)
  else:
    #print "Queue empty. getwork failed"
    task = ""
    #if (len(workq) > 0):
    #  w = workq[0]
    #  (wcounter, wname, wtime, task) = w
    #  if (curtime - wtime).total_seconds() > 600:
    #    print "found work item older than 600 seconds; redoing"
    #    workq.pop(0)
    #    workq.append((wcounter, workername, curtime, task))
    #    mycounter = wcounter
  state['readyq'] = readyq
  state['workq'] = workq
  state.close()
  return (mycounter, workername, curtime, task)

@app.task
def donework(task):
  #print "donework called"
  curtime = datetime.datetime.now()
  (mycounter, workername, ts, work) = task
  #print str(mycounter) + " " + workername + " " + work
  remove_index = -1
  i = 0
  state = shelve.open(build_dir + "/state")
  workq = state['workq']
  doneq = state['doneq']
  for w in workq:
    (wcount, wname, wts, wwork) = w
    if wcount == mycounter:
      remove_index = i
    i += 1
  if remove_index >= 0:
    del workq[remove_index]
    doneq.append((mycounter, workername, ts, curtime, work))
  else:
    print "Error: task counter not in workq"
  state['workq'] = workq
  state['doneq'] = doneq
  state.close()

@app.task
def stats():
  ret = "WorkQ entries:\n"
  state = shelve.open(build_dir + "/state")
  for w in state['workq']:
    (wcount, wname, wts, wwork) = w
    ret += str(wcount) + " : " + str(wname) + " : " + str(wts) + " : " + wwork + "\n"
  ret += "DoneQ entries:\n"
  for w in state['doneq']:
    (wcount, wname, wts_start, wts_stop, wwork) = w
    ret += str(wcount) + " : " + str(wname) + " : " + str(wts_start) + " : " + str(wts_stop) + " : " + wwork + "\n"
  ret += "Counter: " + str(state['counter']) + "\n"
  ret += "ReadyQ: " + str(len(state['readyq'])) + "\n"
  ret += "WorkQ: " + str(len(state['workq'])) + "\n"
  ret += "DoneQ: " + str(len(state['doneq'])) + "\n"
  state.close()
  return ret
