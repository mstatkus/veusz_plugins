# -*- coding: utf-8 -*-
"""
Created on Fri May 25 21:09:14 2018

@author: Mike
"""

#import veusz.plugins as plugins
from veusz.plugins import *


#import logging
#logging.basicConfig(filename=r'd:\Google Drive\scripts\ms-chrom-extract\vsz.log',level=logging.INFO)

class ImportPluginExample(ImportPlugin):
    """An example plugin for reading a set of unformatted numbers
    from a file."""

    name = "MS data import plugin"
    author = "Mike Statkus"
    description = "Imports MS chromatograms from Shimadzu LabSolutions .txt export files"

    # Uncomment this line for the plugin to get its own tab
    promote_tab='MS import'

    file_extensions = set(['.txt'])

    def __init__(self):
        ImportPlugin.__init__(self)
        self.fields = [ImportFieldCheck("zero", descr="Adjust baseline to zero",default = True),
                       ImportFieldCheck("round_MZ", descr="Round MZ values",default=True),
                       ImportFieldCheck("MIC", descr="Import MIC"),
                       ImportFieldCheck("TIC", descr="Import TIC")]

    def open_filename(self,filename):
        f = open(filename,'r')
        raw_data = f.read() # reading whole file as a single string
        f.close()
        return raw_data
    
    def split_to_blocks(self,raw_data,token1='[MS Chromatogram]',token2 = '\n\n'):
        """
        Split raw txt data to blocks; each block starts with token1 and ends with token2 or EOF
        Returns list of strings        
        """
        data = []
        
        pos = 0 # position in the raw data string
        flag = False # flag set if end of file reached 
        while not flag:
            pos_A=raw_data.find(token1,pos) # searching for token1 - start of block
            if pos_A == -1:                 # if token1 not found - quit cycle
                flag = True
            else:
                pos_B=raw_data.find(token2,pos_A)
                
                if pos_B == -1:             #if token2 (explicit block end) not found, take the rest of raw data string
                    pos_B = len(raw_data)
                else:
                    pos = pos_B
                    
                block = raw_data[pos_A:pos_B]
                data.append(block)
        return data
    
    def extract_data_from_block(self,block,skip_lines=7):
        """
        Convert raw text string (one block of data) to dict of lists
        returns dict
        skip_lines - skip header, default = 7
        
        """
    
        lines = block.split('\n') #process block line by line
        chrom = {}
        chrom['title'] = lines[1] #block full title in 2nd line
        dump,chrom['short_title'] = lines[1].rsplit(' ',maxsplit=1) #taking last part of the line which is mz
        
        time = [] # time, minutes
        signal = [] #raw signal
        signal_rel =[] #relative signal
        
        for i in range(skip_lines,len(lines)):
            (t,s,sr) = lines[i].split()
            time.append(float(t))
            signal.append(float(s))
            signal_rel.append(float(sr))
        
        
        
        chrom['time']=time
        chrom['signal']=signal
        chrom['signal_rel']=signal_rel
        signal_zero = [s - min(signal) for s in signal] #baseline adjusted signal
        
        
        chrom['signal_zero'] = signal_zero
        
        return chrom
    
    def process_data_to_chromatograms(self,data):
        """
        Process all blocks of data to chrom dicts
        Returns list of dicts
        """
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
        #logging.info(params.filename)
        raw_data = self.open_filename(params.filename)
        #logging.info('file open ok')
        data = self.split_to_blocks(raw_data)
        #logging.info('splitting ok')
        chromatograms = self.process_data_to_chromatograms(data)
        #logging.info('extract ok')
        
        processed_data = []
        
        zero = params.field_results["zero"]
        MIC = params.field_results["MIC"]
        TIC = params.field_results["TIC"]
        round_MZ = params.field_results["round_MZ"]
        
        for chrom in chromatograms:
            
            prefix = chrom['short_title']
            if ("." in prefix) and round_MZ:
                first,last = prefix.split('.')
                prefix = first
            
            if ("MIC" in prefix) and (not MIC):
                pass
            elif ("TIC" in prefix) and (not TIC):
                pass
            else:
                x = ImportDataset1D(name=prefix+'_time',data = chrom['time'])
                if zero:
                    y = ImportDataset1D(name=prefix+'_signal',data = chrom['signal_zero'])
                else:
                    y = ImportDataset1D(name=prefix+'_signal',data = chrom['signal'])
                processed_data.append(x)
                processed_data.append(y)
        
        return processed_data
  
# add the class to the registry. 
importpluginregistry.append(ImportPluginExample)