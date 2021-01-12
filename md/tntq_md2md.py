# -*- coding: utf-8 -*-
# This script copies a repository of tN or tQ files in .md format to a second location.
# It cleans up the files in these ways:
#    Parses directory names to get the book IDs
#    Specify target output folder.
#    Standardizes the names of book folders in the target folder.
#    Ensures blank lines surrounding markdown headers.
#    Makes a projects.yaml file to be pasted into manifest.yaml.
#    Fixes links of this form [[:en:...]]

# Global variables
source_dir = r'C:\DCS\Kannada\TQ'
target_dir = r'C:\DCS\Kannada\kn_tq.STR'
resource_type = 'tq'
language_code = 'kn'

projects = []

import re
import io
import os
import sys
import codecs
import convert2md
import usfm_verses
import operator

# Parses the specified folder name to extract the book ID.
# These folder names may be generated by tStudio in the form: language_book_tn.
# Return upper case bookId or empty string if failed to retrieve.
def parseBookId(folder):
    bookId = ""
    parts = folder.split('_')
    if len(parts) >= 3:
        bookId = parts[1].upper()
    elif len(parts) == 1 and len(folder) == 3:
        bookId = folder.upper()
        if bookId == "JAM":
            bookId = "JAS"
        elif bookId == "PHL":
            bookId = "PHP"
    return bookId

import json

def getBookId(path):
    bookId = ""
    manifestpath = os.path.join(path, 'manifest.json')
    if os.path.isfile(manifestpath):
        try:
            f = open(manifestpath, 'r')
        except IOError as e:
            sys.stderr.write("   Can't open " + shortname(manifestpath) + "\n")
        else:
            manifest = json.load(f)
            f.close()
            bookId = manifest['project']['id']
    if not bookId:
        bookId = parseBookId( os.path.split(path)[1] )
        if len(bookId) != 3:
            bookId = ""
    return bookId.upper()

# Returns the English book name from usfm_verses
def getBookTitle(id):
    title = ""
    if id:
        title = usfm_verses.verseCounts[id]['en_name']
    return title

# Appends information about the current book to the global projects list.
def appendToProjects(bookId, bookTitle):
    global projects
    title = bookTitle + " translationNotes"
    if resource_type == 'tq':
        title = bookTitle
    project = { "title": title, "id": bookId.lower(), "sort": usfm_verses.verseCounts[bookId]["sort"], \
                "path": "./" + bookId.lower() }
    projects.append(project)

# Sort the list of projects and write to projects.yaml
def dumpProjects():
    global projects
    
    projects.sort(key=operator.itemgetter('sort'))
    path = makeManifestPath()
    manifest = io.open(path, "ta", buffering=1, encoding='utf-8', newline='\n')
    for p in projects:
        manifest.write("  -\n")
        manifest.write("    title: '" + p['title'] + "'\n")
        manifest.write("    versification: ''\n")
        manifest.write("    identifier: '" + p['id'] + "'\n")
        manifest.write("    sort: " + str(p['sort']) + "\n")
        manifest.write("    path: '" + p['path'] + "'\n")
        manifest.write("    categories: []\n")
    manifest.close()

# Returns path of temporary manifest file block listing projects converted
def makeManifestPath():
    return os.path.join(target_dir, "projects.yaml")

# Returns path of .md file in target directory.
def makeMdPath(id, chap, fname):
    mdPath = os.path.join(target_dir, id.lower())
    if not os.path.isdir(mdPath):
        os.mkdir(mdPath)

    mdPath = os.path.join(mdPath, chap)
    if not os.path.isdir(mdPath):
        os.mkdir(mdPath)

    return os.path.join(mdPath, fname)

# Returns True if the specified directory is one with text files to be converted
def isChapter(dirname):
    isChap = False
    if (dirname != '00' and re.match('\d\d\d?$', dirname)) or dirname == "front":
        isChap = True
    return isChap

def shortname(longpath):
    shortname = longpath
    if source_dir in longpath:
        shortname = longpath[len(source_dir)+1:]
    return shortname

# Converts .md file in fullpath location to .md file in target dir.
def convertFile(id, chap, fname, fullpath):
    if os.access(fullpath, os.F_OK):
        mdPath = makeMdPath(id, chap, fname)
        convert2md.md2md(fullpath, mdPath, language_code, shortname)

# This method is called to convert the text files in the specified chapter folder
# It renames files that have only a single digit in the name.
def convertChapter(bookId, dir, fullpath):
    for fname in os.listdir(fullpath):
        if re.match('\d\.md', fname):
            goodPath = os.path.join(fullpath, '0' + fname)
            if not os.path.exists(goodPath):
                badPath = os.path.join(fullpath, fname)
                os.rename(badPath, goodPath)
                fname = '0' + fname
        if (re.match('\d\d\d?\.md', fname) and fname != '00.md') or fname == "intro.md":
            convertFile(bookId, dir, fname, os.path.join(fullpath, fname))

# Determines if the specified path is a book folder, and processes it if so.
# Return book title, or empty string if not a book.
def convertBook(path):
    bookId = getBookId(path)
    bookTitle = getBookTitle(bookId)
    relativepath = shortname(path)
    if bookId and bookTitle:
        nchapters = 0
        for dir in os.listdir(path):
            if isChapter(dir):
                nchapters += 1
                if nchapters == 1:
                    sys.stdout.write("Converting: " + relativepath + "\n")
                    sys.stdout.flush()
                convertChapter(bookId, dir, os.path.join(path, dir))
        if nchapters > 0:
            appendToProjects(bookId, bookTitle)
        else:
            sys.stderr.write("Book folder has manifest but no chapters: " + relativepath + '\n')
    elif relativepath != "" and relativepath.lower() != "content":
        sys.stderr.write("Not identified as a book folder: " + relativepath + '\n')
    return bookTitle
 
# Converts the book or books contained in the specified folder
def convert(dir):
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
    if os.path.isfile( makeManifestPath() ):
        os.remove( makeManifestPath() )
    if not convertBook(dir):
        for directory in os.listdir(dir):
            folder = os.path.join(dir, directory)
            if os.path.isdir(folder) and directory[0] != ".":
                convert(folder)
    dumpProjects()

# Processes each directory and its files one at a time
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != 'hard-coded-path':
        source_dir = sys.argv[1]
    
    if os.path.isdir(source_dir):
        convert(source_dir)
    else:
        sys.stderr.write("Folder not found: " + source_dir)
    print("\nDone.")
