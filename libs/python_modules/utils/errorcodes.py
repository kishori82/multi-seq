
errorcodes={}
errorcodes[0]="Run completed successfully"
errorcodes[1]="Error during the PREPROCESSING step"
errorcodes[6]="Error during the SCAN_rRNA step"
errorcodes[8]="Error during the ANNOTATION SEQS step"
errorcodes[200]="Multiple errors found run again with \"-v\" or check the \"errors_warnings_log.txt\" for details"
errorcodes[15]="Error while computing refscores"
errorcodes[16]="Error during the CREATE_ANNOT_REPORTS step"


errors={}


def insert_error(i):
   global errors
   global errorcodes

   if i in errorcodes:
      errors[i] = errorcodes[i]
   else:
      errors[i] = "Unknown error"


def error_message(i) :
    global errorcodes
    if i in errorcodes:
       return errorcodes[i]
    return "Unkonwn error"

def get_error_list():
   global errors
   return errors
