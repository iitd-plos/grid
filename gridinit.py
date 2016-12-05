#!/usr/bin/python

import Queue
import subprocess
import os
import datetime
import argparse
import shutil
import multiprocessing
from celery import Celery
from gridmaster import init

def main():
  print "calling init.delay()"
  task = init.delay()
  print "calling init.get()"
  task.get(timeout = 3600)
  print "done calling init.get()"
  

if __name__ == "__main__":
  main()
