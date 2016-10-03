#!/bin/bash



# $1 = full path to file name

# so we need to
# figure out old and new identifiers
# change old identifier in filename (just remove it)
# change old identifier in first line of file

# find new filename :

oldid=$1
newid=$2

echo "Updating $oldid files to $newid"

# go to the correct output folder
# VERY IMPORTANT
path=/output/$newid
cd $path
# rename files to new identifier
find .  -exec rename $oldid $newid {} \;

# then edit their contents as well
find . -type f -name "*.tab" -exec sed -i -e "0,/$oldid/{s/$oldid/$newid/}" {} \;

