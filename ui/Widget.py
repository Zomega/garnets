###############################################################################
# WIDGET
###############################################################################
#
# Try to avoid attributes in Widgets
# unless they are specific to the widget,
# and not the underlying data the widget conveys.
# 
# DO NOT dynamically update Widgets except through the model.
# The exception is that the Controller can interface with
# FrameWidgets to swap out what's contained in them.
#
###############################################################################

from Exceptions import UnhandledEventException

# TODO: Add framework for spacial focus?
class Widget:
    def __init__( self, model, controller ):
        self.model = model
        self.controller = controller
        
    ###
    # An override, such that widgets can intentionally ensure they are not
    # focusable. Use sparingly, and make sure there are visual cues.
    ###
    @property
    def focusable( self ):
        return True
    
    def _min_size( self, paradigm ):
        return None
        
    def _max_size( self, paradigm ):
        return None
        
    def _preferred_size( self, paradigm ):
        return None
        
    @property
    def size( self ):
        return (self._width, self._height)
    
    def _validate_canvas_size( self, canvas ):
        min_size = self._min_size( canvas.paradigm )
        if min_size and ( min_size[0] > canvas.size[0] or min_size[1] > canvas.size[1] ):
            InvalidCanvasSizeError("Something attempted to initialize a widget with too little space.")
            
        max_size = self._max_size( canvas.paradigm )
        if max_size and ( max_size[0] < canvas.size[0] or max_size[1] < canvas.size[1] ):
            InvalidCanvasSizeError("Something attempted to initialize a widget with too much space.")
            
    def set_canvas( self, canvas ):
    
        self._validate_canvas_size( canvas )
        self.validate_canvas( canvas )
        
        self.canvas = canvas
            
    def validate_canvas( self, canvas ):
        raise NotImplementedError("Widget subclasses must implement a validate_canvas method.")
        
    def handle_event( self, event ):
        raise UnhandledEventException()
