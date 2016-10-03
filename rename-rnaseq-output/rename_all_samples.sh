
# for each item in the IDENTIFIERS file
while read line; do
   # get old and new IDS
   oldid=`cut -f1 -d"|" <<< $line`
   newid=`cut -f2 -d"|" <<< $line`
   # run the rename script from old id to new id
   /move_1_sample.sh $oldid $newid

done < /IDENTIFIERS

