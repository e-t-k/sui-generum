
# this will look in the current directory for folders named
# after the identifier.
# so you will probably have to run it once per submitting center.

# ASSUMPTION :
# the identifier only appears in the first line

# for each pair old|new in the IDENTIFIERS folder
while read line; do

   # Get the old and new identifiers
   oldid=`cut -f1 -d"|" <<< $line`
   newid=`cut -f2 -d"|" <<< $line`


   echo "copying Kallisto - $oldid to $newid"
   # Make folder in the output folder
   mkdir -p /output/$newid/Kallisto
   # copy from current folder to output folder
   cp -r $oldid/Kallisto/* /output/$newid/Kallisto

done < /IDENTIFIERS

echo Done! Now run kallisto_rename.sh to change the filenames.
