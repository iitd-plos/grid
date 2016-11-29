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

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--num-cores", help='number of cores for multiprocessing, default is 1', type=int, default=1)
  args = parser.parse_args()
  num_cores = args.num_cores
  #multiprocessing.Pool(num_cores).map(run_job, list(range(num_cores)), chunksize=1)
  run_job(0)

def run_job(job_id):
  print "Running on core " + str(job_id)
  while True:
    task = getwork.delay()
    while (not task.ready()):
      pass
    (work_id, work) = task.get(timeout=3600)
    if (work_id > 0 and execute(work)):
      #print "work_id " + str(work_id) + ", work " + work
      donework.delay((work_id, work))
    time.sleep(2)

def execute(work):
  subprocess.call(work, shell=True)

if __name__ == "__main__":
  main()
