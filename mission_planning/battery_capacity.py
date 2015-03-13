# Basic KSP Battery Estimates
# Based on https://docs.google.com/spreadsheets/d/1yHS2LJJ6RAqb6gXNHwoaa8R9ZIqNtbe4ikbQ4e1dcUA/edit#gid=0

from math import sqrt, pi, asin
from planet import Eve, Kerbin, Duna, Jool, Laythe # TODO: add other planets.
                                                  # TODO: Account for planets elipsing the sun for moons?
from orbit import Orbit

h_apoapsis = 3000.0
h_periapsis = 80.0

body = Kerbin

r_apoapsis = h_apoapsis + body.radius
r_periapsis = h_periapsis + body.radius

orbit = Orbit( r_periapsis, r_apoapsis, body )

print orbit.semimajor_axis
print orbit.semiminor_axis
print orbit.eccentricity

print orbit.period

orbit_dark_period_s = ((2*orbit.semimajor_axis*orbit.semiminor_axis)/sqrt(body.mu*(2*(orbit.apoapsis)*(orbit.periapsis)/(orbit.apoapsis+orbit.periapsis))))*(asin(body.radius/orbit.semiminor_axis)+orbit.eccentricity*body.radius/orbit.semiminor_axis)

print orbit_dark_period_s

energy_per_second = 0.21

minimum_battery_capacity = energy_per_second * orbit_dark_period_s

print minimum_battery_capacity
