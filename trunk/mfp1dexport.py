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
        self.lines=list(self.filedata.readlines())
        self.filedata.close()
        
        self.filetype='mfp1dexport'
        self.experiment='smfs'
        
    def close_all(self):
        self.filedata.close()
        
    def is_me(self):
        try:
            self.raw_header=self.lines[0:38]
        except:
            #Not enough lines for a header; not a good file
            return False
        
        #FIXME: We want a more reasonable header recognition
        if self.raw_header[0][0:4]=='Wave':
            return True
        else:
            return False
        
    def _read_columns(self):
        
        self.raw_columns=self.lines[39:]
        
        kline=None
        for line in self.lines:
            if line[:7]=='SpringC':
                kline=line
                break
        
        kline=kline.split(':')
        
        #self.k=float(self.raw_header[23][8:])
        self.k=float(kline[1])
        
        
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
        self.data=self._read_columns()
        return self.data[0][1],self.data[1][1]
        
        
    def default_plots(self):   
        main_plot=lhc.PlotObject()
        defl_ext,defl_ret=self.deflection()
        yextforce=[i*self.k for i in defl_ext]
        yretforce=[i*self.k for i in defl_ret]
        main_plot.add_set(self.data[0][0],yextforce)
        main_plot.add_set(self.data[1][0],yretforce)
        main_plot.normalize_vectors()
        main_plot.units=['Z','force']  #FIXME: if there's an header saying something about the time count, should be used
        main_plot.destination=0
        main_plot.title=self.filename
        #main_plot.colors=['red','blue']
        return [main_plot]
