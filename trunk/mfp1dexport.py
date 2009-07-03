#!/usr/bin/env python

'''
mfp1dexport.py

Driver for text-exported MFP 1D files

Massimo Sandal (c) 2009
'''

import libhookecurve as lhc
import libhooke as lh

class mfp1dexportDriver(lhc.Driver):
    
    def __init__(self, filename):
        
        self.filename=filename
        self.filedata=open(filename,'rU')
        
        lines=list(self.filedata.readlines())
        self.raw_header=lines[0:38]
        self.raw_columns=lines[39:]
        self.filedata.close()
        
        self.data=self._read_columns()
        
        self.k=float(self.raw_header[22][16:])
        
        #print self.k
        self.filetype='mfp1dexport'
        self.experiment='smfs'
        
    def close_all(self):
        self.filedata.close()
        
    def is_me(self):
        #FIXME: We want a more reasonable header recognition
        if self.raw_header[0][0:4]=='Wave':
            return True
        else:
            return False
        
    def _read_columns(self):
        xext=[]
        xret=[]
        yext=[]
        yret=[]
        for line in self.raw_columns:
            spline=line.split()
            xext.append(float(spline[0]))
            yext.append(float(spline[1]))
            xret.append(float(spline[2]))
            yret.append(float(spline[3]))
            
        return [[xext,yext],[xret,yret]]
        
    def deflection(self):
        return self.data[0][1],self.data[1][1]
        
        
    def default_plots(self):   
        main_plot=lhc.PlotObject()
        
        yextforce=[i*self.k for i in self.data[0][1]]
        yretforce=[i*self.k for i in self.data[1][1]]
        main_plot.add_set(self.data[0][0],yextforce)
        main_plot.add_set(self.data[1][0],yretforce)
        main_plot.normalize_vectors()
        main_plot.units=['Z','force']  #FIXME: if there's an header saying something about the time count, should be used
        main_plot.destination=0
        main_plot.title=self.filename
        #main_plot.colors=['red','blue']
        return [main_plot]
