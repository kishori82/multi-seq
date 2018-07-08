#!/usr/bin/env python
#file parse.py: parsers for map file, distance matrix file, env file



from string import strip
from collections import defaultdict
from copy import deepcopy
import os, re
import libs.python_modules.utils.globalcodes

from libs.python_modules.utils.multiseq_utils  import parse_command_line_parameters, eprintf, halt_process
from libs.python_modules.utils  import globalcodes


class RiboCensusError(Exception):
    pass



def group_by_field(table, name):
    """Returns dict of field_state:[row_headers] from table.

    Use to extract info from table based on a single field.
    """
    try:
        col_index = table[0].index(name)
    except ValueError, e:
        raise ValueError, "Couldn't find name %s in headers: %s" % \
            (name, table[0])
    result = defaultdict(list)
    for row in table[1:]:
        header, state = row[0], row[col_index]
        result[state].append(header)
    return result

def group_by_fields(table, names):
    """Returns dict of (field_states):[row_headers] from table.

    Use to extract info from table based on combinations of fields.
    """
    col_indices = map(table[0].index, names)
    result = defaultdict(list)
    for row in table[1:]:
        header = row[0]
        states = tuple([row[i] for i in col_indices])
        result[states].append(header)
    return result


def parse_distmat_to_dict(table):
    """Parse a dist matrix into an 2d dict indexed by sample ids.
    
    table: table as lines
    """
    
    col_headers, row_headers, data = parse_matrix(table)
    assert(col_headers==row_headers)
    
    result = defaultdict(dict)
    for (sample_id_x, row) in zip (col_headers,data):
        for (sample_id_y, value) in zip(row_headers, row):
            result[sample_id_x][sample_id_y] = value
    return result
    
def parse_bootstrap_support(lines):
    """Parser for a bootstrap/jackknife support in tab delimited text
    """
    bootstraps = {}
    for line in lines:
        if line[0] == '#': continue
        wordlist = line.strip().split()
        bootstraps[wordlist[0]] = float(wordlist[1])
        
    return bootstraps



def fields_to_dict(lines, delim='\t', strip_f=strip):
    """makes a dict where first field is key, rest are vals."""
    result = {}
    for line in lines:
        #skip empty lines
        if strip_f:
            fields = map(strip_f, line.split(delim))
        else:
            fields = line.split(delim)
        if not fields[0]:   #empty string in first field implies problem
            continue
        result[fields[0]] = fields[1:]
    return result

def parse_multiseq_parameters(filename):
    """ Return 2D dict of params (and values, if applicable) which should be on
    """
    # The qiime_config object is a default dict: if keys are not
    # present, {} is returned
    def return_empty_dict():
        return dict()

    try:
        filep = open(filename, 'r')
    except:
        eprintf("ERROR: cannot open the parameter file " + sQuote(filename) ) 
        exit_process("ERROR: cannot open the parameter file " + sQuote(filename), errorCode = 0 ) 

    result = {}
    
    lines = filep.readlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            fields = line.split()
            try:
                script_id, parameter_id = fields[0].split(':')
                value = ','.join([ x.strip() for x in fields[1:] ])
                value = re.sub(',,',',',value)
                globalcodes.exit_code = 1
            except :
                eprintf("ERROR\tInvalid line %s in file %s\n", line.strip(), filename)
                continue
                
            #if value.upper() == 'FALSE' or value.upper() == 'NONE':
            #    continue
            #elif value.upper() == 'TRUE':
            #    value = None
            #else:
            #    pass
            
            try:
                result[script_id][parameter_id] = value
            except KeyError:
                result[script_id] = {parameter_id:value}
    filep.close()
    #result['filename'] = filename
    return result


def parse_parameter_file(filename):
    """ Return 2D dict of params (and values, if applicable) which should be on
    """
    # The qiime_config object is a default dict: if keys are not
    # present, {} is returned
    def return_empty_dict():
        return dict()
    result = defaultdict(return_empty_dict)
    file = open( filename, 'r')
    lines = file.readlines()
    file.close()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            fields = line.split()
            script_id, parameter_id = fields[0].split(':')
            try:
                value = ' '.join([ x.strip() for x in fields[1:] ])
            except IndexError:
                continue
                
            if value.upper() == 'FALSE' or value.upper() == 'NONE':
                continue
            elif value.upper() == 'TRUE':
                value = None
            else:
                pass
            
            try:
                result[script_id][parameter_id] = value
            except KeyError:
                result[script_id] = {parameter_id:value}
    return result


