from IML import construct_widgets
from CursesApplication import CursesApplication

from Model import Model
from Controller import Controller

model = Model()
controller = Controller(model)
widget = construct_widgets( 'toggle.iml', model, controller )

with CursesApplication( model, widget, controller ) as app:
    app.run()
