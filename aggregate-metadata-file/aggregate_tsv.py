#!/usr/bin/python2.7

# requires python 2.7 for writeheader
import csv

# Inputs (hardcoded, yah)

# 1 tsv where we rename samples
MISC_TSV = "clin.misc.tsv"
# 1 tsv where we dont
COHORT_TSV = "clin.v3.tab"
# mapping file for renaming samples
MAPPING_FILE="IDENTIFIERS.tsv"
# mapping file for study namespaces
STUDY_MAPPING_FILE="metadata_mapping_to_study.tsv"
# expression sample list  
EXPRESSION_SAMPLES = "samples.from.expression.txt"

# Files we will create
RESULT_METADATA_TSV = "output.tsv"

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


   # get the study namespace mapping as well  
   with open(STUDY_MAPPING_FILE, "r") as studies:
      reader=csv.reader(studies, delimiter="|")
      studyname_to_namespace=dict((r[0],r[1]) for r in reader) 
 
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
            # and get the study ID
            dataset_label = line['Dataset']
            if(dataset_label in studyname_to_namespace):
               study_id = studyname_to_namespace[dataset_label]
            else:
               study_id = "NOT_FOUND"
               print("Couldn't find study id for Dataset='%s'" % dataset_label)

            # fully qualified sample ID
            fq_sample_id = study_id + "/" + sample_id
            # if the metadata is in expression, write it
            if(fq_sample_id in expr_samples):
               # add the study namespace back to the metadata
               line['sampleID'] = fq_sample_id
               result_writer.writerow(line)
               expr_samples.remove(fq_sample_id)
            else:
               print("Didn't find sample '%s' in expression data, dropping." % fq_sample_id)
         # with open misc  
         with open(MISC_TSV, "r") as misc_md:
            misc_reader=csv.DictReader(misc_md, delimiter="\t")

            # If there are fields in the cohort tsv that aren't in
            # this TSV, give up and yell. Will catch renamed fields too
            extrafields = set(field_order) - set(misc_reader.fieldnames)
            if(extrafields):
               print("Metadata file is missing the following necessary fields! %s" % extrafields)
               exit()

            # If there are fields in the misc tsv NOT in the cohort, be aware and drop them
            remove_these_fields = set(misc_reader.fieldnames) - set(field_order)
            if(remove_these_fields):
               print("will drop the extra fields %s from misc tsv" % remove_these_fields)

            # For each item in the misc tsv
            # Rename the sample if we have a mapping and add study namespace
            # lots of duplicated logic with the stuff above 
            for line in misc_reader:
               #print("trying line %s" % line)
               for dropfield in remove_these_fields:
                  del line[dropfield]
               #print("line with fields dropped is %s" % line)

               check_this_sample=line['sampleID']
               # See whether the sample needs renaming - if so , run that mapping
               found_id = check_this_sample # in case it doesnt need renaming
               if(check_this_sample in their_ids_to_ours):
                  found_id=their_ids_to_ours[check_this_sample]
                  print("found ID to rename: %s to %s" % (check_this_sample, found_id))
                  line['sampleID'] = found_id
               # then add the study namespace
               # repeated from cohort stuff above  Iguess
               dataset_label = line['Dataset']
               if(dataset_label in studyname_to_namespace):
                  study_id = studyname_to_namespace[dataset_label]
               else:
                  study_id = "NOT_FOUND"
                  print("Couldn't find study id for Dataset='%s'" % dataset_label)
               fq_found_id = study_id + "/" + found_id

               # if we found it AND we have the sample in the expression file,
               # write it with teh study namespace back to the metadata
               if(fq_found_id in expr_samples):
                  line['sampleID'] = fq_found_id
                  result_writer.writerow(line)
                  expr_samples.remove(fq_found_id) 
               else:
                  print("Didn't find sample '%s' in expression data, dropping." % fq_found_id)
         # done with the input dicts
         # now, make lines for any samples we didnt' find in the metadata
         for sample in expr_samples :
            print("sample %s not found in metadata -- adding" % sample)
            newline = {"sampleID" : sample}
            result_writer.writerow(newline) # omitted fields are blank
    
   print("done; result is in output.tsv")

if __name__ == '__main__':
   main()

