# Basic KSP Aerobraking Calculator
# Based on http://alterbaron.github.io/ksp_aerocalc/

'''
	this.mkPlanet = function(Rmin, Ratm, SOI, mu, H0, P0, Trot) {
		return {
			Rmin: Rmin,	// Equatorial Radius (m)
			Ratm: Ratm+Rmin,	// Atmospheric Height (m) // helps simplify calculations
			SOI: SOI,	// Sphere of influence (m)
			mu: mu,	// Grav. parameter (m3/s2) // kerbal constant
			H0: H0,	// Scale height of atmosphere (m) // P falls off by 1/e for each H0
			P0: P0,	// Pressure at zero altitude (atm)
			Trot: Trot	// Sidereal Rotation Period (s)
		};
	};

	this.Planets = {
		Eve: mkPlanet(700000,96708.574,85109365,8.1717302e12,7000,5,80500),
		Kerbin: mkPlanet(600000,69077.553,84159286,3.5316e12,5000,1,21600),
		Duna: mkPlanet(320000,41446.532,47921949,301363210000,3000,0.2,65517.859),
		Jool: mkPlanet(6000000,138155.11,2455985200,2.82528e14,10000,15,36000),
		Laythe: mkPlanet(500000,55262.042,3723645.8,1.962e12,4000,0.8,52980.879)
	};
'''
from planet import Eve, Kerbin, Duna, Jool, Laythe
from orbit import Orbit

from numpy import cross, vdot
from scipy.linalg import norm
from math import sqrt, sin, cos, asin, acos, atan2
import numpy as np
import scipy.optimize

Planets = [Eve, Kerbin, Duna, Jool, Laythe]

def sign( x ):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


# TODO: use numpy...

# vmult( k, v )
# k * v

# vsum( v, w, ... )
# v + w + ...

# vdiff( v, w )
# v - w

# vnorm( v )
# numpy.linalg.norm( v )

# vdot( v, w )
# numpy.linalg.vdot( v, w )

# vcross2d( v, w )
# numpy.cross( v, w )

# vec2( x, y )
# numpy.array([x, y])

# fzero( f, a, b ) -> 
# scipy.optimize.bisect(f, a, b, xtol = 1e^-5, maxiter = 1000)

def integrate_path( F, m, r0, v0, dt, body ):
    t = 0
    r = r0
    v = v0
    
    def a( rin, vin ):
        return F( rin, vin ) / m
        
    firstrun = True
    
    rold = None
    vold = None
    vest = None
    
    while firstrun or ( norm(r) <= body.r_atm and norm(r) > body.radius ):
        rold = r
        vold = v
        a_t = a( rold, vold )
        
        r = rold + ( dt * vold ) + ( (0.5 * dt**2) * a_t )
        
        vest = vold + (0.5 * dt) * ( a_t + a( r, vold + dt * a_t ) )
        v = vold + (0.5 * dt) * ( a_t + a(r,vest) )
        t += dt
        firstrun = False
		
    return r, v, t
		
#TODO: Port this function
'''
	// Physics integrator
	// Velocity-Verlet with Velocity-dependent forces
	// Terminates once atmosphere is breached OR if impact occurs.
	this.integrate_path = function( F, m, r0, v0, dt, Planet ) {
		var t = 0,
			r = r0,
			v = v0;

		var a = function(rin, vin) { return vmult(1/m, F(rin, vin)); };

		firstrun = true;

		var rold, vold, vest, a_t;

		while (firstrun || (vnorm(r) <= Planet.Ratm && vnorm(r) >= Planet.Rmin)) {
			rold = r;
			vold = v;
			a_t = a(rold, vold);
			r = vsum(rold, vmult(dt, vold), vmult(0.5*dt*dt, a_t));
			vest = vsum(vold, vmult(0.5*dt, vsum(a_t,a(r,vsum(vold,vmult(dt,a_t))))));
			v = vsum(vold, vmult(0.5*dt,vsum(a_t,a(r,vest))));
			t = t + dt;
			firstrun = false;
		}
		return {rf:r, vf:v, tf:t};
	};'''


# TODO: Move this function to the Orbit package.
def get_orbit_params(r, v, body):
    # sp. orbital energy
    ep = vdot(v,v)/2 - body.mu/norm(r)
    # sp. angular momentum
    hmag = cross( r, v )
    
    ec = sqrt(1 + 2 * ep * ( hmag ** 2 )/( body.mu ** 2 ) )
    
    a = - body.mu / ( 2 * ep )
    
    rpe = ( 1 - ec ) * a
    
    rap = ( 1 + ec ) * a
    
    orbit = Orbit( rpe, rap, body )
    
    return orbit
    
def in_atmo_force( drag_coeff, m, A, body, orbitDir ):
    assert body.has_atmosphere
    Kp = 1.2230948554874*0.008
    braking_functions = {
        "prograde":   lambda r, v : v + numpy.array([-2.0*pi/body.T_rot*r[1], 2.0*pi/body.T_rot*r[0]]), # TODO: Simplify more...
        "retrograde": lambda r, v : v - numpy.array([-2.0*pi/body.T_rot*r[1], 2.0*pi/body.T_rot*r[0]]),
        "ignore":     lambda r, v : v
    }
    v_surface = braking_functions[orbitDir]
    
    def F( r, v ):
        F_drag = - ( 0.5 * Kp * body.pressure( norm(r) ) * norm( v_surface(r,v) ) * drag_coeff * m * A ) * v_surface(r,v)
        F_grav = - ( m * body.mu / ( norm(r) ** 3 ) ) * r
        return F_drag + F_grav
    return F
        
'''
	// Net force in atmosphere
	this.in_atmo_force = function(d, m, A, Planet, orbitDir) {
		// Need to consider orbit direction!
		var Kp = 1.2230948554874*0.008,
			braking_functions = {
				"prograde": function(r,v) {return vdiff(v, vmult(-1,[-2.0*Math.PI/Planet.Trot*r[1], 2.0*Math.PI/Planet.Trot*r[0]]))},
				"retrograde": function(r,v) {return vdiff(v, vmult(1,[-2.0*Math.PI/Planet.Trot*r[1], 2.0*Math.PI/Planet.Trot*r[0]]))},
				"ignore": function(r,v) {return v;}
			},
			v_surface = braking_functions[orbitDir];
		return function(r,v) {return vsum(vmult(-0.5*Kp*Planet.P0*Math.exp((Planet.Rmin-vnorm(r))/Planet.H0)*vnorm(v_surface(r,v))*d*m*A, v_surface(r,v)), vmult(-m*Planet.mu/Math.pow(vnorm(r),3), r));};
	};'''


def calc1( dist, vx, vy, d, body, orbitDir ):

    r0 = np.array([dist, 0])
    v0 = np.array([vx, vy])
    dt = 1.0
    m = 1
    A = 1

    rap_out = 0

    inbound_orbit = get_orbit_params( r0, v0, body )

    # Short-circuit tests

    # Check if we will impact the surface neglecting the atmosphere...
    if inbound_orbit.periapsis < body.radius:
        # Impact!
        return body.radius # Technically, this is the apoapse of the new orbit.

    if inbound_orbit.specific_orbital_energy >= 0 and inbound_orbit.periapsis > body.r_atm:
        # Initial hyperbolic (or parabolic) escape
        return body.soi + 1 # Still technically right . . . # TODO: No it's not, this is ridiculus in any other situation. really, both of this and the case below are the same. The orbit is not going to contact the atmosphere, so it will be unchanged.
			
    if inbound_orbit.specific_orbital_energy < 0 and inbound_orbit.periapsis > body.r_atm:
        # Initial orbit is stable
        return inbound_orbit.apoapse
		
    # If we've made it this far, we're hitting the atmosphere without guarantee of impact!

    # Angle from periapsis at which we contact the atmosphere.
    theta_contact = acos( ( 1 / inbound_orbit.eccentricity ) * ( inbound_orbit.semimajor_axis * ( 1 - inbound_orbit.eccentricity ** 2 ) / body.r_atm - 1 ) )

    # Magnitude of velocity when contacting atmosphere
    vcontact_mag = sqrt( 2 * ( inbound_orbit.specific_orbital_energy + body.mu / body.r_atm ) )

    # Use conservation of angular momentum to find angle between velocity and radial position
    theta_1 = asin( inbound_orbit.specific_angular_momentum / (body.r_atm * vcontact_mag) )

    rcontact = body.r_atm * np.array([cos(theta_contact), sin(theta_contact)])

    # The sines and cosines here have been chosen to give the velocity as [vr, vtheta]
    vcontact = vcontact_mag * np.array([-cos(theta_1+theta_contact), -sin(theta_1+theta_contact)])

    F = in_atmo_force( d, m, A, body, orbitDir );

    # Integrate path in atmosphere.
    r_out, v_out, t_out = integrate_path(F, m, rcontact, vcontact, dt, body)

    if norm(r_out) <= body.radius:
        # Impact during braking
        return body.radius
        
    orbit_out =  get_orbit_params(r_out, v_out, body)

    if orbit_out.specific_orbital_energy >= 0:
        # hyperbolic (or parabolic) escape
        return body.soi + 1 # Still technically right . . . # TODO: No it's not, this is ridiculus in any other situation. really, both of this and the case below are the same. The orbit is not going to contact the atmosphere, so it will be unchanged.

    return orbit_out.apoapsis
        
'''
	this.calc1 = function(dist, vx, vy, d, Planet, orbitDir) {
		var r0 = [dist, 0],
			v0 = [vx, vy],
			dt = 1,
			m = 1,
			A = 1;

		var rap_out = 0;

		var p1 = get_orbit_params( r0, v0, Planet );

		// Short-circuit tests
		if (p1.rpe < Planet.Rmin) {
			// Initial suborbital
			rap_out = Planet.Rmin;	// Technically right!
			return rap_out;
		}
		else if (p1.ep >= 0 && p1.rpe > Planet.Ratm) {
			// Initial hyperbolic (or parabolic) escape
			rap_out = Planet.SOI+1;	// Still technically right . . .
			return rap_out;
		}
		else if (p1.ep < 0 && p1.rpe > Planet.Ratm) {
			if (p1.rap < Planet.SOI) {
				// Initial stable, no atmosphere entry
				rap_out = p1.rap;
				return rap_out;
			} else {
				// Initial ep<0 SOI escape
				rap_out = Planet.SOI+1;
				return rap_out;
			}
		}
		// If we've made it this far, we're hitting the atmosphere without guarantee of impact!
		//console.log(Planet);
		// Angle from periapsis at which we contact the atmosphere.
		var theta_contact = Math.acos((1/p1.ec)*(p1.a*(1-p1.ec*p1.ec)/Planet.Ratm-1));

		// Magnitude of velocity when contacting atmosphere
		var vcontact_mag = Math.sqrt(2*(p1.ep+Planet.mu/Planet.Ratm));

		// Use conservation of angular momentum to find angle between velocity and radial position
		var theta_1 = Math.asin(p1.hmag/(Planet.Ratm*vcontact_mag));

		var rcontact = vmult(Planet.Ratm, [Math.cos(theta_contact), Math.sin(theta_contact)]);

		// The sines and cosines here have been chosen to give the velocity as [vr, vtheta]
		var vcontact = vmult(vcontact_mag, [-Math.cos(theta_1+theta_contact), -Math.sin(theta_1+theta_contact)]);

		var F = in_atmo_force( d, m, A, Planet, orbitDir );

		// Integrate path in atmosphere.
		var rvt = integrate_path(F, m, rcontact, vcontact, dt, Planet);
		//console.log(rvt.rf);
		//console.log('Aero-encounter!');
		if (vnorm(rvt.rf) >= Planet.Rmin) {// If not, we've impacted!
			var p2 = get_orbit_params(rvt.rf, rvt.vf, Planet);
			if (p2.ep < 0) {
				rap_out = (1+p2.ec)*p2.a;	// Tentative apoapse distance
				if (rap_out > Planet.SOI) { // Post aerobrake SOI escape!
					rap_out = Planet.SOI+1;
					return rap_out;
				}
				//console.log('Capture!');
			} else {
				rap_out = Planet.SOI+1;	// Parabolic or hyperbolic escape
				//console.log('Escape!');
				return rap_out;
			}
		} else {
			// Impact!
			//console.log('Impact!');
			rap_out = Planet.Rmin;
			return rap_out;
		}
		final_orbit_params = get_orbit_params(rvt.rf, rvt.vf, Planet);
		return rap_out;
	};'''

def calc_pe( r, v, rpe, d, body, orbitDir):
    print r, v, rpe, d
    vy = ( rpe / r ) * sqrt( v ** 2 + 2 * body.mu * ( 1 / rpe - 1/r ) )
    vx = sqrt( v**2 - vy**2 )
    ap = calc1( r, vx, vy, d, body, orbitDir )
    return ap
    
'''// Perform calculations for a given r (scalar), v (scalar), rpe (scalar)
	this.calc_pe = function( r, v, rpe, d, Planet, orbitDir ) {
		var vy = (rpe/r)*Math.sqrt(v*v+2*Planet.mu*(1/rpe-1/r));
		var vx = Math.sqrt(v*v-vy*vy);
		var ap = calc1(r, vx, vy, d, Planet, orbitDir);
		return ap;
	};'''

'''// Allow (optional) use of units.
	this.parseUnitFloat = function(v) {
		var v = v.toLowerCase();
		var value = parseFloat(v);
		if (v.indexOf("mm") !== -1) {
			return value * 1000000;
		} else if (v.indexOf("km") !== -1) {
			return value * 1000;
		} else {
			return value;
		}
	};'''

def solve( r, v, rpe, targ, d, body, orbitDir ):
    assert rpe < r
    vy = ( rpe / r ) * sqrt( v**2 + 2 * body.mu * ( 1 / rpe - 1/r ) )
    vx = sqrt( v**2 - vy**2 )
    
    def apoapsis_error( pe ):
        return calc_pe( r, v, pe, d, body, orbitDir ) - targ
        
    new_periapsis = scipy.optimize.bisect( apoapsis_error, body.radius, body.r_atm, xtol = 1e-5, maxiter = 1000)
    
    #new_vy = ( new_periapsis / r ) * sqrt( v**2 + 2 * body.mu * ( 1 / new_periapsis - 1/r ) )
    #new_vx = sqrt( v**2 - new_vy**2 )
    
    #dv = norm( numpy.array([vx, vy]) - numpy.array([new_vx, new_vy]) )
    #dvtheta = atan2(new_vy-vy,new_vx-vx);
    
'''
	// Main function
	// r is scalar (distance from centre of planet)
	// v is scalar (magnitude of orbital velocity)
	// rpe is scalar (periapse distance)
	// We search for a constant-velocity solution to this problem.
	this.solve = function( r, v, rpe, targ, d, Planet, orbitDir ) {
		var vy = (rpe/r)*Math.sqrt(v*v+2*Planet.mu*(1/rpe-1/r));
		var vx = Math.sqrt(v*v-vy*vy);

		var c_ap = function(pe) {return calc_pe(r,v,pe,d,Planet,orbitDir)-targ};

		var new_pe = fzero(c_ap,Planet.Rmin, Planet.Ratm);

		var vy1 = (new_pe/r)*Math.sqrt(v*v+2*Planet.mu*(1/new_pe-1/r));
		var vx1 = Math.sqrt(v*v-vy1*vy1);

		var dv = vnorm(vdiff([vx1, vy1], [vx, vy]));
		var dvtheta = Math.atan2(vy1-vy,vx1-vx);

		if (isNaN(dv) || isNaN(dvtheta) || isNaN(vnorm([vx1, vy1]))) {
			$('#inputAlt,#inputVel,#inputPE,#inputAP').parent().parent().addClass('error');
			$('#outputPE,#outputDV,#outputAng,#outputVel2,#outputCircDV').val('No Solution!');
			return;
		}

		$('#outputPE').val((new_pe-Planet.Rmin).toFixed(2));
		$('#outputDV').val(dv.toFixed(2));
		$('#outputAng').val((dvtheta*180/Math.PI).toFixed(2));
		$('#outputVel2').val((vnorm([vx1, vy1])).toFixed(2));
		$('#outputCircDV').val((Math.sqrt(Planet.mu/final_orbit_params.rap)-Math.abs(final_orbit_params.hmag / final_orbit_params.rap)).toFixed(2));
	};
	'''

'''
	$('#go').click(function() {

		$('#inputAlt,#inputVel,#inputPE,#inputAP').parent().parent().removeClass('error');

		var Planet = this.Planets[$('#inputBody').val()],
			r = parseUnitFloat($('#inputAlt').val(), 10)+Planet.Rmin,
			v = parseFloat($('#inputVel').val(), 10),
			pe = parseUnitFloat($('#inputPE').val(), 10)+Planet.Rmin,
			orbitDir = $('input[name=inputDir]:radio:checked').val(),
			d = parseFloat($('#inputD').val(), 10),
			target = parseUnitFloat($('#inputAP').val(), 10)+Planet.Rmin;

		solve(r,v,pe,target,d,Planet,orbitDir);
	});'''

dist = 800.0
vx = 0.0
vy = 1.9575

drag_coeff = 0.2

body = Kerbin

orbitDir = "ignore"

print calc1( dist, vx, vy, drag_coeff, body, orbitDir )

# solve( r, v, rpe, targ, d, body, orbitDir )
print solve( 10000.0, 0.2, 660.0, 1000.0, drag_coeff, body, orbitDir )

