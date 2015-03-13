from Widget import Widget
from FocusableWidget import *
from CompositeWidget import CompositeWidget


class FocusWidget(FocusableWidget):
    def __init__(self, model, controller):
        FocusableWidget.__init__(self, model, controller)
        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("ArtificialHorizons only support AsciiCanvases for now...")
        
    def handle_event( self, event ):
        raise UnhandledEventException()
        
    def render( self ):      
        if self.focused:
            self.canvas.paint_rect( (0,0), (self.canvas.size[0]-1,self.canvas.size[1]-1), bg_color = 'Y' )
        else:
            self.canvas.paint_rect( (0,0), (self.canvas.size[0]-1,self.canvas.size[1]-1), bg_color = 'B' )
            
    def best_focus_locations( self, focus_metric ):
        best_metric = None
        best_locations = []
        width, height = self.size
        for x in range(width):
            for y in range(height):
                metric = focus_metric((x,y))
                if best_metric == None or metric >= best_metric:
                    best_metric = metric
                    if metric == best_metric:
                        best_locations.append( (x,y) )
                    else:
                        best_locations = [(x,y)]
        return best_locations
                    
            
from CursesApplication import CursesApplication

from Controller import Controller
from Model import Model

model = Model()
controller = Controller(model)
widget = CompositeWidget(model, controller)

widget.add( FocusWidget(model, controller), (0,0), (10,10) )
widget.add( FocusWidget(model, controller), (11,11), (21,21) )
widget.add( FocusWidget(model, controller), (0,11), (10,21) )
widget.add( FocusWidget(model, controller), (11,0), (21,10) )

with CursesApplication( model, widget, controller ) as app:
    app.run()
            
