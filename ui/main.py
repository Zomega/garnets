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
controller = Controller(model)
widget = CompositeWidget(model, controller)

widget.add( MissionTimer(model, controller), (0,0), (200,200) )
widget.add( ArtificialHorizon(model, controller), (15,8), (200,200) )
widget.add( Altimeter(model, controller), (55,7), (200,200) )
widget.add( HeadingIndicator(model, controller), (15,30), (200,200) )
widget.add( Throttle(model, controller), (0,8), (200,200) )

with CursesApplication( model, widget, controller ) as app:
    app.run()
