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
  parser.add_argument("job", help='job command', nargs="+")
  args = parser.parse_args()
  #job_command = utils.merge_multiple_globs(args.job)
  job_command = "".join(args.job)
  submit.delay(job_command)

if __name__ == "__main__":
  main()
