# -*- coding: utf-8 -*-
"""
Created on Fri May 25 21:09:14 2018

@author: Mike
"""

#import veusz.plugins as plugins
from veusz.plugins import *


import logging
logging.basicConfig(filename=r'd:\Google Drive\scripts\ms-chrom-extract\vsz.log',level=logging.INFO)

class ImportPluginExample(ImportPlugin):
    """An example plugin for reading a set of unformatted numbers
    from a file."""

    name = "MS import plugin2"
    author = "Mike"
    description = "MS import plugin2"

    # Uncomment this line for the plugin to get its own tab
    promote_tab='MS import'

    file_extensions = set(['.txt'])

    def __init__(self):
        ImportPlugin.__init__(self)

    def open_filename(self,filename):
        f = open(filename,'r')
        raw_data = f.read() # reading whole file as a single string
        f.close()
        return raw_data
    
    def split_to_blocks(self,raw_data,token1='[MS Chromatogram]',token2 = '\n\n'):
        data = []
        
        pos = 0
        flag = False
        while not flag:
            pos_A=raw_data.find(token1,pos)
            if pos_A == -1:
                flag = True
            else:
                pos_B=raw_data.find(token2,pos_A)
                if pos_B == -1:
                    pos_B = len(raw_data)
                    flag = True
                else:
                    pos = pos_B
            if not flag:
                block = raw_data[pos_A:pos_B]
                data.append(block)
        return data
    
    def extract_data_from_block(self,block,skip_lines=7):
    
        lines = block.split('\n')
        chrom = {}
        chrom['title'] = lines[1]
        dump,chrom['short_title'] = lines[1].rsplit(' ',maxsplit=1) #taking last part of the line which is mz
        
        time = []
        signal = []
        signal_rel =[]
        
        for i in range(skip_lines,len(lines)):
            (t,s,sr) = lines[i].split()
            time.append(float(t))
            signal.append(float(s))
            signal_rel.append(float(sr))
        
        
        
        chrom['time']=time
        chrom['signal']=signal
        chrom['signal_rel']=signal_rel
        signal_zero = [s - min(signal) for s in signal]
        
        
        chrom['signal_zero'] = signal_zero
        
        return chrom
    
    def process_data_to_chromatograms(self,data):
        chromatograms = []
        for block in data:
            chrom = self.extract_data_from_block(block)
            chromatograms.append(chrom)
        return chromatograms   
        

    def doImport(self, params):
        """Actually import data
        params is a ImportPluginParams object.
        Return a list of ImportDataset1D, ImportDataset2D objects
        """
        logging.info(params.filename)
        raw_data = self.open_filename(params.filename)
        logging.info('file open ok')
        data = self.split_to_blocks(raw_data)
        logging.info('splitting ok')
        chromatograms = self.process_data_to_chromatograms(data)
        logging.info('extract ok')
        
        processed_data = []
        
        for chrom in chromatograms:
            prefix = chrom['short_title']
            t = ImportDataset1D(name=prefix+'_t',data = chrom['time'])
            sz = ImportDataset1D(name=prefix+'_sz',data = chrom['signal_zero'])
            processed_data.append(t)
            processed_data.append(sz)
        
        return processed_data


    
# add the class to the registry. An instance also works, but is deprecated
importpluginregistry.append(ImportPluginExample)