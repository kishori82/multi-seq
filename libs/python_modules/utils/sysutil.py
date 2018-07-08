import sys, os, re, gzip
from datetime import date


def os_type():

    x = sys.platform
    if x:

        hits = re.search(r'darwin', x, re.I)
        if hits :
          return 'mac'
        
        hits = re.search(r'win', x, re.I)
        if hits :
          return 'win'

        hits = re.search(r'linux', x, re.I)
        if hits:
          return 'linux'


def pathDelim():
    ostype = os_type()
    if ostype == 'win':
        return "\\"

    if ostype in ['linux', 'mac']:
        return "/"


def getstatusoutput(cmd):
    """Return (status, output) of executing cmd in a shell."""
    pipe = os.popen(cmd + ' 2>&1', 'r')
    text = pipe.read()
    sts = pipe.close()
    if sts is None: sts = 0
    if text[-1:] == '\n': text = text[:-1]
    return sts, text



def open_file(filename, perm, compress=False, tag = ''):
   try:
     gzPATT = re.compile(r'[.]gz$')
     if compress and  not gzPATT.search(filename):
         filename = filename + ".gz"
         perm = perm + 'b'

     if compress:
        fh = gzip.open(filename + tag, perm)
     else:
        fh = open(filename + tag, perm)
   except:
      raise IOError("ERROR: Cannot open file %s with permission %s" %(filename, perm) )

   return fh, filename


def open_file_read(filename):
   try:
     gzPATT = re.compile(r'[.]gz$')
     if gzPATT.search(filename):
        fh = gzip.open(filename, 'rb')
     else:
        if os.path.exists(filename):
           fh = open(filename, 'r')
        elif os.path.exists(filename + '.gz'):
           fh = gzip.open(filename + '.gz', 'rb')
        else:
           raise IOError("ERROR: Cannot open file %s to read" %(filename) )
   except:
      raise IOError("ERROR: Cannot open file %s to read" %(filename) )

   return fh
