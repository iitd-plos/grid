#!/usr/bin/python

import Queue
import subprocess
import os
import datetime
import argparse
import shutil

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help='file containing newline-separated jobs', type = str)
  parser.add_argument("--num-stripes", help='number of stripes', type = int, default = 15)
  args = parser.parse_args()
  jobs = {}
  filename = os.path.abspath(args.filename)
  num_stripes = args.num_stripes
  for i in range(0, num_stripes):
    jobs[i] = ""
  i = 0
  with open(filename, 'r') as fh:
    for line in fh:
      if line[0] != '#':
        jobs[i] = jobs[i] + line
        i = (i + 1) % num_stripes
  jobs_filename = []
  for i in range(0, num_stripes):
    jobs_filename.append(filename + '.' + str(i))
    with open(jobs_filename[i], 'w') as fh:
      fh.write(jobs[i])
  if num_stripes <= 15:
    p = []
    for i in range(0, 15):
      node_num = str(i + 2)
      if (len(node_num) == 1):
        node_num = "0" + node_num
      node_name = "xorav" + node_num
      logfile = node_name + ".log"
      cmd = "ssh " + node_name + " \"parallel -j 8 :::: " + jobs_filename[i] + "\""
      p.append(subprocess.Popen(cmd, shell=True))
    for i in range(0, 15):
      p[i].communicate()

if __name__ == "__main__":
  main()
