#!/usr/bin/python
import csv

# Inputs (hardcoded, yah)

# 1 tsv where we rename samples
MISC_TSV = "clindata.provisional.oct10.tsv"
# 1 tsv where we dont
COHORT_TSV = "clin.v3.tab"
# mapping file
MAPPING_FILE="IDENTIFIERS.tsv"
# expression sample list  
EXPRESSION_SAMPLES = "samples.from.expression.txt"
# header row for the output file
OUTPUT_HEADER = "header.for.output.file.tsv"

# Files we will create
MISC_TSV_RENAMED = "clindata.newsampleids.tsv"
RESULT_METADATA_TSV = "output.tsv"

# TODO
# Need to account for study delimiters
# Probably what will happen ultimately : we will need
# study delimiter to be a new column in the 
# COHORT_TSV and MISC_TSV. I mean preferably the delimiter
# would just be already attached to the sample name.
# but then we need to add it properly in the mapping file as well. 

# note : 
# if a sample is listed multiple times in the metadata tsvs,
# the first one encountered will have its metadata used;
# further encounters will be silently discarded.

# If a sample is listed multiple times in the EXPRESSION_SAMPLES,
# Again, later uses will be silently discarded.


## RUN IT ##

def main():

   # 1. Rename MISC samples per mapping file


   # get the mapping
   with open(MAPPING_FILE, "r") as ids:
      reader=csv.reader(ids, delimiter="|")
      their_ids_to_ours=dict((r[0], r[1]) for r in reader)

   print("mapped:")
   print(their_ids_to_ours)
   # rename the samples
   with open(MISC_TSV, "r") as md_tsv_in:
      with open(MISC_TSV_RENAMED, "w") as md_tsv_out:
         writer=csv.writer(md_tsv_out, delimiter="\t", lineterminator="\n")
         reader=csv.reader(md_tsv_in, delimiter="\t")
         for line in reader:
            check_this_sample = line[0]
            if(check_this_sample in their_ids_to_ours):
               found_id = their_ids_to_ours[line[0]]
               print("found id to rename")
               print found_id
               line[0] = found_id
            # then write the line
            writer.writerow(line)
      
   # 2. Get  samplenames that we have expression data for
   with open(EXPRESSION_SAMPLES, "r") as samples:
      expr_samples = set(line.strip() for line in samples)

   print("got expression samps")
   #print expr_samples

   ####  Begin making the final metadata file! ###
   with open(RESULT_METADATA_TSV, "w") as result_md:
      result_writer=csv.writer(result_md, delimiter="\t", lineterminator="\n")

      # Should probably give the output a header line
      with open(OUTPUT_HEADER, "r") as headerline:
         result_md.write(headerline.readline())

      # 3a and 3b duplicate code, oops. could fix. TODO.

      # 3a. Go through the cohort md tsv and discard samples not in set
      with open(COHORT_TSV, "r") as cohort_md:
         cohort_reader=csv.reader(cohort_md, delimiter="\t")
         for line in cohort_reader:
            sample_id = line[0]
            # we could make this faster by just attempting to remove
            # and catching the keyerror to know it wasnt there
            
            # if the metadata is in expression   
            if(sample_id in expr_samples):
               result_writer.writerow(line)
               expr_samples.remove(sample_id)
            # if not, line isn't written to output
      # 3b - also go through the renamed misc tsv
      with open(MISC_TSV_RENAMED, "r") as misc_md:
         misc_reader=csv.reader(misc_md, delimiter="\t")
         for line in misc_reader:
            sample_id = line[0]
            if(sample_id in expr_samples):
               result_writer.writerow(line)
               expr_samples.remove(sample_id)
      # ok.
      # at this point, we've found all the overlap
      # now we just need to make fake lines for any expr_samples
      # we didn't find in the metadata.

      for sample in expr_samples :
         print("adding extra sample")
         print sample
         # consstruct the line
         newline = [sample] + [""] * 12 # 13 columns total.
         result_writer.writerow(newline)
    
  

   print("done; result is in output.tsv")

if __name__ == '__main__':
   main()

