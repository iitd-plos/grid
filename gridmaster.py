CELERY_AMQP_TASK_RESULT_EXPIRES = 60

from celery import Celery
from queuelib import FifoDiskQueue
from config_host import *
import Queue
import datetime
import os
import shelve
import pickle

gridmaster_host = os.environ['GRIDMASTER_HOST']
#print "gridmaster_host = " + gridmaster_host
app = Celery('gridmaster', backend='rpc://', broker='pyamqp://' + gridmaster_host)

@app.task()
def init():
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
  return ""

@app.task(ignore_result=True)
def submit(task):
  counter_state = shelve.open(build_dir + "/counter_state")
  print "submitting \"" + task + "\" at counter " + str(counter_state['counter'])
  cur_counter = counter_state['counter']
  counter_state['counter'] = cur_counter + 1
  counter_state.close()
  readyq = FifoDiskQueue(build_dir + "/readyq")
  readyq.push(pickle.dumps((cur_counter, task), protocol=2))
  readyq.close()

@app.task
def getwork(workername):
  curtime = datetime.datetime.now()
  mycounter = 0
  task = ""
  readyq = FifoDiskQueue(build_dir + "/readyq")
  workq_state = shelve.open(build_dir + "/workq_state")
  workq = workq_state['workq']
  if len(readyq) > 0:
    (mycounter, task) = pickle.loads(readyq.pop())
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
  workq_state['workq'] = workq
  workq_state.close()
  readyq.close()
  return (mycounter, workername, curtime, task)

@app.task(ignore_result=True)
def donework(task):
  #print "donework called"
  curtime = datetime.datetime.now()
  (mycounter, workername, ts, work) = task
  #print str(mycounter) + " " + workername + " " + work
  remove_index = -1
  i = 0
  workq_state = shelve.open(build_dir + "/workq_state")
  workq = workq_state['workq']
  doneq = FifoDiskQueue(build_dir + "/doneq")
  for w in workq:
    (wcount, wname, wts, wwork) = w
    if wcount == mycounter:
      remove_index = i
    i += 1
  if remove_index >= 0:
    del workq[remove_index]
    doneq.push(pickle.dumps((mycounter, workername, ts, curtime, work), protocol=2))
  else:
    print "Error: task counter not in workq"
  workq_state['workq'] = workq
  doneq.close()
  workq_state.close()

@app.task
def stats():
  ret = "WorkQ entries:\n"
  workq_state = shelve.open(build_dir + "/workq_state")
  workq_size = 0
  for w in workq_state['workq']:
    (wcount, wname, wts, wwork) = w
    ret += str(wcount) + " : " + str(wname) + " : " + str(wts) + " : " + wwork + "\n"
    workq_size += 1
  workq_state.close()
  #ret += "DoneQ entries:\n"
  #for w in state['doneq']:
  #  (wcount, wname, wts_start, wts_stop, wwork) = w
  #  ret += str(wcount) + " : " + str(wname) + " : " + str(wts_start) + " : " + str(wts_stop) + " : " + wwork + "\n"
  counter_state = shelve.open(build_dir + "/counter_state")
  ret += "Counter: " + str(counter_state['counter']) + "\n"
  counter_state.close()
  readyq = FifoDiskQueue(build_dir + "/readyq")
  ret += "ReadyQ: " + str(len(readyq)) + "\n"
  readyq.close()
  ret += "WorkQ: " + str(workq_size) + "\n"
  doneq = FifoDiskQueue(build_dir + "/doneq")
  ret += "DoneQ: " + str(len(doneq)) + "\n"
  doneq.close()
  return ret
