from Widget import *

from Canvas import *
from AsciiCanvas import *

from Event import *
from EventType import *

# TODO: Hook this up to the Model instead...

class Checkbox(Widget):
    def __init__( self ):
        self.checked = False
        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Checkboxes only support AsciiCanvases for now...")
        if not canvas.size == (3,1):
            raise InvalidCanvasSizeError("Checkboxes need a 3x1 canvas.")
        
    def handle_event( self, event ):
        if event.type == EventType.MOUSE_LEFT_CLICK:
            self.checked = not self.checked
            return True
        return False
        
    def render( self ):
        self.canvas.putchr( (0,0), '[' )
        self.canvas.putchr( (2,0), ']' )
        if self.checked:
            self.canvas.putchr( (1,0), 'X' )
        else:
            self.canvas.putchr( (1,0), ' ' )
