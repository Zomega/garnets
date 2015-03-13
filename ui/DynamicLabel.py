from Widget import *

from Canvas import *
from AsciiCanvas import *

from Event import *
from EventType import *

# TODO: Hook this up to the Model instead...

class DynamicLabel(Widget):
    def __init__( self, model, attribute, maxlen ):
        self.maxlen = maxlen
        
        self.model = model
        self.attribute = attribute
        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Checkboxes only support AsciiCanvases for now...")
        c_width, c_height = canvas.size
        if c_height < 1 or c_width < self.maxlen:
            raise InvalidCanvasSizeError("Label was the wrong size!")
        
    # TODO the label should never gain focus...
    def handle_event( self, event ):
        return False
        
    def render( self ):
        self.canvas.putstr( (0,0), getattr(self.model, str(self.attribute)) )
