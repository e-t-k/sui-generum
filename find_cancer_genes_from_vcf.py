#!/usr/bin/python
import csv
import os
import subprocess
import re

# Preprocessing steps before using this script:
# Create a file with a list of directory names.

# This script will enter each named directory
# for each file ending in ".vcf" in that directory, it will
# compare it to the "canonical" gtf file
# via BEDOPS' bedmap:
# $ bedmap --echo --echo-map-id src1 src2 > dest
# It then does post processing to add gene names.
# Output file contains:
# For each call in the vcf that overlapped a gene
# it lists that call, the gene id(s), gene name(s), and then
# IN_CGC if at least one of those genes is in the 
# cancer gene census, or NO_CGC if not.


# Configuration
# 

TARGET_DIRECTORIES="dirs.containing.vcfs.txt"
GTF_FILE= "sourcefiles/gencode.v19.annotation_NOPARY.genes_only.chr_stripped.bed"

# BEDOPS configuration
VCF2BED = "vcf2bed" # use full path if it's not in your PATH
BEDMAP = "bedmap" # "

INCGC = "IN_CGC"
NOTCGC = "NOT_CGC"

# will be a hash of gene id -> gene name
IDS_TO_GENES_LIST = "sourcefiles/gene_id_to_name.mapping.final.tsv"
IDS_TO_GENES = {}
# and which gene names are in the cancer gene census?
GENES_IN_CENSUS_LIST="sourcefiles/cancer_gene_names.final.txt"
CANCER_GENE_CENSUS=set()


def convert_to_bed(vcf):
   outbed = vcf + ".bed"
   with open(vcf, "r") as vcf_fh:
      with open(outbed, "w") as bed_fh:
         subprocess.check_call(VCF2BED, stdin=vcf_fh, stdout=bed_fh)
   return outbed

def compare_to_gtf(bed):
   outbed = bed + ".genes"
   compare_cmd = [BEDMAP, "--echo", "--echo-map-id",
                  bed, GTF_FILE]

   with open(outbed, "w") as outbed_fh:
      subprocess.check_call(compare_cmd, stdout=outbed_fh)
   return outbed

def add_gene_names(bed):
   result = bed + ".filtered.bed"
   with open(bed, "r") as infile:
      with open(result, "w") as outfile:
         for line in infile:
            line = line.rstrip()
            # reset - is this line in the cancer gene census
            in_cgc = NOTCGC
            
            # Get the gene IDs. If there's none, omit this line.
            gene_ids = line.split("|")[-1].split(";")
            if gene_ids == [""]:
               continue
            else:
               genes = set(map(lambda(x):IDS_TO_GENES[x], gene_ids))
               for gene in genes:
                  # If at least one of them is in the CGC, mark the line
                  if gene in CANCER_GENE_CENSUS:
                     in_cgc = INCGC
               # Add on gene names -- NOT IN SAME ORDER necessarily as gene ids
               newline = (line +   "|" + ";".join(genes) + "|" + in_cgc+ "\n") 
               outfile.write(newline)
   return result

def process_vcf(dir, vcf):
   vcfpath = os.path.join(dir, vcf)
 
   print "processing %s..." % vcfpath
   src_bed = convert_to_bed(vcfpath)
   result_bed = compare_to_gtf(src_bed)
   final_result = add_gene_names(result_bed)
   print "created %s." % final_result 

def main():

   # Before we do anything, set up the mapping between
   # gene IDs and gene names.
   global IDS_TO_GENES  
   with open(IDS_TO_GENES_LIST, "r") as gids:
      reader = csv.reader(gids, delimiter="\t")
      IDS_TO_GENES = dict((r[0], r[1]) for r in reader)

   # also set up the cancer gene census info
   global CANCER_GENE_CENSUS
   with open(GENES_IN_CENSUS_LIST, "r") as gic:
      reader = csv.reader(gic)
      for row in reader:
         CANCER_GENE_CENSUS.add(row[0])       


   # open target dirs and get vcfs in
   with open(TARGET_DIRECTORIES) as dirs:
      for dir in dirs:
         dir = dir.rstrip()
         # find all files ending in .vcf.
         # OSError here indicates a dir entry wasn't found.
         vcfs = filter(lambda x: re.compile('\.vcf$').search(x),
                        os.listdir(dir))
         print vcfs
         for vcf in vcfs:
            process_vcf(dir, vcf)

   print "Done!"


if __name__ == '__main__':
   main()

