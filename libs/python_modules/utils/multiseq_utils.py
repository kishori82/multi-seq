#!/usr/bin/env python

__author__ = "Kishori M Konwar"
__copyright__ = "Copyright 2013, RiboCensus"
__credits__ = ["r"]
__version__ = "1.0"
__maintainer__ = "Kishori M Konwar"
__status__ = "Release"


"""Contains general utility code for the multiseq project"""

from shutil import rmtree
from StringIO import StringIO
from os import getenv, makedirs, _exit
from operator import itemgetter
from os.path import split, splitext, abspath, exists, dirname, join, isdir
from collections import defaultdict
from optparse import make_option
from datetime import datetime
from optparse import OptionParser
import sys, os, traceback, math, re, time
from libs.python_modules.utils.utils import *
from libs.python_modules.utils.errorcodes import error_message, get_error_list, insert_error




def halt_process(secs=4, verbose =False):
    time.sleep(secs)

    errors=get_error_list()
    if len(errors)>1:
       insert_error(200)

    if verbose:
      for errorcode in errors.keys():
         eprintf("ERROR:\t%d\t%s\n",errorcode, errors[errorcode])
      
    if len(errors.keys())>1:
        errorcode = 200
        _exit(errorcode)
    elif len(errors.keys())==1:
        errorcode = errors.keys()[0]
        _exit(errorcode)

    _exit(0)

def exit_process(message = None, delay = 0, logger = None):
    if message != None: 
      eprintf("ERROR\t%s", message+ "\n")
      eprintf('ERROR\tExiting the Python code\n')
    if logger:
       logger.printf('ERROR\tExiting the Python code\n')
       logger.printf('ERROR\t' + message + '\n')
    time.sleep(delay)
    _exit(0)


def exit_step(message = None):
    if message != None: 
      eprintf("%s", message+ "\n")

    eprintf("INFO: Exiting the Python code\n")
    eprintf("ERROR\t" + str(traceback.format_exc(10)) + "\n")
    time.sleep(4)
    _exit(0)



def getShortORFId(orfname) :
    #return orfname
    orfNameRegEx = re.compile(r'(\d+_\d+)$')

    pos  = orfNameRegEx.search(orfname)

    shortORFname = "" 
    if pos: 
        shortORFname = pos.group(1)

    return shortORFname


def getShortContigId(contigname):
    contigNameRegEx = re.compile(r'(\d+)$')
    shortContigname = "" 
    pos  = contigNameRegEx.search(contigname)
    if pos: 
        shortContigname = pos.group(1)

    return shortContigname

def ContigID(contigname):
    contigNameRegEx = re.compile(r'^(\S+_\d+)_\d+$')
    shortContigname = "" 
    pos  = contigNameRegEx.search(contigname)
    if pos: 
        shortContigname = pos.group(1)

    return shortContigname


def getSampleNameFromContig(contigname):
    contigNameRegEx = re.compile(r'(.*)_(\d+)$')
    sampleName = "" 
    pos  = contigNameRegEx.search(contigname)
    if pos: 
        sampleName = pos.group(1)

    return sampleName

def strip_taxonomy(product):
   func = re.sub(r'\[[^\[\]]+\]', '', product)
   return func


def getSamFiles(readdir, sample_name):
   '''This function finds the set of fastq files that has the reads'''

   samFiles = []
   _samFiles = glob(readdir + PATHDELIM + sample_name + '.sam')

   if _samFiles:
     samFiles = _samFiles

   return samFiles


def parse_command_line_parameters(script_info, argv):
    print script_info 
    print argv
    opts = []
    return opts

class TreeMissingError(IOError):
    """Exception for missing tree file"""
    pass

class OtuMissingError(IOError):
    """Exception for missing OTU file"""
    pass

class AlignmentMissingError(IOError):
    """Exception for missing alignment file"""
    pass

class MissingFileError(IOError):
    pass

def make_safe_f(f, allowed_params):
    """Make version of f that ignores extra named params."""
    def inner(*args, **kwargs):
        if kwargs:
            new_kwargs = {}
            for k, v in kwargs.items():
                if k in allowed_params:
                    new_kwargs[k] = v
            return f(*args, **new_kwargs)
        return f(*args, **kwargs)
    return inner

def extract_seqs_by_sample_id(seqs, sample_ids, negate=False):
    """ Returns (seq id, seq) pairs if sample_id is in sample_ids """
    sample_ids = {}.fromkeys(sample_ids)

    if not negate:
        def f(s):
            return s in sample_ids
    else:
        def f(s):
            return s not in sample_ids

    for seq_id, seq in seqs:
        sample_id = seq_id.split('_')[0]
        if f(sample_id):
            yield seq_id, seq
            
def split_fasta_on_sample_ids(seqs):
    """ yields (sample_id, seq_id, seq) for each entry in seqs 
    
        seqs: (seq_id,seq) pairs, as generated by MinimalFastaParser
    
    """
    for seq_id, seq in seqs:
        yield (seq_id.split()[0].rsplit('_',1)[0], seq_id, seq)
    return
        



def isarray(a):
    """
    This function tests whether an object is an array
    """
    try:
        validity=isinstance(a,ndarray)
    except:
        validity=False

    return validity



class WorkflowError(Exception):
    pass


def contract_key_value_file(fileName):

     file = open(fileName,'r')
     lines = file.readlines()
     if len(lines) < 20:
        file.close()
        return

     keyValuePairs = {}
     
     for line in lines:
       fields = [ x.strip() for x in line.split('\t') ] 
       if len(fields) == 2:
          keyValuePairs[fields[0]] = fields[1]
     file.close()

     file = open(fileName,'w')
     for key, value in  keyValuePairs.iteritems():
          fprintf(file, "%s\t%s\n",key, value)
     file.close()


class FastaRecord(object):
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence

#    return FastaRecord(title, sequence)
def read_fasta_records(input_file):
    records = []
    sequence=""
    while 1:
         line = input_file.readline()
         if line == "": 
            if sequence!="" and name!="":
               records.append(FastaRecord(name, sequence))
            return  records

         if line=='\n':
            continue

         line = line.rstrip()
         if  line.startswith(">") :
            if sequence!="" and name!="":
               records.append(FastaRecord(name, sequence))

            name = line.rstrip()
            sequence ="" 
         else:
            sequence = sequence + line.rstrip()
    return records

def generate_log_fp(output_dir,
                    basefile_name='',
                    suffix='txt',
                    timestamp_pattern=''):
    filename = '%s.%s' % (basefile_name,suffix)
    return join(output_dir,filename)


     
class WorkflowLogger(object):
    
    def __init__(self,log_fp=None,params=None,multiseq_config=None,open_mode='w'):
        if log_fp:
            self._filename = log_fp
            #contract the file if we have to
            if open_mode=='c':
                try:
                   contract_key_value_file(log_fp)
                except:
                   pass 
                open_mode='a'
            self._f = open(self._filename, open_mode)
            self._f.close()
        else:
            self._f = None

        #start_time = datetime.now().strftime('%H:%M:%S on %d %b %Y')
        self.writemultiseqConfig(multiseq_config)
        self.writeParams(params)

    def get_log_filename(self): 
        return self._filename


    def printf(self, fmt, *args):
        self._f = open(self._filename,'a')
        if self._f:
            self._f.write(fmt % args)
            self._f.flush()
        else:
            pass
        self._f.close()


    def write(self, s):
        self._f = open(self._filename,'a')
        if self._f:
            self._f.write(s)
            # Flush here so users can see what step they're
            # on after each write, since some steps can take
            # a long time, and a relatively small amount of 
            # data is being written to the log files.
            self._f.flush()
        else:
            pass
        self._f.close()
    
    def writemultiseqConfig(self,multiseq_config):
        if multiseq_config == None:
            #self.write('#No multiseq config provided.\n')
            pass
        else:
            self.write('#multiseq_config values:\n')
            for k,v in multiseq_config.items():
                if v:
                    self.write('%s\t%s\n' % (k,v))
            self.write('\n')
            
    def writeParams(self,params):
        if params == None:
            #self.write('#No params provided.\n')
            pass 
        else:
            self.write('#parameter file values:\n')
            for k,v in params.items():
                for inner_k,inner_v in v.items():
                    val = inner_v or 'True'
                    self.write('%s:%s\t%s\n' % (k,inner_k,val))
            self.write('\n')
    
    def close(self):
        end_time = datetime.now().strftime('%H:%M:%S on %d %b %Y')
        self.write('\nLogging stopped at %s\n' % end_time)
        if self._f:
            self._f.close()
        else:
            pass



def ShortenORFId(_orfname, RNA=False) :
    
    ORFIdPATT = re.compile("(\\d+_\\d+)$")
    RNAPATT = re.compile("(\\d+_\\d+_[tr]RNA)$")

    if RNA:
       result =  RNAPATT.search(_orfname)
    else:
       result =  ORFIdPATT.search(_orfname)

    if result:
      shortORFname = result.group(1)
    else:
        return ""
    return shortORFname

def ShortentRNAId(_orfname) :
    ORFIdPATT = re.compile("(\\d+_\\d+_tRNA)$")

    result =  ORFIdPATT.search(_orfname)

    if result:
      shortORFname = result.group(1)
      
    else:
        return ""
    return shortORFname

def ShortenrRNAId(_orfname) :
    ORFIdPATT = re.compile("(\\d+_\\d+_rRNA)$")

    result =  ORFIdPATT.search(_orfname)
    if result:
      shortORFname = result.group(1)
    else:
        return ""
    return shortORFname


def ShortenContigId(_contigname) :
    ContigIdPATT = re.compile("(\\d+)$")

    result =  ContigIdPATT.search(_contigname)

    if result:
      shortContigname = result.group(1)
    else:
        return ""

    return shortContigname

def create_multiseq_parameters(filename, folder):
    """ creates a parameters file from the default """
    default_filename = folder + PATHDELIM + 'resources'+ PATHDELIM + "multiseq_params.txt"
    try:
        filep = open(default_filename, 'r')
    except:
        eprintf("ERROR: cannot open the default  parameter file " + sQuote(default_filename) ) 
        exit_process("ERROR: cannot open the default parameter file " + sQuote(default_filename)) 

    lines = filep.readlines()
    with open(filename, 'w') as newfile:
       for line in lines:
         fprintf(newfile, "%s", line);
         
    filep.close()
    #result['filename'] = filename
    return True


def environment_variables_defined(*variables):
    status=True
    for variable in variables:
       if not variable in variables:
           eprintf("ERROR: Environment variable %s not defined; define it as \"export %s=<value>\"\n" %(variable, variable)) 
           status =False
    return status


def create_multiseq_configuration(filename, folder):
    """ creates a cofiguration file from the default """
    variablePATT = re.compile(r'<([a-zA-Z0-9_]*)>')
    default_filename = folder  + PATHDELIM + 'resources'+ PATHDELIM + "multiseq_config.txt"
    try:
        filep = open(default_filename, 'r')
    except:
        eprintf("ERROR: cannot open the default config file " + sQuote(default_filename) ) 
        exit_process("ERROR: cannot open the default config file " + sQuote(default_filename)) 

    res= [0, '']
    lines = filep.readlines()
    with open(filename, 'w') as newfile:
       for line in lines:
         line = line.strip()
         result = variablePATT.search(line)
         if result:
            VARIABLE=result.group(1)
            if VARIABLE in os.environ:
               line =line.replace( '<'+ VARIABLE + '>', os.environ[VARIABLE])
            else:
               default =""
               if VARIABLE=='MULTISEQ_PATH':
                  default = folder + PATHDELIM

               line = line.replace('<' + VARIABLE + '>', default)
               msg = "ERROR: Setting default value for \"%s\" as \"%s\"" %( VARIABLE, default)
               msg+= "      To set other values :\n"
               msg+= "                       1.  set the shell variable \"%s\"\n" %(VARIABLE)
               msg+= "                       2.  rerun command\n"
               res = [1, msg]
               
         fprintf(newfile, "%s\n", line);
    filep.close()

    if res[0]==1:
       os.remove(filename)

    return res

