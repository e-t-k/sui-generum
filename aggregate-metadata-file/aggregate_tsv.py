#!/usr/bin/python
import csv

# Inputs (hardcoded, yah)

# 1 tsv where we rename samples
MISC_TSV = "clindata.2016-10-13.tsv"
# 1 tsv where we dont
COHORT_TSV = "clin.v3.tab"
# mapping file for renaming samples
MAPPING_FILE="IDENTIFIERS.tsv"
# mapping file for study namespaces
STUDY_MAPPING_FILE="Dataset_to_Study.tsv"
# expression sample list  
EXPRESSION_SAMPLES = "samples.from.expression.txt"

# Files we will create
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
   # Get the samples from the expression file
   with open(EXPRESSION_SAMPLES, "r") as samples:
      expr_samples = set(line.strip() for line in samples)


   # Get the mapping
   with open(MAPPING_FILE, "r") as ids:
      reader=csv.reader(ids, delimiter="|")
      their_ids_to_ours=dict((r[0], r[1]) for r in reader)


   # TODO get the study namespace mapping as well  
 
   # then, we need to get the rows from cohort_tsv so we know the
   # output row order before we do anything else.

   with open(COHORT_TSV, "r") as cohort_md:
      cohort_reader=csv.DictReader(cohort_md, delimiter="\t")
      # Get the fieldname order from COHORT_TSV - we will use that in the result file
      field_order=cohort_reader.fieldnames

      with open(RESULT_METADATA_TSV, "w") as result_md:
         result_writer=csv.DictWriter(result_md, field_order, delimiter="\t", lineterminator="\n")
         result_writer.writeheader()
         for line in cohort_reader:
            sample_id = line['sampleID']
            # if the metadata is in expression, write it
            if(sample_id in expr_samples):
               # add the study namespace TODO
               result_writer.writerow(line)
               expr_samples.remove(sample_id)
         # with open misc  
         with open(MISC_TSV, "r") as misc_md:
            misc_reader=csv.DictReader(misc_md, delimiter="\t")

            # If there are fields in the cohort tsv that aren't in
            # this TSV, give up and yell. Will catch renamed fields too
            extrafields = set(field_order) - set(misc_reader.fieldnames)
            if(extrafields):
               print("Metadata file is missing the following necessary fields! %s" % extrafields)
               exit()

            # For each item in the misc tsv
            # Rename the sample if we have a mapping and add study namespace
            for line in misc_reader:
               print line
               check_this_sample=line['sampleID']
               found_id = check_this_sample # in case it doesnt need renaming
               if(check_this_sample in their_ids_to_ours):
                  found_id=their_ids_to_ours[check_this_sample]
                  print("found ID to rename: %s to %s" % (check_this_sample, found_id))
                  line['sampleID'] = found_id
               # add the study namespace TODO
               if(found_id in expr_samples):
                  result_writer.writerow(line)
                  expr_samples.remove(found_id) 
         # done with the input dicts
         # now, make lines for any samples we didnt' find in the metadata
         for sample in expr_samples :
            print("sample %s not found in metadata -- adding" % sample)
            newline = {"sampleID" : sample}
            result_writer.writerow(newline) # omitted fields are blank
    
   print("done; result is in output.tsv")

if __name__ == '__main__':
   main()

