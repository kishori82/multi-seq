#!/usr/bin/env python




"""Contains general utility code for the metapaths project"""

try:
    from shutil import rmtree
    from StringIO import StringIO
    from os import getenv, makedirs, path, remove
    from operator import itemgetter
    from os.path import abspath, exists, dirname, join, isdir
    from collections import defaultdict
    from optparse import make_option
    from glob import glob
    import sys, os, traceback, shutil, gzip, re

    from libs.python_modules.utils.fastareader  import FastaReader
    from libs.python_modules.utils.sysutil import pathDelim
except:
    print """ Could not load some user defined  module functions"""
    print """ Make sure your typed \'source RiboCensusrc\'"""
    print """ """
    print traceback.print_exc(10)
    sys.exit(3)

def fprintf(file, fmt, *args):
   file.write(fmt % args)
   
   

def printf(fmt, *args):
   sys.stdout.write(fmt % args)
   sys.stdout.flush()
 
def eprintf(fmt, *args):
   sys.stderr.write(fmt % args)
   sys.stderr.flush()

PATHDELIM = pathDelim()


def isMultiNodeFile(filename):
    ''' checks if a fasta file is a nucleotide file format'''
    MultiNodePATT = re.compile(r'_[0-9]+$')
    fastaNamePATT = re.compile(r'^>')

    try:
      c = 0
      t = 0
      with open(filename) as fp:
        for line in fp:
          '''trim the line'''
          line_trimmed = line.strip()
          if line_trimmed:
             if fastaNamePATT.search(line_trimmed):
                t += 1
                if MultiNodePATT.search(line_trimmed):
                  c += 1
          if t > 500:
            break;
    except:
       eprintf("ERROR:\tCannot open file " + filename)
       return False

    if c==t: 
       return True;
    
    return False;


def isVregionFile(filename):
    ''' checks if a fasta file is a nucleotide file format'''
    VregionPATT = re.compile(r'V[0-9]')
    fastaNamePATT = re.compile(r'^>')


    try:
      c = 0
      t = 0
      with open(filename) as fp:
        for line in fp:
          '''trim the line'''
          line_trimmed = line.strip()
          if line_trimmed:
             if fastaNamePATT.search(line_trimmed):
               t += 1
               if VregionPATT.search(line_trimmed):
                  c += 1
          if t > 500:
            break
    except:
       eprintf("ERROR:\tCannot open file " + filename)
       return False

    if c==t: 
       return True;

    return False;





def remove_files(dir, filenames):
   for file in filenames:
      try:
        if path.exists(dir + PATHDELIM + file):
         remove(dir + PATHDELIM + file)
      except IOError:
         print "Cannot remove file  " + dir + PATHDELIM + file + " !"
         sys.exit(0)


# (Re)create the sequence blocks along with the necessary log files 
def create_splits(outputdir, listfilename, input_filename, maxMBytes,   maxSize, splitPrefix = 'split', splitSuffix=''):
     maxBytes = 1024*1024*maxMBytes
     if splitSuffix:
        suffix = '.' + splitSuffix
     else:
        suffix = ''

     try:
        if path.exists( listfilename):
           listfile = open( listfilename, 'r')
           listfilenames = [ x.strip() for x in listfile.readlines() ]
           remove_files(outputdir, listfilenames)
           listfile.close()
     except IOError:
        print "Cannot read file " +  listfilename + " !"
        sys.exit(0)

     try:
        listfile = open(listfilename, 'w')
     except IOError:
        print "Cannot read file " + listfilename + " !"
        sys.exit(0)


     fragments= []
     seq_beg_pattern = re.compile(">")
     splitno = 0
     currblocksize = 0
     currblockbyteSize = 0

     fastareader = FastaReader(input_filename)
     # Read sequences from sorted sequence file and write them to block files

     for name in fastareader:
           fragments.append(fastareader.seqname) 
           fragments.append(fastareader.sequence)

           if currblocksize >= maxSize -1 or currblockbyteSize >= maxBytes:
               splitfile = open(outputdir +  PATHDELIM + splitPrefix + str(splitno) + suffix, 'w')
               fprintf(splitfile, "%s",'\n'.join(fragments))
               fragments=[]
               splitfile.close()
                # Add this block name to the blocklistfile
               fprintf(listfile, "%s\n", splitPrefix + str(splitno) + suffix)
               splitno += 1
               currblocksize = 0
               currblockbyteSize = 0
           else: 
               currblocksize += 1
               currblockbyteSize += len(fastareader.sequence)


     if fragments:
        splitfile = open(outputdir +  PATHDELIM + splitPrefix + str(splitno) + suffix, 'w')
        fprintf(splitfile, "%s",'\n'.join(fragments))
        splitfile.close()
        fragments = []
        fprintf(listfile, "%s\n", splitPrefix + str(splitno) + suffix)
        splitno += 1

     #Add this block name to the blocklistfile
     currblocksize = 0
     currblockbyteSize = 0

     listfile.close()
     return True

def countNoOfSequencesInFile(file):
    fastareader = FastaReader(file)
    count = 0
    for record in fastareader:
       count+=1
    return count

def number_of_lines_in_file(filename):
     
     try:  
         file = open(filename, 'r')
         lines = file.readlines()
         file.close()
         size = len(lines)
     except:   
         return 0
         
     return size

def  read_one_column(listfilename, dictionary, col=0) :
  try:
    listfile = open(listfilename, 'r')
    lines = listfile.readlines()
    for line in lines:
       fields = [ x.strip() for x in line.strip().split('\t') ]
       if len(fields) > col:
          dictionary[fields[col]] = True
    listfile.close()
  except:
    traceback.print_exc(1)

def  enforce_number_of_fields_per_row(listfilename, col):
  needsSanitization = False
  try:
    listfile = open(listfilename, 'r+')
    lines = listfile.readlines()
    for line in lines:
       fields = [ x.strip() for x in line.strip().split('\t') if len(x.strip())  ]
       if len(fields) !=  col:
         needsSanitization = True

    if needsSanitization: 
       listfile.seek(0) 
       listfile.truncate()
    
       for line in lines:
          fields = [ x.strip() for x in line.strip().split('\t') if len(x.strip()) ]
          if len(fields) == col:
            fprintf(listfile, line)

    listfile.close()
  except:
    traceback.print_exc(1)

  return  needsSanitization


# if the the folder is found all the files
# in the folder and but DO NOT  delete the folder 
def clearFolderIfExists(folderName):
    if path.exists(folderName) :
       files = glob(folderName)
       for  f in files:
         remove(f)

# if folder does not exist then create one
def createFolderIfNotFound( folderName ):
    if not path.exists(folderName) :
        makedirs(folderName)
        return False
    else:
        return True 
 
# does folder does ?
def doesFolderExist( folderName ):
    if not path.exists(folderName) :
        return False
    else:
        return True

# does file exist ?
def doesFileExist( fileName ):
    if not path.exists(fileName) :
        return False
    else:
        return True


def read_list(listfilename, dictionary, col=0) :
  """ Read the contents of a file into a dictionary (col begin with 0) """
  try:
    listfile = open(listfilename, 'r')
    lines = listfile.readlines()
    for line in lines:
       fields = [ x.strip() for x in line.strip().split('\t') ]
       if len(fields) > col:
        dictionary[fields[0]] = fields[col]
    listfile.close()
  except:
    traceback.print_exception()

def hasInput(expected_input):
    """ checks if the expected input, a file or folder is present"""
    if  path.exists(expected_input):
        return True 
    else:
        return False

def sQuote(string):
    """ Puts double quotes around a string"""
    return "\'" + string + "\'"



def shouldRunStep1(run_type, dir , expected_outputs):
    """ decide if a command should be run if it is overlay,
        when the expected outputs are present """
    if  run_type =='overlay'  and  doFilesExist(expected_outputs, dir =  dir):
        return False
    else:
        return True


def shouldRunStep(run_type, expected_output):
    """ decide if a command should be run if it is overlay,
      when results are alread computed decide not to run """
    if  run_type =='overlay'  and  path.exists(expected_output):
        return False
    else:
        return True

def hasResults(expected_output):
    """ has the results to use """
    if  path.exists(expected_output):
        return True
    else:
        return False


def hasResults1(dir , expected_outputs):
    """ has the results to use """
    if  doFilesExist(expected_outputs, dir =  dir):
        return True
    else:
        return False

def shouldRunStepOnDirectory(run_type, dirName):
    """if the directory is empty then there is not precomputed results
        and so you should decide to run the command
    """
    dirName = dirName + PATHDELIM + '*'
    files = glob(dirName)
    if len(files)==0:
      return True
    else:
      return False

def removeDirOnRedo(command_Status, origFolderName):
    """ if the command is "redo" then delete all the files
        in the folder and then delete the folder too """
    if command_Status=='redo' and path.exists(origFolderName) :
       folderName = origFolderName + PATHDELIM + '*'
       files = glob(folderName)
       for  f in files:
         remove(f)
       if path.exists(origFolderName):
         shutil.rmtree(origFolderName)

def removeFileOnRedo(command_Status, fileName):
    """ if the command is "redo" then delete the file """
    if command_Status=='redo' and path.exists(fileName) :
        remove(fileName)
        return True
    else:
        return False


def cleanDirOnRedo(command_Status, folderName):
    """ remove all the files in the directory on Redo """
    if command_Status=='redo':
       cleanDirectory(folderName)


def cleanDirectory( folderName):
    """ remove all the files in the directory """
    folderName = folderName + PATHDELIM + '*'
    files = glob(folderName)
    for  f in files:
       remove(f)

def checkOrCreateFolder( folderName ):
    """ if folder does not exist then create one """
    if not path.exists(folderName) :
        makedirs(folderName)
        return False
    else:
        return True

def doFilesExist( fileNames, dir="", gz=False ):
    """ does the file Exist? """
    for fileName in fileNames:
       file = fileName
       if dir!='':
         file = dir + PATHDELIM + fileName
       if not path.exists(file):
         if gz==False or not path.exists(file + ".gz"):
             return False

    return True


def isgzipped(filename):
     patt = re.compile(r'.gz$')

     if patt.search(filename):
        return True
     return False

def open_plain_or_gz(filename, perm):
    if path.exists(filename):
       fh = open(filename, perm)
    else:
       if path.exists(filename + ".gz"):
          fh = gzip.open(filename + ".gz", perm)
       else: 
          fh = None
    return fh

def plain_or_gz_file_exists(filename):
    if path.exists(filename):
        return True
    if path.exists(filename + ".gz"):
        return True
    return False

def Singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance


def createDummyFile(absfilename):
    try:
        f = open(absfilename, 'w')
        f.close()
    except:
        return False

    return True
    #
def sample_name_conflicts(input_list):
    basenames =[]
    namePATT = re.compile(r'^([^.]*)')
    for name in input_list:
       basename = os.path.basename(name)
       res =  namePATT.search(basename)
       if res:
           basenames.append(res.group(1))

    N = len(basenames)
    correct =True

    for i in range(0, N):
       res1 = re.search("_", basenames[i])
       if res1:
          eprintf("ERROR: incorrect sample name \"%s\", with \"_\"\n", basenames[i])
          correct = False

    for i in range(0, N):
      for j in range(i+1, N):

         if basenames[i]==basenames[j]:
            eprintf("ERROR: incorrect sample names \"%s\" and \"%s\", \"%s\" is the same as \"%s\"\n", name1, name2, name1, name2)
            correct = False

         #res1 = re.match( basenames[i], basenames[j])
         #res2 = re.match( basenames[j], basenames[i])
         #if res1 or res2:
         #   if res1:
         #     name1 = basenames[i] 
         #     name2 = basenames[j] 
         #   else:
         #     name1 = basenames[j] 
         #     name2 = basenames[i] 

         #   eprintf("ERROR: incorrect sample names \"%s\" and \"%s\", \"%s\" is prefix of \"%s\"\n", name1, name2, name1, name2)
         #   correct = False

    return not correct
