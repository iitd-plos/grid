from celery import Celery
import Queue

counter = 1
readyq = Queue.Queue()
workq = []
doneq = []

app = Celery('gridmaster', backend='rpc://', broker='pyamqp://guest@localhost//')
EMPTY = "empty"

@app.task
def submit(task):
  global counter
  global readyq
  global workq
  global doneq
  try:
    print "submitting \"" + task + "\""
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
    (counter, task) = readyq.get_nowait()
    workq.append((counter, task))
    print "getwork returned \"" + task + "\""
  except Queue.Empty:
    print "Queue empty. getwork failed"
    task = EMPTY
    counter = 0
  return (counter, task)

@app.task
def donework(task):
  global counter
  global readyq
  global workq
  global doneq
  if task in workq:
    workq.remove(task)
    doneq.append(task)
