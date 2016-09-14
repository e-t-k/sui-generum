#!/bin/bash

# Selects from a rectangular file the expression data
# for a particular gene -- every sample, as well as only samples
# from a chosen sub cohort (AML in this case.)

#### INPUT ####
# Following files must exist in this dir:
# DESIRED_GENES : 1-per-line gene names you want to extract
# EVERY_GENE_EXPRESSION.tsv : rectangular file with expression data
# EVERY_GENE_NAME : cut -f 1 EVERY_GENE_EXPRESSION
# EVERY_SAMPLENAME : head -n 1 EVERY_GENE_EXPRESSION with 1 name per line
# EVERY_AML_SAMPLENAME : 1 samplename per line of only samples in sub cohort

#### OUTPUT ####
# (gene name).pancancer.tsv 
# (gene name).AML.tsv

# get genes from DESIRED_GENES
while read line
  do
    # Find it in the cohort; use -x for exact line match
    #geneline=`grep -m1 -n -x -F $line EVERY_GENE_NAME | cut -d ":" -f 1`
    foundgene=`grep -m1 -n -x -F $line EVERY_GENE_NAME`
    geneline=`echo $foundgene | cut -d ":" -f 1`
    echo Searched for $line and found $foundgene
    # get that line
    head -n $geneline EVERY_GENE_EXPRESSION.tsv | tail -n 1 > $line.oneline.tsv.tmp
    # verticalize it
    sed -e 's/\t/&\n/g' < $line.oneline.tsv.tmp > $line.pancancer.tsv
    # connect it to samplenames
    paste EVERY_SAMPLENAME $line.pancancer.tsv > $line.with.samplenames.tsv.tmp
    # get only AML samples
    grep -F -f EVERY_AML_SAMPLENAME $line.with.samplenames.tsv.tmp | cut -f 2 > $line.AML.tsv
    rm *.tsv.tmp
  done < DESIRED_GENES
