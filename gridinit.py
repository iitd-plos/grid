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
  task = init.delay()
  task.get(timeout = 3600)
  

if __name__ == "__main__":
  main()
