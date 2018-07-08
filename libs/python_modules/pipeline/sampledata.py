#!/usr/bin/env python



try:
    import os, re, sys, traceback

    from shutil import rmtree
    from optparse import make_option
    from os import path, _exit

    from libs.python_modules.utils.multiseq_utils import *
    from libs.python_modules.utils.sysutil import pathDelim
    from libs.python_modules.utils.utils import *
except:
    print "Cannot load some modules"
    print """ Make sure your typed \"source RiboCensusrc\""""
    print """ """
    print traceback.print_exc(10)
    sys.exit(0)
   
PATHDELIM = pathDelim()


class SampleData():
    """Contains the sample related data """

    runlogger = None
    stepslogger = None
    errorlogger = None
    runstatslogger = None

    def __init__(self):
      self.input_files = None
      self.output_dir = None

      self.preprocessed_dir = None
      self.run_statistics_dir = None
      self.output_results = None

      self.stages = []
      self.stages_context = {}
      self.sample_names = []


      pass

    #not important
    def setSampleNames(self, names):
        for name in names:
            sample_name = extractSampleName(name)

    def getContexts(self):
        contexts = []
        for name in self.stages:
           if name in self.stages_context:
              contexts.append( self.stages_context[name] )
        return contexts

    def getContextBlocks(self):
        contextBlocks  =[]

        for block in self.stages:
          contexts = []
          for name in block:
             if name in self.stages_context:
                 contexts.append( self.stages_context[name] )
          contextBlocks.append(contexts)

        return contextBlocks
    #not important
    def numJobs(self):
        return len(self.stages)

    def clearJobs(self):
       self.stages = []
       self.stages_context = {}

    # not so important
    def extractSampleName(self, inputFile):
        input_file = inputFile
        sample_name = re.sub(r'[.][a-zA-Z]*$','',input_file)
        sample_name = path.basename(sample_name)
        sample_name = re.sub('[.]','_',sample_name)
        return sample_name

    def setInputOutput(self, inputFiles = None, output_dir = None):
        if inputFiles == None and output_dir == None:
            return False
        self.input_files = inputFiles

        self.output_dir = output_dir
        self.sample_dir = self.output_dir + PATHDELIM + self.sample_name
        self.preprocessed_dir = self.output_dir + PATHDELIM + self.sample_name + PATHDELIM + "preprocessed" + PATHDELIM
        self.run_statistics_dir = self.output_dir +  PATHDELIM + self.sample_name + PATHDELIM + "statistics"  +PATHDELIM
        self.alignment_dir =  self.output_dir +  PATHDELIM + self.sample_name +  PATHDELIM + "alignment"  + PATHDELIM
        self.expression_matrix_dir = self.output_dir +  PATHDELIM + self.sample_name + PATHDELIM + "expression_matrix" + PATHDELIM


    def setParameter(self,  parameter, value):
        setattr(self, parameter, value)

    def prepareToRun(self):
        self._createFolders()
        self._createLogFiles()


    def getType(self):
        if hasattr(self, 'PROTOCOL_NAME') and self.PROTOCOL_NAME=='DROP-SEQ':
            return self.PROTOCOL_NAME
        else:
            return None

        if not hasattr(self, 'FILE_TYPE'):
           return None

        return 'UNKNOWN'


    def _createLogFiles(self):
        self.runlogger = WorkflowLogger(generate_log_fp(self.output_dir, basefile_name='multiseq_run_log'), open_mode='a')
        self.stepslogger = WorkflowLogger(generate_log_fp(self.output_dir, basefile_name='multiseq_steps_log'),open_mode='a')
        self.errorlogger = WorkflowLogger(generate_log_fp(self.output_dir, basefile_name='errors_warnings_log'),open_mode='a')
        self.runstatslogger = WorkflowLogger(generate_log_fp(self.run_statistics_dir,  basefile_name = 'run.stats'),open_mode='a')

    def _createFolders(self):
      if self.PROTOCOL_NAME=='DROP-SEQ':
        checkOrCreateFolder(self.sample_dir)
        checkOrCreateFolder(self.preprocessed_dir)
        checkOrCreateFolder(self.run_statistics_dir)
        checkOrCreateFolder(self.alignment_dir)
        checkOrCreateFolder(self.expression_matrix_dir)

    # not important
    def addPipeLineStage(self, stepName, inputs= [], outputs = [], status = 'yes'):
        stagecontext = Context()
        stagecontext.inputs  = inputs
        stagecontext.outputs = outputs
        stagecontext.name= stepName
        stagecontext.status = context

        stages_context[stepName] = stagecontext

    def addContextBlock(self, contextBlock):
          self.contextBlock.append(contextBlock)

    def addContexts(self, contextBlock):
        stages = []
        for contexts in contextBlock:
           for context in contexts:
              stages.append(context.name)
              self.stages_context[context.name] = context

        self.stages.append( stages)

