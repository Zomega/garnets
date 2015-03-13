###############################################################################
# IML UTILITIES
###############################################################################
#
# This file contains the utilities needed to create interfaces from
# IML (Interface Markup Language) files, which are typically stored as *.iml.
#
# Note that IML is a very loose specification -- it's function is to provide a
# concise way to store and modify widgets layouts, not to provide portability.
# In particular, in order to function the user must provide
# construct_widgets( ... ) with a dictionary of widget constructing functions,
# which are thin wrappers around widget constructors.
#
# For simplicity of use, the dictionary defaults to a simple package of
# ASCII widgets. 
#
###############################################################################

import xml.etree.ElementTree

###############################################################################
# DEFAULT WIDGET CONSTRUCTOR SET
###############################################################################
# TODO: Make sure this is all sequestered away...

from Label import Label
from DynamicLabel import DynamicLabel
from Button import Button
from CompositeWidget import CompositeWidget

def vstack_constructor( attributes, children, model, controller ):
    return hstack_constructor( attributes, children, model, controller )
    
def hstack_constructor( attributes, children, model, controller ):
    i = 0
    composite = CompositeWidget()
    
    while i < len(children):
        composite.add( children[i], (0,3*i), (30,3*i + 3) )
        i += 1
    return composite    
    
def vsep_constructor( attributes, children, model, controller ):
    return Label( '-vsep-' )

def hsep_constructor( attributes, children, model, controller ):
    return Label( '-hsep-' )

def label_constructor( attributes, children, model, controller ):
    return Label( attributes['text'] )
    
def dlabel_constructor( attributes, children, model, controller ):
    return DynamicLabel( model, attributes['contents'], int( attributes['maxlen'] ) )
    
def button_constructor( attributes, children, model, controller ):
    return Button( attributes['text'], attributes['action'] )
    
_default_widget_dict = {
    'vstack' : vstack_constructor,
    'hstack' : hstack_constructor,
    'vsep'   : vsep_constructor,
    'hsep'   : hsep_constructor,
    'label'  : label_constructor,
    'dlabel' : dlabel_constructor,
    'button' : button_constructor
}

###############################################################################
# CORE FUNCTION
###############################################################################

def construct_widgets( filename, model, controller, widget_dict = None ):
    if widget_dict == None:
        widget_dict = _default_widget_dict
        
    def construct_widget( node ):
        w_type = node.tag
        
        if not w_type in widget_dict:
            raise InvalidTagError("Unable to construct widget relating to \"" + w_type + "\", no such constructor function.")
        
        children = [ construct_widget( child ) for child in node ]
        
        attributes = node.attrib
        
        constructor = widget_dict[ w_type ]
        return constructor( attributes, children, model, controller )
    
    tree = xml.etree.ElementTree.parse(filename)
    root = tree.getroot()
    
    root_widget = construct_widget( root )
    return root_widget
