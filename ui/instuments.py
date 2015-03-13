from CursesApplication import CursesApplication

from Controller import Controller
from Model import Model

from CompositeWidget import CompositeWidget
from MissionTimer import MissionTimer
from Altimeter import Altimeter
from ArtificialHorizon import ArtificialHorizon
from HeadingIndicator import HeadingIndicator
from Throttle import Throttle

model = Model()
widget = CompositeWidget()
controller = Controller(model)

widget.add( MissionTimer(model), (0,0), (200,200) )
widget.add( ArtificialHorizon(model), (15,8), (200,200) )
widget.add( Altimeter(model), (55,7), (200,200) )
widget.add( HeadingIndicator(model), (15,30), (200,200) )
widget.add( Throttle(model), (0,8), (200,200) )

with CursesApplication( model, widget, controller ) as app:
    app.run()
