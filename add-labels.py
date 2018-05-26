# -*- coding: utf-8 -*-
"""
Created on Fri May 18 20:00:57 2018

@author: Mike
"""

import veusz.plugins as plugins

import logging
logging.basicConfig(filename='vsz.log',level=logging.INFO)

class AddManyLabels(plugins.ToolsPlugin):
    """Add many labels to veusz graph"""
    
    # a tuple of strings building up menu to place plugin on
    menu = ('Add data point labels',)
    # unique name for plugin
    name = 'Add data point labels'

    # name to appear on status tool bar
    description_short = 'Add a list of data point labels'
    # text to appear in dialog box
    description_full = 'Add a list of data point labels'
    
    def __init__(self):
        """Make list of fields."""
        self.fields = [ 
            plugins.FieldWidget("widget", descr="Select graph",
                                default="/"),
            plugins.FieldDataset("xPos", descr="X coordinates for labels"),
            plugins.FieldDataset("yPos", descr="Y coordinates for labels"),
            plugins.FieldDataset("labels", descr="List of labels"),
            ]
        
    def apply(self, interface, fields):
        """Do the work of the plugin.
        interface: veusz command line interface object (exporting commands)
        fields: dict mapping field names to values
        """

        # get the Node corresponding to the widget path given
        graph = interface.Root.fromPath(fields['widget'])
        
        xPos = interface.GetData(fields['xPos'])[0]
        yPos = interface.GetData(fields['yPos'])[0]
        labels = interface.GetData(fields['labels'])[0]
        
        logging.info(labels)
        logging.info(str(labels[0]))
        
        for (x,y,label) in zip (xPos,yPos,labels):
            str_label = str(label)
            graph.Add('label',name=str_label,label=str_label,positioning='axes',xPos=x,yPos=y)
        
plugins.toolspluginregistry.append(AddManyLabels)



















