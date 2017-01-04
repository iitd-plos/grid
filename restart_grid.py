#!/usr/bin/python

import Queue
import subprocess
import os
import datetime
import argparse
import shutil
import multiprocessing
from celery import Celery
from gridmaster import submit
from gridmaster import getwork
from gridmaster import donework

workers = ("02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16")
gridmaster_host = os.environ['GRIDMASTER_HOST']

subprocess.call("make killmaster", shell=True)
subprocess.call("make runmaster", shell=True)
for w in workers:
  cmd = "ssh xorav" + w + " \"source .profile && cd grid && make killworker && make GRIDMASTER_HOST=" + gridmaster_host + " runworker\""
  print "execing " + cmd
  subprocess.call(cmd, shell=True)
subprocess.call("make killmaster", shell=True)
subprocess.call("make runmaster", shell=True)
