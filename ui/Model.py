###############################################################################
# MODEL
###############################################################################
#
# The Model contains all the information needed to populate the Widgets.
# Models are easy to create:
#
# >>> m_engine = Model('engine')
#
# Models have attributes "registered" with them.
# Attribute names are restricted to avoid conflict with method names.
#
# >>> m_engine.register( 'throttle' )
#
# Once the values of attributes are deep copied and therefore
# cannot and should not be updated except via model methods
#
# >>> m_engine.update( 'throttle', 52.6 )
#
# Reading values, however, is easy.
#
# >>> print m_engine.throttle
# 52.6
#
# It's also possible to "watch" attributes.
#
# >>> throttle_widget = MyThrottleWidget()
# >>> m_engine.watch('throttle', throttle_widget)
#
# Widgets watching an attribute will recive an EventType.MODEL_UPDATE event
# when update is called on the attribute. For more details on this type of
# event, look at the Event documentation.
#
# Models can also have sub-models.
#
# Sub-models must have a unique non-restricted name, but a single model can
# be attached to multiple parent models. Their attributes can be accessed via
# dot indirection.
#
# >>> m_plane = Model('plane')
# >>> m_plane.engine.throttle
# 52.6
#
###############################################################################

class Model:
    def __init__(self):
        self.attrs = {}
        
    def register(self, attr_name):
        self.attrs[ attr_name ] = None
        
    def update(self, attr_name, value):
        if attr_name in self.attrs:
            self.attrs[ attr_name ] = value
        else:
            raise AttributeError(attr_name)   
        
    def __getattr__(self, attr_name):
        if attr_name in  self.attrs:
            return self.attrs[ attr_name ]
        raise AttributeError(attr_name)
    
