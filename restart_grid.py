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

subprocess.call("make killmaster", shell=True)
for w in workers:
  subprocess.call("ssh xorav" + w + " \"cd grid && make killworker && make runworker\" ", shell=True)
subprocess.call("make runmaster", shell=True)
