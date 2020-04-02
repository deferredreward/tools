# -*- coding: utf-8 -*-
# This Python 3 script cleans up a few kinds of markdown formatting problems in column 9
# of the TSV tN files. It is only a partial solution.
# When translators alter the number of hash marks, they break the Markdown heading conventions.
# For example, the header jumps from level 1 with level 4 with no level 2 and 3 in between.
# This program intends to eliminate the jumps in heading levels by applying some
# informed guessing as to what the levels should have been. The algorithm is not perfect.
# The goal is to reduce the Errors and Warnings generated by the Door43 page builds
# while restoring the heading levels closer to their intended order.
# Correct operation of the algorithm depends on the consistency of the translator in assigning
# heading levels.
#
# This script also removes leading spaces from the first markdown header in each row.
# Also removes double quotes that surround lines that should begin with just a markdown header.
# Adds space after markdown header hash marks, if missing.
#
# This script was written for TSV notes files.
# Backs up the files being modified.
# Outputs files of the same name in the same location.

import re       # regular expression module
import io
import os
import string
import sys

# Globals
max_files = 999      # How many files do you want to process
source_dir = r'E:\DCS\Malayalam\TN\Mar-20'  # Where are the files located

nProcessed = 0
filename_re = re.compile(r'.*\.tsv$')
hash_re = re.compile(r'(#+) ', flags=re.UNICODE)

# Each inlinekey is matched against each line of a file.
# The matches occur in sequence, so the result of one match impacts the next.
inlinekey = []
inlinekey.append( re.compile(r'\t"(#.*)" *$', flags=re.UNICODE) )
inlinekey.append( re.compile(r'\<br\> +(#.*)$', flags=re.UNICODE) )
inlinekey.append( re.compile(r'#([^# \n].*)', flags=re.UNICODE) )

# Strings to replace with
newstring = []
newstring.append( '\t' )
newstring.append( '<br>' )
newstring.append( '# ' )


def shortname(longpath):
    shortname = longpath
    if source_dir in longpath:
        shortname = longpath[len(source_dir)+1:]
    return shortname

# Calculates and returns the new header level.
# Updates the truelevel list.
def shuffle(truelevel, nmarks, currlevel):
    newlevel = currlevel
    if nmarks > currlevel and truelevel[nmarks] > currlevel:
        newlevel = currlevel + 1
    elif truelevel[nmarks] < currlevel:
        newlevel = truelevel[nmarks]
    
    # Adjust the array
    while nmarks > 1 and truelevel[nmarks] > newlevel:
        truelevel[nmarks] = newlevel
        nmarks -= 1
    return newlevel    

# Converts and returns a single line
def convertLine(line):
    currlevel = 0
    truelevel = [0,1,2,3,4,5,6,7,8,9]
    header = hash_re.search(line, 0)
    while header:
        nmarks = len(header.group(1))
        newlevel = shuffle(truelevel, nmarks, currlevel)
        if newlevel != nmarks:
            line = line[0:header.start()] + '#' * newlevel + line[header.end()-1:]
        currlevel = newlevel
        header = hash_re.search(line, header.start() + newlevel + 1)
    return line

# Fixes the heading levels for the specified file.
def fixHeadingLevels(path):
    input = io.open(path, "tr", 1, encoding="utf-8")
    lines = input.readlines()
    input.close()

    bakpath = path + ".orig"
    if not os.path.isfile(bakpath):
        os.rename(path, bakpath)
    output = io.open(path, "tw", buffering=1, encoding='utf-8', newline='\n')
    for line in lines:
        if "##" in line:
            line = convertLine(line)
        output.write(line)
    output.close

# Removes leading spaces from markdown headers.
# Removes double quotes that surround lines that should begin with just a markdown header.
# Adds space after markdown header hash marks, if missing.
def fixSpacing(path):
    input = io.open(path, "tr", 1, encoding="utf-8-sig")
    lines = input.readlines()
    input.close()
    bakpath = path + ".orig"
    if not os.path.isfile(bakpath):
        os.rename(path, bakpath)
    count = 0
    output = io.open(path, "tw", buffering=1, encoding='utf-8', newline='\n')
    for line in lines:
        count += 1
        for i in range(len(inlinekey)):
            while sub := inlinekey[i].search(line):
                line = line[0:sub.start()] + newstring[i] + sub.group(1) + '\n'
        output.write(line)
    output.close
    
# Puts a single .tsv file through all cleanup steps.
def convertFile(path):
    global nProcessed
    
    sys.stdout.write("Processing " + shortname(path) + "\n")
    sys.stdout.flush()
    fixSpacing(path)
    fixHeadingLevels(path)
    nProcessed += 1

# Recursive routine to convert all files under the specified folder
def convertFolder(folder):
    global nProcessed
    global max_files
    if nProcessed >= max_files:
        return
    sys.stdout.write(shortname(folder) + '\n')
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isdir(path) and entry[0] != '.':
            convertFolder(path)
        elif filename_re.match(entry):
            convertFile(path)
        if nProcessed >= max_files:
            break

# Processes all .txt files in specified directory, one at a time
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != 'hard-coded-path':
        source_dir = sys.argv[1]

    if source_dir and os.path.isdir(source_dir):
        convertFolder(source_dir)
        sys.stdout.write("Done. Processed " + str(nProcessed) + " files.\n")
    elif os.path.isfile(source_dir):
        convertByLine(source_dir)
        sys.stdout.write("Done. Processed 1 file.\n")
    else:
        sys.stderr.write("Usage: python tsv_cleanup.py <folder>\n  Use . for current folder.\n")
