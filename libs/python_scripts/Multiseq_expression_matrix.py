try:
   import  sys, re, csv, traceback
   from os import path, _exit, rename

   import logging.handlers
   from optparse import OptionParser, OptionGroup

   from libs.python_modules.utils.Utility import  combine_reads, generate_matrix
   from libs.python_modules.utils.sysutil import pathDelim
   from libs.python_modules.utils.multiseq_utils import fprintf, printf, eprintf,  exit_process
   from libs.python_modules.utils.sysutil import getstatusoutput


except:
     print(""" Could not load some user defined  module functions""")
     print(""" Make sure your typed 'source Multiseqsrc'""")
     print(""" """)
     print(traceback.print_exc(10))
     sys.exit(3)

PATHDELIM=pathDelim()

usage = sys.argv[0] + """ --preprocess_dir <preprocess_dir> --alignment_dir <alignment_dir> --expression_mat_dir <exp_mat_dir""" +\
                      "-s <sample>  -b <barcodes>"

parser = None
def createParser():
    global parser
    epilog = """This script is used for """

    epilog = re.sub(r'\s+',' ', epilog)

    parser = OptionParser(usage=usage, epilog=epilog)

    # Input options

    param_group =  OptionGroup(parser, 'expression matrix  parameters')


    param_group.add_option('--preprocess_dir', dest='preprocess_dir',  default=None,
                           help='preprocess files dir  [REQUIRED]')

    param_group.add_option('--alignment_dir', dest='alignment_dir',  default=None,
                           help='alignment files dir  [REQUIRED]')

    param_group.add_option('--expression_mat_dir', dest='expression_mat_dir',  default=None,
                           help='expression matrix dir  [REQUIRED]')

    param_group.add_option('-s', '--sample', dest='sample_name', default=None,
                           help='sample name [REQUIRED]')

    param_group.add_option('-b', '--barcodes', dest='extracted_barcodes', default=None,
                           help='file containing the barcodes [REQUIRED]')

    param_group.add_option("-g", "--gene-annot", dest="gene_annotation_file",  default=None,
                      help='the gene annotation file [REQUIRED]')

    parser.add_option_group(param_group)


def main(argv, errorlogger = None, runcommand = None, runstatslogger = None):
    global parser

    options, args = parser.parse_args(argv)

    gene_on_symbol_bed = options.expression_mat_dir + PATHDELIM + options.sample_name + ".gene_on_symbol.bed"
    (code, message) = _execute_bedtools_intersect(
                            options.alignment_dir + PATHDELIM + options.sample_name + ".bed",
                            options.preprocess_dir + PATHDELIM + options.sample_name + ".gene_anno_symbol.bed",
                            gene_on_symbol_bed,
                            additional_params="-wo | sort -k 4,4 - "
                        )

    gene_on_cds_bed = options.expression_mat_dir + PATHDELIM + options.sample_name + ".gene_on_cds.bed"
    (code, message) = _execute_bedtools_intersect(
                            options.alignment_dir + PATHDELIM + options.sample_name + ".bed",
                            options.preprocess_dir + PATHDELIM + options.sample_name + ".gene_anno_cds.bed",
                            gene_on_cds_bed,
                            additional_params="-c | sort -k 4,4 -  "
                        )

    gene_on_3utr_bed = options.expression_mat_dir + PATHDELIM + options.sample_name + ".gene_on_3utr.bed"
    (code, message) = _execute_bedtools_intersect(
                            options.alignment_dir + PATHDELIM + options.sample_name + ".bed",
                            options.preprocess_dir + PATHDELIM + options.sample_name + ".gene_anno_3utr.bed",
                            gene_on_3utr_bed,
                            additional_params="-c  | sort -k 4,4 -"
                        )

    gene_on_5utr_bed = options.expression_mat_dir + PATHDELIM + options.sample_name + ".gene_on_5utr.bed"
    (code, message) = _execute_bedtools_intersect(
                            options.alignment_dir + PATHDELIM + options.sample_name + ".bed",
                            options.preprocess_dir + PATHDELIM + options.sample_name + ".gene_anno_5utr.bed",
                            gene_on_5utr_bed,
                            additional_params="-c | sort -k 4,4 - "
                        )
    gene_on_TTSdis_bed = options.expression_mat_dir + PATHDELIM + options.sample_name + ".gene_on_TTSdis.bed"
    (code, message) = _execute_bedtools_intersect(
                            options.alignment_dir + PATHDELIM + options.sample_name + ".bed",
                            options.preprocess_dir + PATHDELIM + options.sample_name + ".gene_anno_TTSdis.bed",
                            gene_on_TTSdis_bed,
                            additional_params="-c | sort -k 4,4 -"
                        )

    # sample_down_transform_sam(options.samout, bedout, samout_sampledown, bedout_sampledown, 5000000, options.q30filter)
    # cmd1 = "bedtools intersect -a %s -b %s  -wo   | sort -k 4,4 - >  %s" % (
    # conf_dict['General']['bed'], annotation_dir + conf_dict['General']['outname'] + '_gene_anno_symbol.bed',
    # conf_dict['General']['outname'] + '_on_symbol.bed')
    # cmd2 = "bedtools intersect -a %s -b %s -c | sort -k 4,4 - > %s" % (
    # conf_dict['General']['bed'], annotation_dir + conf_dict['General']['outname'] + '_gene_anno_cds.bed',
    # conf_dict['General']['outname'] + '_on_cds.bed')
    # cmd3 = "bedtools intersect -a %s -b %s -c | sort -k 4,4 - > %s" % (
    # conf_dict['General']['bed'], annotation_dir + conf_dict['General']['outname'] + '_gene_anno_3utr.bed',
    # conf_dict['General']['outname'] + '_on_3utr.bed')
    # cmd4 = "bedtools intersect -a %s -b %s -c | sort -k 4,4 - > %s" % (
    # conf_dict['General']['bed'], annotation_dir + conf_dict['General']['outname'] + '_gene_anno_5utr.bed',
    # conf_dict['General']['outname'] + '_on_5utr.bed')
    # cmd5 = "bedtools intersect -a %s -b %s -c | sort -k 4,4 - > %s" % (
    # conf_dict['General']['bed'], annotation_dir + conf_dict['General']['outname'] + '_gene_anno_TTSdis.bed',
    # conf_dict['General']['outname'] + '_on_TTSdis.bed')

    combined_hits_bed = options.expression_mat_dir + pathDelim() + options.sample_name + ".combined.bed"
    try:
       combine_reads(options.extracted_barcodes,
                  gene_on_cds_bed, gene_on_3utr_bed, gene_on_5utr_bed, gene_on_symbol_bed, gene_on_TTSdis_bed,
                  combined_hits_bed, 2)
    except:
        print(traceback.print_exc(10))
        sys.exit(3)


    combined_hits_bed_sorted = options.expression_mat_dir + pathDelim() + options.sample_name + ".combined.sorted.bed"
    cmd = "sort -k 7,7 -k 5,5 %s > %s" % (combined_hits_bed, combined_hits_bed_sorted)
    result = getstatusoutput(cmd)

    qcmatrix = options.expression_mat_dir + pathDelim() + options.sample_name + ".qcmatrix.txt"
    expmatrix =  options.expression_mat_dir + pathDelim() + options.sample_name + ".expmatrix.txt"
    qcmatrix_full = options.expression_mat_dir + pathDelim() + options.sample_name + ".qcmatrix_full.txt"

    try:
      generate_matrix(options.gene_annotation_file, combined_hits_bed_sorted, True, qcmatrix_full, qcmatrix, expmatrix, 2, True)
    except:
        print(traceback.print_exc(10))
        sys.exit(3)

    if code != 0:
        a= '\nERROR\tCannot successfully execute\n'
        outputStr =  a

        eprintf(outputStr + "\n")

        if errorlogger:
           errorlogger.printf(outputStr +"\n")
        return code

    return 0


def  _execute_bedtools_intersect(a_arg, b_arg, outfile,  additional_params=""):
    args= [ ]

    args.append( 'bedtools intersect' )
    args += [ "-a", a_arg ]
    args += ["-b", b_arg]
    args += [additional_params]
    args +=  [">", outfile]


    try:
       result = getstatusoutput(' '.join(args) )
    except:
       return (1, "Cannot execute BEDTOOLS successfully")

    return (result[0], result[1])



def Multiseq_expression_matrix(argv, extra_command = None, errorlogger = None, runstatslogger =None):
    if errorlogger != None:
       errorlogger.write("#STEP\tALIGN_READS\n")
    createParser()
    try:
       code = main(argv, errorlogger = errorlogger, runcommand= extra_command, runstatslogger = runstatslogger)
    except:
       #insert_error(4)
       return (0,'')

    return (0,'')

if __name__ == '__main__':
    createParser()
    main(sys.argv[1:])

