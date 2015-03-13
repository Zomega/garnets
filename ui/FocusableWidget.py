from Widget import Widget

class FocusableWidget( Widget ):

    def __init__( self, model, controller ):
        Widget.__init__( self, model, controller )
        self._focused = False
        self._focus_location = None
        
    ###
    # An override, such that widgets can intentionally ensure they are not
    # focusable. Use sparingly, and make sure there are visual cues.
    ###
    @property
    def focusable( self ):
        return True 
       
    @property
    def focused( self ):
        return self._focused

    @property
    def focus_location( self ):
        return self._focus_location
        
    ###
    # Returns the optimal focus location under the given metric.
    # Focus metrics should have df/dr < 0, i.e. their gradients are
    # well-conditioned to ascent.
    ###
    def best_focus_locations( self, focus_metric ):
        return None
    
    ###
    # Give focus to the widget at the designated location.
    # If the location is invalid, then an InvalidFocusLocationException may be raised.
    ###    
    def give_focus( self, location ):
        self._focus_location = location # TODO: Validate?
        self._focused = True
        
    ###
    # Revoke focus to the widget.
    ###        
    def revoke_focus( self ):
        self._focused = False
