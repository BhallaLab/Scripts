#!/usr/bin/env python

"""abf_to_dat.py: 

Convert ABF file to other format.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
import neo.io
import numpy as np

def main( infile ):
    data = neo.io.AxonIO( infile )
    bl = data.read_block(lazy=False, cascade=True)
    print( bl.segments )
    print( bl.segments[0].analogsignals )
    print( bl.segments[0].eventarrays )

if __name__ == '__main__':
    infile = sys.argv[0]
    main( infile )
