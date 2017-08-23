#!/usr/bin/python

# Given a file containing paths to rna-seq output directories
# prints the UMEND for each of those results.
# UMEND  is in readDist.txt_PASS_qc.txt or FAIL ; it's the
# item under estExonicUniqMappedNonDupeReadCount 
# paths should not include the FAIL. prefix ; it will detect and add this

import sys
import os.path

# Read UMEND from the umend file and print along with dir
def get_umend(infile, path_to_print):
   if os.path.isfile(infile):
      with open(infile, "r") as f:
         firstline = f.readline()
         secondline = f.readline()
         want =  "input\tuniqMappedNonDupeReadCount\testExonicUniqMappedNonDupeReadCount\tqc\n"
         if firstline == want:
            # looks like a good readDist file, grab the umend and print w filepath
            items = secondline.split("\t") 
            print "{}\t{}".format(path_to_print, items[2])
         else:
            print "{}\tERROR: has a correctly named UMEND file but bad contents".format(path_to_print)
   else:
      print "{}\tERROR: doesn't have a UMEND file or it doesn't match FAIL status of sampledir".format(path_to_print)

#### MAIN ####

input_file=sys.argv[1]

with open(input_file, "r") as f:
   for line in f:
      path = line.rstrip()
      passdir = path
      faildir = os.path.join(os.path.dirname(path), "FAIL.{}".format(os.path.basename(path)))

      # If we can't find it, see if it's a FAIL. sample
      if os.path.isdir(passdir):
         passpath = os.path.join(passdir, "QC", "bamQC", "readDist.txt_PASS_qc.txt")
         get_umend(passpath, passdir)

      elif os.path.isdir(faildir):
         failpath = os.path.join(faildir, "QC", "bamQC", "readDist.txt_FAIL_qc.txt")
         get_umend(failpath, faildir)

      else:
         print "{}\tERROR: Can't find sampledir or FAIL.sampledir".format(path)
