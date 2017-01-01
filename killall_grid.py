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

for w in workers:
  subprocess.call("ssh xorav" + w + " \"killall -9 harvest\"", shell=True)
  subprocess.call("ssh xorav" + w + " \"killall -9 peepgen\"", shell=True)
