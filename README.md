# Garnets

Moderately Believable Planetary Systems, baked fresh daily.

Port of the StarGen Stellar System Generator from C to Python3. Focus on enhancing readability and extensibility. The name is an Anagram of the original.

# StarGen -- On the Shoulders of Giants

Garnets directly owes its existence to an earlier program, Jim Burrows' StarGen, which itself has a complicated lineage.

## What is StarGen?

To quote the author:

> StarGen is ... a program for creating moderately believable planetary systems around stars
> other than our own. The most recent version runs on Macintosh and Unix machines and produces
> HTML files as output.

## Why port StarGen?

There are a couple reasons.

### StarGen is hard to integrate into other systems.

It outputs HTML, which is not really ideal as an interchange format. It's also set up as a stand-alone program, and it's not very easy to adapt into a library.

### StarGen is difficult to read and extend.

As Burrows mentions, StarGen was at least 15 years old in 2004, and borrowed code and concepts from as early as the 1970s.

Taken together, StarGen has a lot of code baggage, and there are places where it shows. There are (to me at least) arcane tuning variables, there are a lot of weird unit conversions and choices (some parts use cgs, others stick to AUs, others km).

### StarGen produces some results that do not match the best experimental data.

* Hot Jupiters
* Collisions between bodies can produce important results.
  * Venus spins the wrong way
  * Earth's moon is massive compared to expectations -- belived to be the result of a collision between two rocky proto-planets.

## Inclusion of StarGen Code:
Some StarGen code is included as a reference while I'm doing the initial porting. Since StarGen is MIT Licensed, this in on the up and up. :)

# Goals of Garnets

## Match StarGen functionality

Pretty self explanatory -- garnets should do what Stargen does.

## Refactor into modules

By nature of the way it's organized, StarGen is not very modular. I want to break out, for instance, the atomspheric simulation into it's own module, and the orbit calculation into another.

## Clean up the units

Right now, the units are a right mess, and I'm not confident everything is working right. I intend ot use `natu` to clean up the units and ensure that there are no more messy conversion factors hanging around.

## Add basic n-body simulation and collision handling.

There are multiple places in our own solar system where we see the effects of gravitational interactions. In particular:

* Jupiter has strong gravitational effects on asteroids and comets in the inner solar system, acting to "vaccum" eccentric objects away.
* Jupiter and other planets shape where smaller bodies like asteriods congregate using their lagrange points and resonances (see Kirkwood gaps).
* Jupiter likely prevented the formation of a planet from the materials in the asteroid belt.
* Three of Jupiter's Galilean moons are locked into resonant orbits, which stabilizes them.
* Hot Jupiters exist -- our current understanding is that these planets started their lives further out, and through interactions with other planets, they fell inward towards their stars.

I'd like to replace the current proto-planet subroutine with a quick simulation of the protoplanets actually encountering each other, perhaps by using rebound.

In addition, I want to add some postprocessing to allow the system to develop stable resonances and weed out unstable ones.

Support [Planetary migration](https://en.wikipedia.org/wiki/Planetary_migration).

## Add support for disks around large proto-planets / improve moon formation.

This will, I hope, help to address the lack of moons around large planets. We know from our own solar system that gas giants tend to support numerous small rocky and icy moons, but StarGen tends not to have the same result because these planets are not generally numerous enough to be captured.

I won't know until it's implemented, but I think this is likely because of how StarGen handles moon formation as a capturing process, rather than letting large protoplanets form their own accertion disks.

## Improve handling related to the Roche Limit / Stellar Stripping.

Right now, the roche limit is handled by ensuring that moons that are captured do not end up with orbits inside the Roche Limit. Sensible, but it means that there's no way for planets to form saturn-like rings!

Support [Chthonian Planets](https://en.wikipedia.org/wiki/Chthonian_planet)

## Integrate more recent findings from Exoplanets

In the time since StarGen was written, we've gotten a ton of actionable data about solar system formation in the form of [exoplanets](https://en.wikipedia.org/wiki/Exoplanet). That includes some really cood data about gas giant colors, and a prevalence of Hot Jupiters.

There's a lot to digest.

# Credits

## Jim Burrows AKA Brons

Author of StarGen (last updated c. 2008), which Garnets is most closely based on.

## Matt Burdick

Author of Starform / Accrete (c. 1988)

## Chris Croughton AKA Keris

Forked and updated Starform

## Carl Burke

Forked and updated Starform

## Martyn Fogg

Wrote an early version of this concept and published a paper on it. This paper appears to have directly inspired Starform.


# Bibliography

Shamlessly stolen from StarGen docs.

"The Internal Constitution of the Planets"
D. S. Kothari, Ph.D. , Mon. Not. Roy. Astr. Soc. Vol 96, pp. 833 - 843, 1936

"Habitable Planets for Man"
S. H. Dole, Blaisdell Publishing Company, NY, 1964.

"Q in the Solar System"
P. Goldreich and S. Soter, Icarus, Vol 5, pp. 375 - 389, 1966

"Formation of Planetary Systems by Aggregation: A Computer Simulation"
S. H. Dole, RAND paper no. P-4226, 1969

"Computer Simulation of the Formation of Planetary Systems"
Dole, S. Icarus, vol 13, pp 494-508, 1970.

"Computer Simulation of Planetary Accretion Dynamics: Sensitivity to Initial Conditions"
Isaacman, Richard & Sagan, Carl Icarus, vol 31, p 510, 1977.

"The Evolution of the Atmosphere of the Earth"
Michael H. Hart, Icarus, Vol 33, pp. 23 - 39, 1978

"Extra-Solar Planetary Systems: A Microcomputer Simulation"
Fogg, Martyn J. Journal of the British Interplanetary Society, vol 38, 501-514, 1985.
