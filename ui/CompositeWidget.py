from Widget import *
from FocusableWidget import *
from Canvas import *

from EventType import *

class CompositeWidget(FocusableWidget): # TODO: Focus methods...
    def __init__( self, model, controller ):
        Widget.__init__(self, model, controller)
        self.widgets = []
        
        self._focus_loc_map = {} # Keeps track of where widgets have promised focus...
        
    # This is a problem, don't know the paradigm yet...
    def add( self, widget, tl, br ):
        self.widgets.append((widget, tl, br))
        # TODO: Better layout planning

    def set_canvas( self, canvas ):
        for widget, tl, br in self.widgets:
            x, y = tl
            x_, y_ = br
            width = x_ - x
            height = y_ - y
            widget.set_canvas( canvas.subcanvas( x, y, width, height ) )
        self.canvas = canvas
        
    def render( self ):      
        for widget, _, _ in self.widgets:
            widget.render()
            
    def handle_event( self, event ):
        self.revoke_focus()
        if event.type == EventType.MOUSE_CLICK:
            self.widgets[1][0].give_focus( None )
        else:
            self.widgets[0][0].give_focus( None )
            
    ###
    # Focus Arbitration
    ###
    
    @property
    def focusable( self ):
        for widget, _, _ in self.widgets:
            if widget.focusable:
                return True
        return False
        
    @property
    def focused( self ):
        return self.focused_subwidget != None
        
    @property
    def focus_location( self ):
        if self.focused_subwidget != None:
            return self.focused_subwidget.focus_location
        return None
        
    @property
    def focused_subwidget( self ): # TODO: Could rewrite other properties in terms of this...
        for widget, _, _ in self.widgets:
            # Short circuit protects .focused from being called on
            # the wrong widgets...
            if widget.focusable and widget.focused:
                return widget
        return None
        
    def best_focus_locations( self, focus_metric ):
        self._focus_loc_map = {} # Clear out the map...
        
        best_metric = None
        best_locations = []
        for widget in self.widgets:
            if widget.focusable:
                for location in widget.best_focus_locations( focus_metric ): # TODO: Transform metric
                    self._focus_location_map[ location ] = widget
                    metric = focus_metric( location )
                    if best_metric == None or metric >= best_metric:
                        best_metric = metric
                        if metric == best_metric:
                            best_locations.append( location )
                        else:
                            best_locations = [ location ]
        return best_locations

    def give_focus( self, location ):
        if location in self._focus_loc_map:
            # Pass the focus down to the correct widget.
            self._focus_loc_map[ location ].give_focus( location )
        else:
            raise InvalidFocusLocationException( "Possible threading error / did you call best_focus_locations before this?" )
            
    def revoke_focus( self ):
        if self.focused_subwidget != None:
            self.focused_subwidget.revoke_focus()
