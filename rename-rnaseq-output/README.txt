
Steps:
=================================
1. copy rsem files over
2. rename rsem files
3. copy kallisto files over
4. rename kallisto files


Detailed steps:
=================================
(note: these are edited from an email; I've removed the pathnames specific to the system it was being run on.
So you'll have to add in the full path to some of these commands, probably not difficult to figure out when.)

=================================
1 and 2:
=================================


There's a file named IDENTIFIERS. Look at it. That's the format you need. That's the file you will be editing.

old|new

old need to be the folder names that the RSEM contents are in. new is the new ID eg 1234_S1 . so, eg

S1|1234_S1

Edit the IDENTIFIERS file to put your desired identifiers in it.

NEXT:

files will go into the output/ folder in this folder. 

At any time you can start over by removing all the contents of that folder. you may have to use -f since some files are read only for some reason.



So step 1 is copy over the files.

Go into the rnaseq folder for each of the submitting centers.

then, from that folder, run :

copyFilesOver.sh

This will copy over all the samples in that folder.
So, only samples from that submitting center.
But, it's looking at all samples from all centers. So you will probably see several error messages like :
cp: cannot stat `S1/RSEM/*': No such file or directory

This is fine. This just means the sample in the IDENTIFIERS list is from a different submitting center then the folder you are in right now.

So you'll have to run it from each of the submitting center folders. 

To confirm that you've copied everything over, you can run:

wc -l IDENTIFIERS

and

ls output | wc -l

and confirm they are the same.

Step 2 : rename everything

only run this once

If you run this twice, it will have weird effects and the easiest thing to do will be to delete the contents of the output folder and start over.

To do this step :

rename_all_samples.sh

You can be in any folder.

It will take a few minutes to run.
It'll list what sample it's currently working on.

Once this is done, the following folder will contain all the samples with their new names
and identifiers changed:

output

Copy it somewhere safe!
=================================
3 and 4:
=================================
To run, essentially the same as copying RSEM files:

- list of IDENTIFIERS is already complete.
For each submitting center, navigate to the parent folder containing sample folders.
run :
kallisto.copyFilesOver.sh

This will copy Kallisto files into existing output folder.

When all files copied, run (once) --

kallisto_rename.sh 

This will rename (but not modify any contents of) kallisto files in the output folder.
