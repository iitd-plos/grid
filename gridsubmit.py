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
  parser.add_argument("filename", help='file containing newline-separated jobs', type = str)
  args = parser.parse_args()
  with open(args.filename, 'r') as fh:
    for line in fh:
      if line[0] != '#':
        submit.delay(job_command)

if __name__ == "__main__":
  main()
