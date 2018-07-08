#!/usr/bin/python

"""This script run the orf prediction """

try:
   import  sys, re, csv, traceback
   from os import path, _exit, rename

   import logging.handlers
   from optparse import OptionParser, OptionGroup

   from libs.python_modules.utils.sysutil import pathDelim
   from libs.python_modules.utils.multiseq_utils  import fprintf, printf, eprintf,  exit_process
   from libs.python_modules.utils.sysutil import getstatusoutput


except:
     print """ Could not load some user defined  module functions"""
     print """ Make sure your typed 'source Multiseqrc'"""
     print """ """
     print traceback.print_exc(10)
     sys.exit(3)

PATHDELIM=pathDelim()



def fprintf(file, fmt, *args):
    file.write(fmt % args)

def printf(fmt, *args):
    sys.stdout.write(fmt % args)

usage = sys.argv[0] + """ -r command"""

parser = None
def createParser():
    global parser
    epilog = """This script is used for running a R script to generate the figures."""

    epilog = re.sub(r'\s+',' ', epilog)

    parser = OptionParser(usage=usage, epilog=epilog)

    # Input options

    input_group =  OptionGroup(parser, 'R command')


    input_group.add_option('-i', '--input', dest='input', 
                           metavar='INPUT FOLDER', default=None, help='processed sample-wise folder')

    input_group.add_option('-s', '--samples', dest='samples', default=[], action="append",
                           help='samples to process')

    parser.add_option_group(input_group)


def isFileNonEmpty(options):
    c =0
    with open(options.blast_query, 'r') as fp:
       for line in fp:
         c += 1
         if c >=2:
           return True
    return False

def main(argv, errorlogger = None, runcommand = None, runstatslogger = None):
    global parser

    options, args = parser.parse_args(argv)


    create_data_files(options, logger = errorlogger)


def create_vregion_count_stats(options):
    fastaNamePATT = re.compile(r'>')

    combined = 'combined'
    vregions=[ 'V1', 'V2','V3', 'V4','V5', 'V6','V7', 'V8','V9']
    results = {}
    fastaNamePATT = re.compile(r'>')


    for s in options.samples:
       results[s] = []
       for v in vregions:
           input_results_vregions_dir  = options.input +  PATHDELIM + s + PATHDELIM +  "vregions"  
           input_file = input_results_vregions_dir  + PATHDELIM +   s + "." + v + ".fasta"

           with open(input_file, 'r') as fp:
               vcount =0
               for line in fp:
                  if fastaNamePATT.search(line):
                     vcount += 1
               results[s].append(vcount)

   
    s = 'combined'
    output_file  = options.input +  PATHDELIM + s + PATHDELIM +  "results" + PATHDELIM + "vregion_count_stats.txt"

    with open(output_file, 'w') as fout:
      flag=False
      for v in vregions:
         if flag==False:
            flag = True
         else:
            fprintf(fout, "\t") 
         fprintf(fout, "%s",v) 
      fprintf(fout, "\n") 

      for s in options.samples:
         fprintf(fout, "%s",s) 
         for c in results[s]:
            fprintf(fout, "\t%d",c) 
         fprintf(fout, "\n") 

def create_vregion_length_stats(options):
    fastaNamePATT = re.compile(r'>')

    combined = 'combined'
    vregions=[ 'V1', 'V2','V3', 'V4','V5', 'V6','V7', 'V8','V9']
    results = {}
    fastaNamePATT = re.compile(r'>')

    for s in options.samples:
       results[s] = {}
       for v in vregions:
           results[s][v] = []
           input_results_vregions_dir  = options.input +  PATHDELIM + s + PATHDELIM +  "vregions"  
           input_file = input_results_vregions_dir  + PATHDELIM +   s + "." + v + ".fasta"

           with open(input_file, 'r') as fp:
               for line in fp:
                  line = line.strip()
                  if fastaNamePATT.search(line):
                      continue
                  results[s][v].append(len(line))

   
    s = 'combined'
    output_file  = options.input +  PATHDELIM + s + PATHDELIM +  "results" + PATHDELIM + "vregion_length_stats.txt"
    with open(output_file, 'w') as fout:
      for s in options.samples:
         fprintf(fout, "%s\n",s) 
         for v in vregions:
             fprintf(fout, "%s",v) 
             for c in results[s][v]:
                fprintf(fout, "\t%d",c) 
             fprintf(fout, "\n") 

def create_tree_stats(options):
  s = 'combined'
  otu_tree_file  = options.input +  PATHDELIM + s + PATHDELIM +  "results" + PATHDELIM + "otu_tree.txt"
  with open( otu_tree_file, 'w') as fout:
    for level in range(3, 9): 
      for i in range(0, len(options.samples)):
         _B, headers, seen = read_tax_for_sample(options, i, level)

         # at most 50, and the top 50 high counts 
         LIM=25
         cutoff =0 
         if  len(seen) > LIM:
            cutoff = sorted(seen.values(), reverse=True)[LIM] 
         B=[]
         for b in _B: 
           if seen[';'.join(b)] > cutoff:
              B.append(b)

         C = create_the_tree(B, seen)
         if C:
           fprintf(fout, "%s\t%d\t%s\n", headers[i], level,  C)
         #for key, value in seen.iteritems():
         #    print key, value



def read_tax_for_sample(options, i, level):
    commentPATT = re.compile(r'OTU_SAMPLE')
    s = 'combined'
    otu_table_file  = options.input +  PATHDELIM + s + PATHDELIM +  "results" + PATHDELIM + "otu_table.txt"
    B = [] 
    seen = {}
    with open( otu_table_file, 'r') as fin:
       for line in fin:
         fields=[ x.strip() for x in line.strip().split('\t') ]
         
         if commentPATT.search(line):
            headers=[ x.strip() for x in line.strip().split('\t') ]
            continue
         
         if int(fields[i + 1]) == 0 :
            continue

         tax =  fields[-1]
       
         taxsplit = [ x.strip() for x in tax.split(';') ]
         if len(taxsplit) < level -1:
            continue

         taxarray=["root"]
         for j in range(0, level-1):
            taxarray.append(re.sub(r'\s','_',taxsplit[j]) )


         if ';'.join(taxarray) in seen:
            seen[';'.join(taxarray)] += int(fields[i+1])
            continue

         seen[';'.join(taxarray)] = int(fields[i+1])
        
         B.append(taxarray)

    return B, headers[1:], seen


def create_the_tree(B, count):
    S1=[]
    S1.append("(")
    S1.append("root")

    S2=[]

    S2.append(';')
    S2.append(')')
    

    k=0
    s = len(B)
    
    m= [0 for i in range(0, s) ]
    M= [ len(B[i]) for  i in range(0, s) ]
    
     
    while k < s:
       if len(S1)==0:
         break
       c = S1.pop()
    
       if c == '(':
         S2.append(c)
         continue
    
       D={}
       k=0
       seen ={}
       for i in range(0, s):
         if m[i]==M[i]-1:
           k += 1
           continue

         if c == B[i][m[i]]:
            m[i] += 1
            if B[i][m[i]]  in seen:
               continue
              
            if m[i] < M[i] - 1:
                 D[B[i][m[i]]]= True
            else:
               if S2[-1]!=')':
                  S2.append(',')
               S2.append("\'" + B[i][m[i]] + "_(" + str(count[';'.join(B[i])]) + ")\'"  )
            seen[B[i][m[i]]]= True

       if len(D)>0:
         S1.append('(')
         for d in D:
            S1.append(d)
    
         if S2[-1]!=')':
              S2.append(',')
         S2.append(')')
    
    S3= [ x for x in reversed(S2) ]
    if len(S3)==2:
       return '';

    return ' '.join(S3)
   

def  create_data_files(options, logger = None):

    create_vregion_count_stats(options)
    create_vregion_length_stats(options)

    create_tree_stats(options)


def Multiseq_create_figures(argv, extra_command = None, errorlogger = None, runstatslogger =None): 
    if errorlogger != None:
       errorlogger.write("#STEP\tFUNC_SEARCH\n")
    createParser()
    try:
       code = main(argv, errorlogger = errorlogger, runcommand= extra_command, runstatslogger = runstatslogger)
    except:
       insert_error(4)
       return (0,'')

    return (0,'')

if __name__ == '__main__':
    createParser()
    main(sys.argv[1:])

