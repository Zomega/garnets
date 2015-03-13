###############################################################################
# CONTROLLER
###############################################################################
#
# Controllers contain program logic and can even swap out widgets at excecution
# time.
#
###############################################################################

import datetime
import time
from math import sin

from Model import Model

# TODO: This is not a flexible controller eidolon.
class Controller:
    def __init__(self, model):
        self.model = model
        self.model.register('time')
        self.model.register('throttle')
        
        self.model.register('mode')
        self.model.update( 'mode', '*' )
        
        self.model.register('above_horizon')
        
        self.model.register('roll')
        self.model.register('pitch')
        self.model.register('yaw')
        
        self.model.register('x')
        self.model.register('y')
        self.model.register('z')
        
    def update(self):
        t = datetime.datetime.now().time()
        self.model.update('time', t.isoformat())
        
        dt = time.time()
        
        throttle = int( 50 * sin( dt / 24 ) + 50 )
        self.model.update('throttle', throttle)
        
        roll = dt / 6
        self.model.update('roll', roll)
        
        above_horizon = int( 10 * sin( dt / 5 ) )
        self.model.update('above_horizon', above_horizon)
        
        x = int( 49 * sin( dt / 25 ) + 50 )
        self.model.update('x', x)
        y = int( 49 * sin( dt / 26 ) + 50 )
        self.model.update('y', y)
        z = int( 49 * sin( dt / 27 ) + 50 )
        self.model.update('z', z)
