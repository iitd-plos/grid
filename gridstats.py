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
from gridmaster import stats

def main():
  task = stats.delay()
  stat = task.get(timeout = 3600)
  print stat
  

if __name__ == "__main__":
  main()
