import sys
import pylab
import numpy
import time
import imp
import moose
print "moose path", moose.__path__
loadpath = '/acc92'
moose.loadModel('/home1/ghevar/acc92_caBuff.g',loadpath,'gsl')  
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

moose.reinit()

ca.concInit = ori
moose.start(40)

ca.concInit = 5e-03
moose.start(20)

ca.concInit = ori
moose.start(80) #here give the interval time 

ca.concInit = 5e-03
moose.start(20)

ca.concInit = ori
moose.start(80)

t = numpy.linspace(0.0, moose.element("/clock").runTime, len(table.vector)) # sec
pylab.plot( t, table.vector, label="Ca Conc (interval- 8000s)" )
pylab.legend()

pylab.figure()

t1 = numpy.linspace(0.0, moose.element("/clock").runTime, len(table1.vector)) # sec
pylab.plot( t1, table1.vector, label="Protein Conc (interval- 8000s)" )
pylab.legend()

pylab.show()

dataDir = '_data'
if os.path.exists( dataDir ):
   os.makedirs( dataDir )

print('[INFO] Saving data to csv files')
tabPath1 = '%s.csv' % table.name
numpy.savetxt(tabPath1, numpy.matrix([t, table.vector]).T, newline='\n')
tabPath2 = '%s.csv' % t1.name
numpy.savetxt(tabPath2, numpy.matrix([t1, table1.vector]).T, newline='\n')
