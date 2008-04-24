#!/usr/bin/env python

'''
libhooke.py

General library of internal objects and utilities for Hooke.

Copyright (C) 2006 Massimo Sandal (University of Bologna, Italy).
With algorithms contributed by Francesco Musiani (University of Bologna, Italy)

This program is released under the GNU General Public License version 2.
'''



import libhookecurve as lhc

import scipy
import scipy.signal
import scipy.optimize
import scipy.stats
import numpy
import xml.dom.minidom
import os
import string
import csv

HOOKE_VERSION=['0.8.3', 'Seinei', '2008-04-16']
WX_GOOD=['2.6','2.8'] 
    
class PlaylistXML:
        '''
        This module allows for import/export of an XML playlist into/out of a list of HookeCurve objects
        '''
        
        def __init__(self):
            
            self.playlist=None #the DOM object representing the playlist data structure
            self.playpath=None #the path of the playlist XML file
            self.plaything=None
            self.hidden_attributes=['curve'] #This list contains hidden attributes that we don't want to go into the playlist.
        
        def export(self, list_of_hooke_curves, generics):
            '''
            Creates an initial playlist from a list of files.
            A playlist is an XML document with the following syntaxis:
            <playlist>
            <element path="/my/file/path/"/ attribute="attribute">
            <element path="...">
            </playlist>
            '''   
        
            #create the output playlist, a simple XML document
            impl=xml.dom.minidom.getDOMImplementation()
            #create the document DOM object and the root element
            newdoc=impl.createDocument(None, "playlist",None)
            top_element=newdoc.documentElement
            
            #save generics variables
            playlist_generics=newdoc.createElement("generics")
            top_element.appendChild(playlist_generics)
            for key in generics.keys():
                newdoc.createAttribute(key)
                playlist_generics.setAttribute(key,str(generics[key]))
            
            #save curves and their attributes
            for item in list_of_hooke_curves:
                #playlist_element=newdoc.createElement("curve")
                playlist_element=newdoc.createElement("element")
                top_element.appendChild(playlist_element)
                for key in item.__dict__:
                    if not (key in self.hidden_attributes):
                        newdoc.createAttribute(key)
                        playlist_element.setAttribute(key,str(item.__dict__[key]))    
            
            self.playlist=newdoc
            
        def load(self,filename):
            '''
            loads a playlist file
            '''
            myplay=file(filename)
            self.playpath=filename
            
            #the following 3 lines are needed to strip newlines. otherwise, since newlines
            #are XML elements too (why?), the parser would read them (and re-save them, multiplying
            #newlines...)
            #yes, I'm an XML n00b
            the_file=myplay.read()
            the_file_lines=the_file.split('\n')
            the_file=''.join(the_file_lines)
                       
            self.playlist=xml.dom.minidom.parseString(the_file)  
                           
            #inner parsing functions
            def handlePlaylist(playlist):
                list_of_files=playlist.getElementsByTagName("element")
                generics=playlist.getElementsByTagName("generics")
                return handleFiles(list_of_files), handleGenerics(generics)
            
            def handleGenerics(generics):
                generics_dict={}
                if len(generics)==0:
                    return generics_dict
                
                for attribute in generics[0].attributes.keys():
                    generics_dict[attribute]=generics[0].getAttribute(attribute)
                return generics_dict
        
            def handleFiles(list_of_files):
                new_playlist=[]
                for myfile in list_of_files:
                    #rebuild a data structure from the xml attributes
                    the_curve=lhc.HookeCurve(myfile.getAttribute('path'))
                    for attribute in myfile.attributes.keys(): #extract attributes for the single curve
                        the_curve.__dict__[attribute]=myfile.getAttribute(attribute)
                    new_playlist.append(the_curve)
                
                return new_playlist #this is the true thing returned at the end of this function...(FIXME: clarity)
                    
            return handlePlaylist(self.playlist)
            

        def save(self,output_filename):
            '''
            saves the playlist in a XML file.
            '''    
            outfile=file(output_filename,'w')
            self.playlist.writexml(outfile,indent='\n')
            outfile.close()


class HookeConfig:
    '''
    Handling of Hooke configuration file
    
    Mostly based on the simple-yet-useful examples of the Python Library Reference
    about xml.dom.minidom
    
    FIXME: starting to look a mess, should require refactoring
    '''
    
    def __init__(self):
        self.config={}
        self.config['plugins']=[]
        self.config['drivers']=[]
        self.config['plotmanips']=[]
                
    def load_config(self, filename):
        myconfig=file(filename)
                    
        #the following 3 lines are needed to strip newlines. otherwise, since newlines
        #are XML elements too, the parser would read them (and re-save them, multiplying
        #newlines...)
        #yes, I'm an XML n00b
        the_file=myconfig.read()
        the_file_lines=the_file.split('\n')
        the_file=''.join(the_file_lines)
                       
        self.config_tree=xml.dom.minidom.parseString(the_file)  
        
        def getText(nodelist):
            #take the text from a nodelist
            #from Python Library Reference 13.7.2
            rc = ''
            for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                    rc += node.data
            return rc
        
        def handleConfig(config):
            display_elements=config.getElementsByTagName("display")
            plugins_elements=config.getElementsByTagName("plugins")
            drivers_elements=config.getElementsByTagName("drivers")
            workdir_elements=config.getElementsByTagName("workdir")
            plotmanip_elements=config.getElementsByTagName("plotmanips")
            handleDisplay(display_elements)
            handlePlugins(plugins_elements)
            handleDrivers(drivers_elements)
            handleWorkdir(workdir_elements)
            handlePlotmanip(plotmanip_elements)
            
        def handleDisplay(display_elements):
            for element in display_elements:
                for attribute in element.attributes.keys():
                    self.config[attribute]=element.getAttribute(attribute)
                    
        def handlePlugins(plugins):
            for plugin in plugins[0].childNodes:
                try:
                    self.config['plugins'].append(str(plugin.tagName))
                except: #if we allow fancy formatting of xml, there is a text node, so tagName fails for it...
                    pass
        #FIXME: code duplication
        def handleDrivers(drivers):
            for driver in drivers[0].childNodes:
                try:
                    self.config['drivers'].append(str(driver.tagName))
                except: #if we allow fancy formatting of xml, there is a text node, so tagName fails for it...
                    pass
        
        def handlePlotmanip(plotmanips):
            for plotmanip in plotmanips[0].childNodes:
                try:
                    self.config['plotmanips'].append(str(plotmanip.tagName))
                except: #if we allow fancy formatting of xml, there is a text node, so tagName fails for it...
                    pass
        
        def handleWorkdir(workdir):
            wdir=getText(workdir[0].childNodes)
            self.config['workdir']=wdir.strip()
            
        handleConfig(self.config_tree)
        #making items in the dictionary more machine-readable
        for item in self.config.keys():
            try:
                self.config[item]=float(self.config[item])
            except TypeError: #we are dealing with a list, probably. keep it this way.
                try:
                    self.config[item]=eval(self.config[item])
                except: #not a list, not a tuple, probably a string?
                    pass
            except ValueError: #if we can't get it to a number, it must be None or a string
                if string.lower(self.config[item])=='none':
                    self.config[item]=None
                else:
                    pass
                                                
        return self.config
        
        
    def save_config(self, config_filename):
        print 'Not Implemented.'
        pass    


class ClickedPoint:
    '''
    this class defines what a clicked point on the curve plot is
    '''
    def __init__(self):
        
        self.is_marker=None #boolean ; decides if it is a marker
        self.is_line_edge=None #boolean ; decides if it is the edge of a line (unused)
        self.absolute_coords=(None,None) #(float,float) ; the absolute coordinates of the clicked point on the graph
        self.graph_coords=(None,None) #(float,float) ; the coordinates of the plot that are nearest in X to the clicked point
        self.index=None #integer ; the index of the clicked point with respect to the vector selected
        self.dest=None #0 or 1 ; 0=top plot 1=bottom plot
                
        
    def find_graph_coords(self, xvector, yvector):
        '''
        Given a clicked point on the plot, finds the nearest point in the dataset (in X) that
        corresponds to the clicked point.
        '''
                   
        #Ye Olde sorting algorithm...
        index=0
        best_index=0
        best_diff=10^9 #FIXME:hope we never go over this magic number, doing best_diff=max(xvector)-min(xvector) can be better...
        for point in xvector:
            diff=abs(point-self.absolute_coords[0])
            if diff<best_diff:
                best_index=index
                best_diff=diff
            index+=1
            
        self.index=best_index
        self.graph_coords=(xvector[best_index],yvector[best_index])
        return
    
#-----------------------------------------
#CSV-HELPING FUNCTIONS        
        
def transposed2(lists, defval=0):
    '''
    transposes a list of lists, i.e. from [[a,b,c],[x,y,z]] to [[a,x],[b,y],[c,z]] without losing
    elements
    (by Zoran Isailovski on the Python Cookbook online)
    '''
    if not lists: return []
    return map(lambda *row: [elem or defval for elem in row], *lists)
        
def csv_write_dictionary(f, data, sorting='COLUMNS'):
    '''
    Writes a CSV file from a dictionary, with keys as first column or row
    Keys are in "random" order.
    
    Keys should be strings
    Values should be lists or other iterables
    '''
    keys=data.keys()
    values=data.values()
    t_values=transposed2(values)
    writer=csv.writer(f)

    if sorting=='COLUMNS':
        writer.writerow(keys)
        for item in t_values:
            writer.writerow(item)
        
    if sorting=='ROWS':
        print 'Not implemented!' #FIXME: implement it.


#-----------------------------------------        
                    
def debug():
    '''
    debug stuff from latest rewrite of hooke_playlist.py
    should be removed sooner or later (or substituted with new debug code!)
    '''
    confo=HookeConfig()
    print confo.load_config('hooke.conf')

if __name__ == '__main__':
    debug()