"""helper.py: 

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import math

def distance( c1, c2 ):
    return math.sqrt( (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1])**2 )

def overlap( cell1, cell2 ):
    c1, r1 = cell1.center, cell1.radius
    c2, r2 = cell2.center, cell2.radius
    dist = distance(c1, c2)
    sep = (r1 + r2 - dist) / min(r1, r2)
    if sep > 0:
        return False, sep
    return True, sep


def remove_duplicates( cells, newcells = [] ):
    if len(cells) == 0:
        return newcells
    c, rest = cells[0], cells[1:]
    for cc in cells[1:]:
        r1, r2 = sorted( [ c.radius, cc.radius ] )
        dist = distance(c.center, cc.center)
        if not (r1/r2 > 0.95 and dist < 5):
            continue
        elif r1/r2 < 0.95:
            continue
        elif distance(c.center, cc.center) > 3:
            continue
        else:
            newcells.append(c)
    return remove_duplicates( rest, newcells )
