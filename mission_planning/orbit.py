from math import sqrt, pi, asin

class Orbit:
    def __init__( self, periapsis, apoapsis, body ):
        assert periapsis <= apoapsis
        self.periapsis = periapsis
        self.apoapsis = apoapsis
        self.body = body
    
    @property
    def eccentricity( self ):
         return ( self.apoapsis - self.periapsis ) / ( self.apoapsis + self.periapsis )
         
    @property
    def semimajor_axis( self ):
        return ( self.apoapsis + self.periapsis ) / 2
        
    @property
    def semiminor_axis( self ):
        return sqrt( self.apoapsis * self.periapsis )
        
    @property
    def period( self ):
        return 2 * pi * sqrt( self.semimajor_axis ** 3 / self.body.mu )
    
    @property
    def specific_angular_momentum( self ):
        return sqrt( ( 1 - self.eccentricity ** 2 ) * self.body.mu * self.semimajor_axis )
            
    @property
    def specific_orbital_energy( self ):
        return - self.body.mu / ( 2 * self.semimajor_axis )
