#!/bin/bash

# To run the tests type ". run_regtests.sh"
source RiboCensusrc

SAMPLE=zymopure

#SAMPLE=beaver

if [ ! -d regtests/output ]; then
   mkdir regtests/output
else 
   rm -rf regtests/output/*
fi


echo python   RiboCensus.py -i regtests/input -o regtests/output -s ${SAMPLE} -v 1
python   RiboCensus.py -i regtests/input -o regtests/output -s ${SAMPLE} -v 1

exitcode=$?

#exit ${exitcode}

