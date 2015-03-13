from EventType import EventType

# TODO: This is meant to be an abstract class of sorts.
class Event:
    @property
    def type(self):
        return EventType.UNDEFINED
    
class KeypressEvent:
    @property
    def type(self):
        return EventType.KEYPRESS
    def __init__( self, keycode ):
        self.keycode = keycode
        
class MouseClickEvent:
    @property
    def type(self):
        return EventType.MOUSE_CLICK
    def __init__( self, location ):
        self.location = location
