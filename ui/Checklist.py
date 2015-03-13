#####
# Checklist
#####
#
# Simple example of a composite Widget
#
#####

from Widget import *

from Canvas import *
from AsciiCanvas import *

from Event import *
from EventType import *

from Label import Label
from Checkbox import Checkbox

class Checklist(Widget):
    def __init__( self, labels ):
        self.pairs = [ ( Checkbox(), Label(text) ) for text in labels ]
        
    def set_canvas( self, canvas ):
        Widget.set_canvas( self, canvas )
        
        for i in range( len( self.pairs ) ):
            self.pairs[i][0].set_canvas( self.canvas.subcanvas(0, i, 3, 1) )
            self.pairs[i][1].set_canvas( self.canvas.subcanvas(4, i, self.canvas.width - 4, 1) )
        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Checkboxes only support AsciiCanvases for now...")
        c_width, c_height = canvas.size
        if c_width < 3 + 1 + 10  or c_height < len(self.pairs): #TODO: Max label size, not 10...
            raise InvalidCanvasSizeError("Checklist need a 3x1 canvas.")
            
    def render( self ):
        for checkbox, label in self.pairs:
            checkbox.render()
            label.render()


