#!/usr/bin/python

# Given a file containing paths to rna-seq output directories
# prints the UMEND for each of those results.
# UMEND  is in readDist.txt_PASS_qc.txt or FAIL ; it's the
# item under estExonicUniqMappedNonDupeReadCount 

import sys
import os.path

# Read UMEND from the umend file and print along with dir
def get_umend(infile, path_to_print):
   with open(infile, "r") as f:
      firstline = f.readline()
      secondline = f.readline()
      want =  "input\tuniqMappedNonDupeReadCount\testExonicUniqMappedNonDupeReadCount\tqc\n"
      if firstline == want:
         # looks like a good readDist file, grab the umend and print w filepath
         items = secondline.split("\t") 
         print "{}\t{}".format(path_to_print, items[2])
      else:
         print "{}\tERROR: doesn't look like a valid UMEND file".format(infile)

#### MAIN ####

input_file=sys.argv[1]

with open(input_file, "r") as f:
   for line in f:
      path = line.rstrip()
      passpath = os.path.join(path, "QC", "bamQC", "readDist.txt_PASS_qc.txt")
      failpath = os.path.join(path, "QC", "bamQC", "readDist.txt_FAIL_qc.txt")
      if os.path.isfile(passpath):
         get_umend(passpath, path)
      elif os.path.isfile(failpath):
         get_umend(failpath, path)
      else:
         print "{}\tERROR: doesn't have a pass or fail UMEND file".format(path)
