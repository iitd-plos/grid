from celery import Celery
from queuelib import FifoDiskQueue
from config_host import *
import Queue
import datetime
import os
import shelve
import pickle

#counter = 1
#readyq = FifoDiskQueue(build_dir + "/readyq")
#workq = []
#doneq = []

gridmaster_host = os.environ['GRIDMASTER_HOST']
#print "gridmaster_host = " + gridmaster_host
app = Celery('gridmaster', backend='rpc://', broker='pyamqp://guest@' + gridmaster_host + '//')

@app.task
def init():
  counter = shelve.open(build_dir + "/counter")
  counter['counter'] = 1
  counter.close()

@app.task
def submit(task):
  counter = shelve.open(build_dir + "/counter")
  readyq = FifoDiskQueue(build_dir + "/readyq")
  print "submitting \"" + task + "\" at counter " + str(counter['counter'])
  readyq.push(pickle.dumps((counter['counter'], task), protocol=2))
  counter['counter'] += 1
  counter.close()
  readyq.close()

@app.task
def getwork(workername):
  curtime = datetime.datetime.now()
  mycounter = 0
  task = ""
  readyq = FifoDiskQueue(build_dir + "/readyq")
  if len(readyq) > 0:
    workq = FifoDiskQueue(build_dir + "/workq")
    (mycounter, task) = pickle.loads(readyq.pop())
    workq.push(pickle.dumps((mycounter, workername, curtime, task), protocol=2))
    workq.close()
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
  readyq.close()
  return (mycounter, workername, curtime, task)

@app.task
def donework(task):
  #global counter
  #global readyq
  #global workq
  #global doneq
  #print "donework called"
  curtime = datetime.datetime.now()
  (mycounter, workername, ts, work) = task
  #print str(mycounter) + " " + workername + " " + work
  remove_index = -1
  i = 0
  os.remove(build_dir + "/tmp_workq")
  workq = FifoDiskQueue(build_dir + "/workq")
  tmp_workq = FifoDiskQueue(build_dir + "/tmp_workq")
  while (len(workq) > 0):
    w = pickle.loads(workq.pop())
    (wcount, wname, wts, wwork) = w
    if wcount == mycounter:
      remove_index = i
    else:
      tmp_workq.push(pickle.dumps(w, protocol=2))
    i += 1
  workq.close()
  tmp_workq.close()
  os.rename(build_dir + "/tmp_workq", build_dir + "/workq")
  if remove_index >= 0:
    doneq = FifoDiskQueue(build_dir + "/doneq")
    doneq.push(pickle.dumps((mycounter, workername, ts, curtime, work), protocol=2))
    doneq.close()
  else:
    print "Error: task counter not in workq"

#@app.task
#def stats():
#  ret = "WorkQ entries:\n"
#  for (wc, wn, ts, wt) in workq:
#    ret += str(wc) + " : " + str(wn) + " : " + str(ts) + " : " + wt + "\n"
#  ret += "DoneQ entries:\n"
#  for (dc, dn, dts_start, dts_finish, dt) in doneq:
#    ret += str(dc) + " : "
#    ret += str(dn) + " : "
#    ret += str(dts_start) + " : "
#    ret += str(dts_finish) + " : "
#    ret += str(dt) + "\n"
#  ret += "Counter: " + str(counter) + "\n"
#  ret += "ReadyQ: " + str(readyq.qsize()) + "\n"
#  ret += "WorkQ: " + str(len(workq)) + "\n"
#  ret += "DoneQ: " + str(len(doneq)) + "\n"
#  return ret
