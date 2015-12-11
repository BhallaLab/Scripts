import sys
import pylab
import numpy
import time
import math
import imp
import moose
import os
import datetime

print "moose path", moose.__path__
dataDir = '_data'
stamp = datetime.datetime.now().isoformat()

dataDir = os.path.join( dataDir, stamp )
if not os.path.exists( dataDir ):
    os.makedirs( dataDir )


loadpath = '/acc92'

def main( runTime ):
    try:
        moose.delete('/acc92')
        print("Deleted old model")
    except Exception as  e:
        print("Could not clean. model not loaded yet")

    moose.loadModel('acc92_caBuff.g',loadpath,'gsl')  
    ca = moose.element(loadpath+'/kinetics/Ca')
    pr = moose.element(loadpath+'/kinetics/protein')
    clockdt = moose.Clock('/clock').dts 
    moose.setClock(8, 0.1)#simdt
    moose.setClock(18, 0.1)#plotdt
    print clockdt
    print " \t \t simdt ", moose.Clock('/clock').dts[8],"plotdt ",moose.Clock('/clock').dts[18]
    ori =  ca.concInit
    tablepath = loadpath+'/kinetics/Ca'
    tableele = moose.element(tablepath)
    table = moose.Table2(tablepath+'.con')
    x = moose.connect(table, 'requestOut', tablepath, 'getConc')
    tablepath1 = loadpath+'/kinetics/protein'
    tableele1 = moose.element(tablepath1)
    table1 = moose.Table2(tablepath1+'.con')
    x1 = moose.connect(table1, 'requestOut', tablepath1, 'getConc')

    ca.concInit = ori
    print("[INFO] Running for 4000 with Ca.conc %s " % ca.conc)
    moose.start(4000)

    ca.concInit = 5e-03
    print("[INFO] Running for 20 with Ca.conc %s " % ca.conc)
    moose.start(20)

    ca.concInit = ori
    moose.start( runTime ) #here give the interval time 

    ca.concInit = 5e-03
    print("[INFO] Running for 20 with Ca.conc %s " % ca.conc)
    moose.start(20)

    ca.concInit = ori
    print("[INFO] Running for 2000 with Ca.conc %s " % ca.conc)
    moose.start(2000)

    pylab.figure()
    pylab.subplot(2, 1, 1)
    t = numpy.linspace(0.0, moose.element("/clock").runTime, len(table.vector)) # sec
    pylab.plot( t, table.vector, label="Ca Conc (interval- 8000s)" )
    pylab.legend()
    pylab.subplot(2, 1, 2)
    t1 = numpy.linspace(0.0, moose.element("/clock").runTime, len(table1.vector)) # sec
    pylab.plot( t1, table1.vector, label="Protein Conc (interval- 8000s)" )
    pylab.legend()
    pylab.savefig( os.path.join( dataDir, '%s_%s.png' % (table1.name, runTime) ) )

    print('[INFO] Saving data to csv files in %s' % dataDir)
    tabPath1 = os.path.join( dataDir, '%s_%s.csv' % (table.name, runTime))
    numpy.savetxt(tabPath1, numpy.matrix([t, table.vector]).T, newline='\n')
    tabPath2 = os.path.join( dataDir, '%s_%s.csv' % (table1.name, runTime) )
    numpy.savetxt(tabPath2, numpy.matrix([t1, table1.vector]).T, newline='\n')

if __name__ == '__main__':
    for x in numpy.linspace( 10, 2000, 20 ):
        print("Running for %s sec" % x)
        main(x)
