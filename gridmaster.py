from celery import Celery
import Queue
import os

counter = 1
readyq = Queue.Queue()
workq = []
doneq = []

gridmaster_host = os.environ['GRIDMASTER_HOST']
print "gridmaster_host = " + gridmaster_host
app = Celery('gridmaster', backend='rpc://', broker='pyamqp://guest@' + gridmaster_host + '//')
EMPTY = "empty"

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
def getwork():
  global counter
  global readyq
  global workq
  global doneq
  try:
    (mycounter, task) = readyq.get_nowait()
    workq.append((mycounter, task))
    print "getwork returned \"" + task + "\" at mycounter " + str(mycounter)
  except Queue.Empty:
    print "Queue empty. getwork failed"
    task = EMPTY
    mycounter = 0
  return (mycounter, task)

@app.task
def donework(task):
  global counter
  global readyq
  global workq
  global doneq
  if task in workq:
    workq.remove(task)
    doneq.append(task)
  else:
    print "Error: task not in workq"

@app.task
def stats():
  global counter
  global readyq
  global workq
  global doneq
  ret = "Counter: " + str(counter) + "\n"
  ret += "ReadyQ: " + str(readyq.qsize()) + "\n"
  ret += "WorkQ: " + str(len(workq)) + "\n"
  ret += "DoneQ: " + str(len(doneq)) + "\n"
  return ret
