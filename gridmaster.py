from celery import Celery
import Queue
import datetime
import os

counter = 1
readyq = Queue.Queue()
workq = []
doneq = []

gridmaster_host = os.environ['GRIDMASTER_HOST']
#print "gridmaster_host = " + gridmaster_host
app = Celery('gridmaster', backend='rpc://', broker='pyamqp://guest@' + gridmaster_host + '//')

@app.task
def submit(task):
  global counter
  global readyq
  global workq
  global doneq
  try:
    print "submitting \"" + task + "\" at counter " + str(counter)
    readyq.put((counter, task))
    counter += 1
  except Queue.Full:
    print "Queue full. submit failed"

@app.task
def getwork(workername):
  global counter
  global readyq
  global workq
  global doneq
  curtime = datetime.datetime.now()
  mycounter = 0
  task = ""
  try:
    (mycounter, task) = readyq.get_nowait()
    workq.append((mycounter, workername, curtime, task))
    print "getwork returned \"" + task + "\" at mycounter " + str(mycounter)
  except Queue.Empty:
    #print "Queue empty. getwork failed"
    task = ""
    if (len(workq) > 0):
      w = workq[0]
      (wcounter, wname, wtime, task) = w
      if (curtime - wtime).total_seconds() > 600:
        print "found work item older than 600 seconds; redoing"
        workq.pop(0)
        workq.append((wcounter, workername, curtime, task))
        mycounter = wcounter
  return (mycounter, workername, curtime, task)

@app.task
def donework(task):
  global counter
  global readyq
  global workq
  global doneq
  #print "donework called"
  curtime = datetime.datetime.now()
  (mycounter, workername, ts, work) = task
  #print str(mycounter) + " " + workername + " " + work
  remove_index = -1
  i = 0
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

@app.task
def stats():
  global counter
  global readyq
  global workq
  global doneq
  ret = "WorkQ entries:\n"
  for (wc, wn, ts, wt) in workq:
    ret += str(wc) + " : " + str(wn) + " : " + str(ts) + " : " + wt + "\n"
  ret += "DoneQ entries:\n"
  for (dc, dn, dts_start, dts_finish, dt) in doneq:
    ret += str(dc) + " : "
    ret += str(dn) + " : "
    ret += str(dts_start) + " : "
    ret += str(dts_finish) + " : "
    ret += str(dt) + "\n"
  ret += "Counter: " + str(counter) + "\n"
  ret += "ReadyQ: " + str(readyq.qsize()) + "\n"
  ret += "WorkQ: " + str(len(workq)) + "\n"
  ret += "DoneQ: " + str(len(doneq)) + "\n"
  return ret
