from Widget import *

from Canvas import *
from AsciiCanvas import *

from Event import *
from EventType import *

# TODO: Hook this up to the Model instead...

class Label(Widget):
    def __init__( self, text ):
        self.text = text
        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Checkboxes only support AsciiCanvases for now...")
        c_width, c_height = canvas.size
        if c_height < 1 or c_width < len( self.text ):
            raise InvalidCanvasSizeError("Label was the wrong size!")
        
    # TODO the label should never gain focus...
    def handle_event( self, event ):
        return False
        
    def render( self ):
        self.canvas.putstr( (0,0), self.text )
        pass
