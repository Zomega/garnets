from Widget import *

from Canvas import *
from AsciiCanvas import *

from Event import *
from EventType import *

class Button(Widget):
    def __init__( self, text, action ):
        self.text = text
        self.action = action
        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Checkboxes only support AsciiCanvases for now...")
        c_width, c_height = canvas.size
        if c_height < 1 or c_width < len( self.text ) + 4:
            raise InvalidCanvasSizeError("Label was the wrong size!")
        
    def handle_event( self, event ):
        return False
        
    def render( self ):
        self.canvas.putstr( (0,0), "[ " + self.text + " ]" )
