#!/bin/bash

# start with expression.tsv
# creates samples.from.expression.tsv needed for the py script

head -n 1 expression.tsv > samplenames.oneline.txt
sed -e "s/\t/\n/g" < samplenames.oneline.txt > samplenames.withGene.txt
# remove 'Gene' header
tail -n +2 samplenames.withGene.txt > samplenames.txt

# TODO - right now we are removing the study delimiters
# ie, everything before a /
#  ultimately, want to leave them in, I think
# but right now they're not in the metadata tsvs.
sed -e "s/.*\///" < samplenames.txt > samples.from.expression.txt

# TODO - if we're removing the study delimiters,
# we also have to remove them from the expression TSV as well
# do this manually. eg for delimiters ABCD and ABCD_reference:

# head -n 1 expression.tsv > header.expression
# sed -e "s/ABCD\///g" -e "s/ABCD_reference\///g" < header.expression > header.fixed

# Then replace the first line with header.fixed



