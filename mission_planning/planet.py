from math import exp

class CelestialBody:
    def __init__( self, name, mu, radius, parent = None ):
        self.name = name
        
        self.mu = mu
        self.radius = radius
        self.parent = parent
    
class Atmosphere:
    def __init__( self, H0, P0, h_atm ):
    	
    	# h_atm : Atmospheric Height (km)
		# H0    : Scale height of atmosphere (km), P falls off by 1/e for each H0
		# P0    : Pressure at zero altitude (atm)
        self.H0 = H0
        self.P0 = P0
        self.h_atm = h_atm
    
class Planetoid(CelestialBody): # TODO: T_rot not optional.
    def __init__( self, name, mu, alt, inclination, radius, T_rot, soi, parent, atmosphere = None ):
        
        # mu    : Grav. parameter (km3/s2)
        # alt   : ??? TODO
        # inclination   : ??? TODO
        # radius: Radius at equator (km)
        # T_rot : Sidereal Rotation Period (s)
        # soi   : Sphere of influence (km)
        
        CelestialBody.__init__( self, name, mu, radius, parent )
        
        self.atmosphere = atmosphere
        self.alt = alt
        self.inclination = inclination
        
    @property
    def has_atmosphere( self ):
        return self.atmosphere != None
        
    @property
    def r_atm( self ):
        assert self.has_atmosphere
        return self.radius + self.atmosphere.h_atm
        
    def pressure( self, r ):
        assert self.has_atmosphere
        
        if r > self.r_atm:
            return 0
        if r <= self.radius:
            return self.atmosphere.P0 # TODO: Handle impact differently?
        return self.atmosphere.P0 * exp( ( self.radius - r ) / self.atmosphere.H0 )
	
Eve_atm = Atmosphere( h_atm = 96.708574, H0 = 7.0, P0 = 5 )
Kerbin_atm = Atmosphere( h_atm = 69.077553, H0 = 5.0, P0 = 1)
Duna_atm = Atmosphere( h_atm = 41.446532, H0 = 3.0, P0 = 0.2 )
Jool_atm = Atmosphere( h_atm = 138.15511, H0 = 10.0, P0 = 15 )
Laythe_atm = Atmosphere( h_atm = 55.262042, H0 = 4.0, P0 = 0.8 )
	
Kerbol =  CelestialBody( "Kerbol",
            mu = 1167922000,
            radius = 65400 )

# Planets
Moho = Planetoid( "Moho",
            mu = 245.25,
            alt = 5263138.3,
            radius = 250,
            inclination = 7,
            T_rot = None, # TODO
            soi = 11206.449,
            parent = Kerbol )
            
Eve = Planetoid( "Eve",
            mu = 8171.73,
            alt = 9832684.544,
            radius = 700,
            inclination = 2.1,
            T_rot = 80500,
            soi = 85109.364,
            atmosphere = Eve_atm,
            parent = Kerbol )

Gilly = Planetoid( "Gilly",
            mu = 0.008289450,
            alt = 31500,
            radius = 13,
            inclination = 12,
            T_rot = None, # TODO
            soi = 126.123,
            parent = Eve )

Kerbin = Planetoid( "Kerbin",
            mu = 3531.6,
            alt = 13599840.256,
            radius = 600,
            inclination = 0,
            T_rot = 21600,
            soi = 84159.2865,
            atmosphere = Kerbin_atm,
            parent = Kerbol )

Mun = Planetoid("Mun",
            mu = 65.138,
            alt = 12000,
            radius = 200,
            inclination = 0,
            T_rot = None, # TODO
            soi = 2430,
            parent = Kerbin )
                
Minmus = Planetoid("Minmus",
            mu = 1.7658,
            alt = 47000,
            radius = 60,
            inclination = 6,
            T_rot = None, # TODO
            soi = 2247.428,
            parent = Kerbin )

Duna = Planetoid("Duna",
            mu = 301.363,
            alt = 20726155.264,
            radius = 320,
            inclination = 1.85,
            T_rot = 65517.859,
            soi = 47921.949,
            atmosphere = Duna_atm,
            parent = Kerbol )
            
Ike = Planetoid("Ike",
            mu = 18.56837,
            alt = 3200,
            radius = 130,
            inclination = 0.2,
            T_rot = None, # TODO
            soi = 1049.599,
            parent = Duna )

Dres = Planetoid("Dres",
            mu = 21.4845,
            alt = 40839348.203,
            radius = 138,
            inclination = 5,
            T_rot = None, # TODO
            soi = 32832.84,
            parent = Kerbol )

Jool = Planetoid("Jool",
            mu = 282528.0042,
            alt = 68773560.320,
            radius = 6000,
            inclination = 1.3,
            T_rot = 36000,
            soi = 2455985.185,
            atmosphere = Jool_atm,
            parent = Kerbol )

Laythe = Planetoid("Laythe",
            mu = 1962,
            alt = 27184,
            radius = 500,
            inclination = 0,
            T_rot = 52980.879,
            soi = 3723.646,
            atmosphere = Laythe_atm,
            parent = Jool )

Vall = Planetoid("Vall",
            mu = 207.4815,
            alt = 43152,
            radius = 300,
            inclination = 0,
            T_rot = None, # TODO
            soi = 2406.401,
            parent = Jool )

Tylo = Planetoid("Tylo",
            mu = 2825.28,
            alt = 68500,
            radius = 600,
            inclination = 0.025,
            T_rot = None, # TODO
            soi = 10856.51837,
            parent = Jool )

Bop = Planetoid("Bop",
            mu = 2.486835,
            alt = 104500,
            radius = 65,
            inclination = 15,
            T_rot = None, # TODO
            soi = 993.0028,
            parent = Jool )

Pol = Planetoid("Pol",
            mu = 0.227,
            alt = 129890,
            radius = 44,
            inclination = 1.304,
            T_rot = None, # TODO
            soi = 2455985.185,
            parent = Jool )

Eeloo = Planetoid("Eeloo",
            mu = 74.410815,
            alt = 90118858.179,
            radius = 210,
            inclination = 6.15,
            T_rot = None, # TODO
            soi = 119082.94,
            parent = Kerbol )
