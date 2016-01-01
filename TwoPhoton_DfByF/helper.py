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
import logging
logger = logging.getLogger('')

def distance( c1, c2 ):
    return math.sqrt( (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1])**2 )

def compute_overlap( cell1, cell2 ):
    c1, r1 = cell1.center, cell1.radius
    c2, r2 = cell2.center, cell2.radius
    dist = distance(c1, c2)
    sep = (dist - r1 - r2) / min(r1, r2)
    if sep > 0.0:
        return False, sep
    return True, sep


def remove_duplicates( cells, result = [] ):
    cells = sorted( cells, key = lambda x: x.radius )
    if len(cells) <= 1:
        logger.debug("After remove_duplicates: %s" %  (result + cells))
        return result + cells
    temp, c = [],  cells[0]
    result.append(c)
    for cc in cells[1:]:
        r1, r2 =  c.radius, cc.radius  
        dist = distance(c.center, cc.center)
        if not (r1/r2 > 0.95 and dist < 5):
            logger.debug("Not Similar: %s, %s" % (c, cc))
            temp.append(cc)
        elif r1/r2 < 0.95:
            logger.debug("Not Similar: %s, %s" % (c, cc))
            temp.append(cc)
        elif distance(c.center, cc.center) > 3:
            logger.debug("Not Similar: %s, %s" % (c, cc))
            temp.append(cc)
        else:
            logger.debug("Similar: %s, %s" % (c, cc))
            continue 
    return remove_duplicates( temp, result )

def remove_contained_cells( cells, result = [] ):

    if len(cells) <= 1:
        logger.debug("After remove_contained_cells: %s" % (result + cells ))
        return result + cells 
    cells = sorted( cells, key = lambda x : x.radius, reverse = True )
    c = cells[0]
    result.append(c)
    temp = []
    for cc in cells[1:]:
        r1, r2 = c.radius, cc.radius
        isOverlapping, overlap = compute_overlap( c, cc )
        if not isOverlapping:
            temp.append(cc)
        elif overlap > -1.0:
            temp.append(cc)
        else:
            continue
    return remove_contained_cells(temp, result)
    

