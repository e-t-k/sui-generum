#!/usr/bin/python
import csv
import os
import subprocess

# Preprocessing steps before using this script:
#
# 1. Create a directory with all vcfs available untarred. Example:
#
# ls > files_to_untar.txt
# while read line; do tar zxvf $line ; done < files_to_untar.txt
#
# 2. Create two TSVs in the following format (example):
# patientId	path_to_file
# 0001	/pod/pstore/groups/[...]A04100.alleleCount.vcf	
# 
# One tsv for the tgen files, one for the mutect files. the patientId
# is the mapping key for which pairs of files to compare and does not need
# to exactly match the actual patient ID. This key will be used for naming
# the results folder.

# Configuration
# 
tgen_mapping_file = "patient.tgen.tsv"
mutect_mapping_file = "patient.mutect.tsv"
path_to_vcftools_exe = "vcftools" # use full path or put it in your PATH

out_basedir = "results"

def run_vcftools(item):
   outdir = out_basedir + "/" + item[0] + ".output"
   file_info = item[1]
   tgen_path = file_info["tgen_vcf"]
   cleaned_mutect_path = file_info["cleaned_mutect_vcf"]

   # Skip vcftools if the outdir already exists.
   if os.path.isdir(outdir):
      print "SKIPPING RERUN OF VCFTOOLS for %s" % outdir
      print "Delete this directory to force rerun."
      return

   os.mkdir(outdir)

   # run VCFtools on input files into output directory
   vcf_command = [path_to_vcftools_exe,
                  "--vcf", tgen_path,
                  "--diff", cleaned_mutect_path,
                  "--diff-site",
                  "--out", "%s/out" % ( outdir) ]

   # Add the --not-chr commands to filter out non-overlapping chrs
   no_chrs = map(make_nochr_arg, file_info["reject_these_chr"]) 
   for chr in no_chrs:
      vcf_command += chr
   #print " ".join(vcf_command)
   subprocess.check_call(vcf_command)
   # CalledProcessError indicates this failed

def make_nochr_arg(x):
   return ["--not-chr", x]
 
def make_extra_files(item):
   # TODO correctly use output pase dir
   # the strings for these filename found in run_vcftools above
   outdir = item[0] + ".output"
   # What to do here :


   # TODO do the header lines stuff later
   # get header lines from tgen file, first.

   # read out.diff.sites_in_files, parse on the IN_FILE column
   # B -> copy to sites_found_in_both_files

   # 1 -> tmp file for tgen
   # 2 -> tmp file for mutect
   # then. 
   # the tmp files are CHR and POS[FOR TGEN/vs mutect - use correct column!]
   # then for each, print header lines to make the vcf files
   # then for each, grep -f -F with ^ to make the vcf files and append,
   # then do a quick grep -vc to see if counts are good. 
   #



   pass


# Iterates through the mutect VCF file
# creates a new vcf with the following changes:
# Lines with REJECT in the FILTER column are dropped
# all cromosomes in CHROM column with format chr$X are changed to $X
def clean_mutect_vcf(mutect_filename):
   cleaned_filename = mutect_filename + ".cleaned.vcf" 
   headers = [] # TODO decouple


   # Skip cleaning if a cleaned file already exists.
   if os.path.isfile(cleaned_filename):
      print "Already cleaned %s, skipping." % mutect_filename
      return {"cleaned_filename" : cleaned_filename, "mutect_header" : headers}


   # Set up the dialect to pass quotes, etc through verbatim
   csv.register_dialect('vcf_file', delimiter="\t",
                                 quotechar="",
                                 lineterminator=os.linesep,
                                 quoting=csv.QUOTE_NONE)

   with open(mutect_filename, "rb") as src:
      with open(cleaned_filename, "wb") as dest:
         writer = csv.writer(dest, 'vcf_file')
         for line in csv.reader(src, 'vcf_file'):
            # If it's a comment, add it to the header text to be returned
            # and also write it to the output file.
            if line[0][0] == "#":
           #    headers.append("\t".join(line))
               writer.writerow(line)
               continue
            # skip if it has REJECT in the FILTER field?
            # fields are:
            #CHROM POS ID REF ALT QUAL FILTER INFO FORMAT...
            if line[6] == "REJECT":
               continue
            # replace chr in CHROM field
            line[0] = line[0].replace("chr", "", 1)
            # bugs: -- won't catch CHR, just chr
            #       -- will turn my_chromX -> my_omX
            # and write
            writer.writerow(line)
   
   return {"cleaned_filename" : cleaned_filename, "mutect_header" : headers}

# get the vcf headers for appending to generated vcfs TODO
def get_vcf_headers(filename):
   pass


def get_chr(filename):
   chrs = set()
   with open(filename) as src:
      for line in csv.reader(src, delimiter="\t"):
         if line[0][0] == "#":
            continue
         chrs.add(line[0])
   return chrs

def reject_chr(mchrs, tchrs):
   return (mchrs ^ tchrs) # symmetric difference - elements only in 1 set
 
# Main operation
def main():

   # stores tgen, mutect filepaths to patient IDs
   # { '0001' -> { tgen_vcf -> "path", 
   #               mutect_vcf -> "path", 
   #              cleaned_mutect_vcf -> "path",
   #              mutect_header = ["#com1", "#com2"],
   #              tgen_header = ["#com1", "#com2"],
   #              mutect_chr =set(1,2,3),
   #              tgen_chr =set(1,2,3),
   #              reject_these_chr = set(X) }
   MAPPING = {}

   # Determine relevant files
   with open(tgen_mapping_file) as tgen_mapping:
      for line in csv.reader(tgen_mapping, delimiter="\t"):
         MAPPING[line[0]] = { "tgen_vcf":line[1]}
   with open(mutect_mapping_file) as mutect_mapping:
      for line in csv.reader(mutect_mapping, delimiter="\t"):
         MAPPING[line[0]]["mutect_vcf"] = line[1]
            # Throws KeyError if there's a patient in the mutect file
            # that wasn't in the tgen file.
   
   # Reprocess mutect vcfs:
   # remove REJECT lines & chrX -> X
   for patient, files in MAPPING.items():
      print "Cleaning file for %s" % patient
      res =  clean_mutect_vcf(files["mutect_vcf"])
      files["cleaned_mutect_vcf"] = res["cleaned_filename"]
      files["mutect_header"] = res["mutect_header"]

   # Also get chromosome list for each pair and calculate
   # intersection for --not-chr field when running vcftools
      files["mutect_chr"] = get_chr(files["cleaned_mutect_vcf"])
      files["tgen_chr"] = get_chr(files["tgen_vcf"])
      files["reject_these_chr"] = reject_chr(files["mutect_chr"],
                                             files["tgen_chr"])
   
         # throws KeyError here if there's a patient in the tgen file
         # with no corresponding mutect file

   # test
   print MAPPING
   #exit() # TODO
   # run vcftools on each pair
   # and create additional output files
   for item in MAPPING.items():
      run_vcftools(item)
      make_extra_files(item)


if __name__ == '__main__':
   main()
