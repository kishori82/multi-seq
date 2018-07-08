#!/usr/bin/env python


try:
    import os, re, sys

    from shutil import rmtree
    from optparse import make_option
    from os import path, _exit
  

    from libs.python_modules.utils.multiseq_utils import *
    from libs.python_modules.utils.sysutil import pathDelim
    from libs.python_modules.utils.utils import *
    from libs.python_modules.pipeline.context import *
except:
   print """ Could not load some user defined  module functions"""
   print """ Make sure your typed \"source RiboCensussrc\" """
   import traceback
   print """ """
   print traceback.print_exc(10)
   sys.exit(3)

   
PATHDELIM = pathDelim()


class JobCreator():
      """ This class looks up the steps status redo, yes, skip and decided which steps 
          needs to be added into the job/context list """ 

      params = {}
      configs = {}
      samples = []

      stagesInOrder = []
      def  __init__(self, params, configs):
          self.params = params
          self.configs = configs
          #print self.configs

      # not important
      def addSampleName(self, sample):
          #sample = re.sub("-", "", sample)
          self.samples.append(sample)

      # not important
      def getSamples(self):
          return self.samples 


      def addJobs(self, s, block_mode=False):
          contextCreator = ContextCreator(self.params, self.configs)

          contextBlock = []
          for stageList in contextCreator.getStageLists(s.getType()):
            for stage in stageList: 
               if stage in self.params['multiseq_steps']:
                  contexts = contextCreator.getContexts(s, stage)
                  contextBlock.append(contexts)

          s.addContexts(contextBlock)



@Singleton
class Params:
      params  = {}
      def __init__(self, params):
          self.params = params
          pass

      def get(self, key1, key2 = None, default = None):
          if not key1 in self.params:
              return default

          if key2 == None:
             return self.params[key1]
          
          if not key2 in self.params[key1]:
              return default

          return self.params[key1][key2]

@Singleton
class Configs:
      configs = None 
      def __init__(self, configs):
         for key, value in configs.iteritems():  
             setattr(self, key, value)


@Singleton
class ContextCreator:
      params = None
      configs = None
      factory = {}
      stageList = {}
      samples = []
      format = None

      def _Message(self, str):

          return '{0: <60}'.format(str)

      def setSamples(self, samples):
          self.samples = samples

      def getSamples(self):
          return self.samples

      def preprocess_input_cmd(self, s):
        """ PREPROCESS """
        contexts = []

        context = Context()
        context.name = 'PREPROCESS'

        '''inputs'''
        context.inputs = {
            "barcodes": s.input_files[0],
            "annotations": s.ref_gene_annotations
        }

        '''outputs'''
        context.outputs = {
            "barcode" : s.preprocessed_dir + PATHDELIM + s.sample_name + ".barcodes.txt",
            "barcode_sorted": s.preprocessed_dir + PATHDELIM + s.sample_name + ".barcodes.sorted.txt",
            "gene_anno_3utr": s.preprocessed_dir + PATHDELIM + s.sample_name  + ".gene_anno_3utr.bed",
            "gene_anno_5utr": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_5utr.bed",
            "gene_anno_cds": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_cds.bed",
            "gene_anno_transcript": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_transcript.bed",
            "gene_anno_TTSdis": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_TTSdis.bed",
            "gene_anno_symbol": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_symbol.bed",
            "gene_anno_binexon": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_binexon.bed"
        }

        '''params'''
        context.status = self.params.get('multiseq_steps','PREPROCESS')

        pyscript = self.configs.MULTISEQ_PATH + self.configs.PREPROCESS

        cmd = "%s -g %s  -b %s -o %s -s %s" % (pyscript, context.inputs['annotations'],
                                               context.inputs['barcodes'], s.preprocessed_dir, s.sample_name)

        context.message = self._Message("PREPROCESS\n")
        context.commands = [cmd]
        contexts.append(context)
        return contexts


      def align_reads_cmd(self, s):
            """ ALIGN_READS """

            contexts = []
            context = Context()
            context.name = 'ALIGN_READS'

            '''inputs'''
            context.inputs = {
             'reads': s.input_files[1],
             'index':s.refindex_dir + pathDelim() + s.refindex_name + ".1.bt2"
            }

            '''params'''
            aligner = self.params.get('ALIGNMENT', 'aligner')
            context.status = self.params.get('multiseq_steps', 'ALIGN_READS')
            q30filter = self.params.get('QC', 'q30filter')

            if aligner == 'bowtie2':
                '''outputs'''
                context.outputs = {
                  "samfile": s.alignment_dir + pathDelim()  + s.sample_name + '.sam',
                  "bamfile": s.alignment_dir + pathDelim() + s.sample_name + '.bam',
                  "samfile_sample_down": s.alignment_dir + pathDelim() + s.sample_name + '.sample_down.sam',
                  "bedfile": s.alignment_dir + pathDelim() + s.sample_name + '.bed',
                  "bedfile_sample_down": s.alignment_dir + pathDelim() + s.sample_name + '.sample_down.bed'
                }

                pyscript =  self.configs.ALIGN_READS
                cmd = "%s -p %s -x %s -U %s -S %s" \
                    % (pyscript, self.configs.NUM_PROCS,
                      s.refindex_dir  + pathDelim() + s.refindex_name, s.input_files[1],
                       context.outputs['samfile'])

                if q30filter=='on':
                    cmd += " --q30filter"

                context.message = self._Message("ALIGN_READS : bowtie2\n")
                context.commands = [cmd]
                contexts.append(context)

            return contexts

      def create_expression_matrix_cmd(self, s):
          """ CREATE_EXPRESSION_MATRIX """

          contexts = []
          context = Context()
          context.name = 'CREATE_EXPRESSION_MATRIX'

          '''inputs'''
          context.inputs = {
              "gene_anno_3utr": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_3utr.bed",
              "gene_anno_5utr": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_5utr.bed",
              "gene_anno_cds": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_cds.bed",
              "gene_anno_TTSdis": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_TTSdis.bed",
              "gene_anno_symbol": s.preprocessed_dir + PATHDELIM + s.sample_name + ".gene_anno_symbol.bed",
              "barcodes_sorted": s.preprocessed_dir + PATHDELIM + s.sample_name + ".barcodes.sorted.txt"
          }

          '''params'''
          context.status = self.params.get('multiseq_steps', 'CREATE_EXPRESSION_MATRIX')


          '''outputs'''
          context.outputs = {
              "gene_on_3utr": s.expression_matrix_dir + PATHDELIM + s.sample_name + ".gene_on_3utr.bed",
              "gene_on_5utr": s.expression_matrix_dir + PATHDELIM + s.sample_name + ".gene_on_5utr.bed",
              "gene_on_cds": s.expression_matrix_dir + PATHDELIM + s.sample_name + ".gene_on_cds.bed",
              "gene_on_TTSdis": s.expression_matrix_dir + PATHDELIM + s.sample_name + ".gene_on_TTSdis.bed",
              "gene_on_symbol": s.expression_matrix_dir + PATHDELIM + s.sample_name + ".gene_on_symbol.bed",
              'combined_hits_bed':  s.expression_matrix_dir + pathDelim() + s.sample_name + ".combined.bed",
              "qcmatrix": s.expression_matrix_dir + pathDelim() + s.sample_name + ".qcmatrix.txt",
              "expmatrix":s.expression_matrix_dir + pathDelim() + s.sample_name + ".expmatrix.txt",
              "qcmatrix_full" : s.expression_matrix_dir + pathDelim() + s.sample_name + ".qcmatrix_full.txt"
          }

          pyscript = self.configs.CREATE_EXPRESSION_MATRIX
          cmd = "%s -s %s -b %s --preprocess_dir %s --alignment_dir %s --expression_mat_dir %s -g %s" \
                    % (pyscript, s.sample_name, context.inputs['barcodes_sorted'], s.preprocessed_dir, s.alignment_dir,
                       s.expression_matrix_dir, s.ref_gene_annotations)


          context.message = self._Message("CREATE_EXPRESSION_MATRIX\n")
          context.commands = [cmd]
          contexts.append(context)

          return contexts

      def create_ref_genome_index_cmd(self, s):
          """ CREATE_REF_GENOME_INDEX """
          contexts = []
          context = Context()
          context.name = 'CREATE_REF_GENOME_INDEX'

          '''input'''
          context.inputs = {
              'refseq_genome_sequences': s.ref_genome_sequences
          }

          '''params'''
          aligner = self.params.get('ALIGNMENT','aligner')

          context.status = self.params.get('multiseq_steps','CREATE_REF_GENOME_INDEX')

          if aligner=='bowtie2':
              '''outputs'''
              context.outputs = {
                  'index': s.refindex_dir + pathDelim() + s.refindex_name + ".1.bt2"
              }
              executable_name =  self.configs.BOWTIE2BUILD
              cmd = "%s %s %s" %(executable_name, s.ref_genome_sequences, s.refindex_dir + pathDelim() + s.refindex_name)
              context.message = self._Message("CREATE_REF_GENOME_INDEX : bowtie2\n")
              context.commands = [cmd]
              contexts.append(context)

          return contexts


      def create_figures_cmd(self, s):
          '''CREATE_FIGURES'''

          contexts = []
          Rscript= self.configs.MULTISEQ_PATH + PATHDELIM + self.configs.CREATE_FIGURES

          context = Context()
          context.name = "CREATE FIGURES"
          context.message = self._Message("CREATE_FIGURES\n")
          context.status = self.params.get('multiseq_steps','CREATE_FIGURES')

          context.inputs["expmatrix"]=s.expression_matrix_dir + pathDelim() + s.sample_name + ".expmatrix.txt"
          context.outputs['barcode_rank_plot'] = s.expression_matrix_dir + PATHDELIM + 'barcode_rank_plot.pdf'


          cmd="R CMD BATCH --no-save \'--args %s %s" %(context.inputs['expmatrix'], context.outputs['barcode_rank_plot'])
          cmd = cmd + '\' ' + Rscript + '  /dev/null'

          context.commands = [cmd]
          contexts.append(context)
          return contexts


      def __init__(self, params, configs): 
          self.params = Singleton(Params)(params)
          self.configs = Singleton(Configs)(configs)
          if self.checkConfigFile():
             exit_process()
          self.initFactoryList()
          pass

      def getContexts(self, s, stage):
          stageList  = {}
          for stageBlock in self.stageList[s.getType()]:
            for _stage in  stageBlock:
               stageList[_stage] = True

          
          if stage in stageList:
              return self.factory[stage](s)

      def getStageLists(self, type):
           return self.stageList[type]

      def checkConfigFile(self):
           error = False
           return error
               
      def initFactoryList(self):
           self.factory['PREPROCESS'] = self.preprocess_input_cmd
           self.factory['CREATE_REF_GENOME_INDEX'] = self.create_ref_genome_index_cmd
           self.factory['ALIGN_READS'] = self.align_reads_cmd
           self.factory['CREATE_EXPRESSION_MATRIX'] = self.create_expression_matrix_cmd
           self.factory['CREATE_FIGURES'] = self.create_figures_cmd

           self.stageList['DROP-SEQ'] = [
                             [
                                 'PREPROCESS',
                                 'CREATE_REF_GENOME_INDEX',
                                 'ALIGN_READS',
                                 'CREATE_EXPRESSION_MATRIX',
                                 'CREATE_FIGURES'
                              ]
                           ]

           self.stageList['SMART-SEQ'] = [
                             [


                              ]
                           ]
           self.stageList['CELL-SEQ'] = [
                             [
                              ]
                           ]

           self.stageList['MARS-SEQ'] = [
                             [
                              ]
                           ]




