# `stellar_system.py` Documentation

## Overall Purpose

The `stellar_system.py` module provides the fundamental "blueprints" for all objects that make up a simulated stellar system. It defines a set of Python classes that represent stars, planets at various stages of their formation (from tiny planetesimals to fully formed worlds), and the orbital paths they follow. These classes are primarily data containers, designed using the `attrs` library for conciseness, and they hold the essential properties and characteristics of each celestial body and its environment. Other modules in the simulation use these class instances to perform calculations and model the system's evolution.

## Core Classes: Representing the Cosmos

The simulation builds up a stellar system using instances of these core classes:

### `Orbit`
*   **Role**: Defines the path an object takes as it orbits a central body. This is a fundamental component used by all orbiting entities like planets, moons, and planetesimals.
*   **Key Attributes**:
    *   `a` (float): The semi-major axis, representing the average distance of the orbit.
    *   `e` (float): The eccentricity, describing the shape of the orbit (0 for circular, >0 for elliptical).
*   **Relationship**: An `Orbit` object is an attribute of every class that orbits another (e.g., `Planetoid`, `Planet`).

### `Star`
*   **Role**: Represents the central star of a planetary system. Its properties, like mass and age, are crucial as they dictate the conditions for planet formation and the extent of the habitable zone.
*   **Key Attributes**:
    *   `mass_ratio` (float): The star's mass relative to the Sun.
    *   `age` (float): The star's age.
    *   `planets` (list): A list that will be populated with `Planet` objects orbiting this star.
*   **Key Properties (calculated from attributes or constants):**
    *   `luminosity_ratio` (float): The star's luminosity relative to the Sun, calculated using a standard mass-luminosity relationship (L ∝ M^3.5).
    *   `stellar_dust_limit` (float): The distance from the star beyond which dust can condense. This is derived from an approximation used in the original StarGen model, based on the star's luminosity.
    *   `r_ecosphere` (float): The radius of the star's ecosphere (habitable zone), also based on an approximation from the StarGen model, scaled with the star's luminosity.
    *   `life` (float): An estimate of the star's main-sequence lifetime, calculated using a formula relating stellar mass to lifetime (T ∝ M^-2.5).
    *   The precise calibration of these stellar models (luminosity, dust limit, ecosphere, lifetime) against the latest astrophysical data is an area for ongoing review and future refinement.
*   **Relationship**: The top-level object in a system. `Planet` objects are associated with a `Star`.

### `Planetoid` (Base Class)
*   **Role**: This is a general base class for any celestial body that is not a star but orbits one. It establishes the core properties common to all such bodies.
*   **Key Attributes**:
    *   `orbit` (`Orbit` object): Defines its path around the central star.
    *   `dust_mass` (float): Mass of solid materials (rock, ice).
    *   `gas_mass` (float): Mass of gaseous materials.
    *   (Calculated `mass` property: total mass).
*   **Key Properties (calculated):**
    *   `reduced_mass` (float): The reduced mass of the planetoid in relation to its star. This calculation currently uses the module-level placeholder `STAR_MASS` for the stellar mass.
    *   `inner_effect_limit` (float): The inner boundary of the planetoid's gravitational influence. The current model defines this limit based on the planetoid's semi-major axis (`a`) and eccentricity (`e`), calculated as `a * (1 - e)`.
    *   `outer_effect_limit` (float): The outer boundary of the planetoid's gravitational influence. The current model defines this limit based on the planetoid's semi-major axis (`a`) and eccentricity (`e`), calculated as `a * (1 + e)`.
*   **Relationship**: Serves as the parent class for `Planetesimal`, `Protoplanet`, `Protomoon`, and indirectly for `Planet`. It defines the concept of having mass and an orbit.

### `Planetesimal`
*   **Role**: Represents the earliest, smallest building blocks of planets, akin to asteroids or cometesimals in a young protoplanetary disk.
*   **Key Attributes (inherits from `Planetoid`)**:
    *   `disk` (`CircumstellarDisk` object): A reference to the disk it resides in, used for calculating its `critical_mass`.
*   **Properties (inherits from `Planetoid`, plus):**
    *   `critical_mass` (float): The mass threshold at which it can begin to rapidly accrete gas. The current model calculates this based on factors including the star's luminosity, the planetesimal's distance from the star, and various physical constants.
*   **Relationship**: A `Planetesimal` is a type of `Planetoid`. It interacts with the `CircumstellarDisk` (defined in `accrete.py`) to grow.

### `Protoplanet`
*   **Role**: Represents a more developed planetary embryo, larger and more massive than a planetesimal. It's an intermediate stage towards becoming a full planet and can start to gather its own small satellites (protomoons).
*   **Key Attributes (inherits from `Planetoid`)**:
    *   `star` (`Star` object): Reference to its parent star.
    *   `moons` (list): A list to hold `Protomoon` objects that may be captured or formed around it.
*   **Properties (inherits from `Planetoid`, plus):**
    *   `critical_mass` (float): Similar to `Planetesimal`, the mass for rapid gas accretion.
*   **Relationship**: A `Protoplanet` is a more evolved `Planetoid`. It orbits a `Star` and can have `Protomoon`s.

### `Protomoon`
*   **Role**: Represents a moon in its formative stages, orbiting a `Protoplanet`.
*   **Key Attributes (inherits from `Planetoid`)**:
    *   `protoplanet` (`Protoplanet` object): A reference to the `Protoplanet` it orbits.
*   **Relationship**: A `Protomoon` is a type of `Planetoid` that is gravitationally bound to a `Protoplanet`.

### `Planet`
*   **Role**: This class represents a fully formed planet, with a comprehensive set of calculated physical and environmental characteristics. It's the most detailed data structure for a celestial body in the simulation.
*   **Key Attributes (selected examples - many are calculated by `enviroment.py` and `garnets.py`):**
    *   `orbit` (`Orbit` object): Its orbit around the `Star` (or parent planet, if it's a moon).
    *   `mass` (float): Total mass.
    *   `radius` (float): Equatorial radius.
    *   `axial_tilt` (float): Determines seasons.
    *   `type` (`PlanetType` enum from `enviroment.py`): Classification like `TERRESTRIAL`, `GAS_GIANT`, `ICE`, etc.
    *   `surf_temp` (float): Surface temperature.
    *   `surf_pressure` (float): Atmospheric surface pressure.
    *   `orbit_zone` (`Zone` enum from `enviroment.py`): Orbital zone classification.
    *   `day_length` (float): Length of one planetary rotation.
    *   `orbital_period` (float): Length of one orbit around the star.
    *   `axial_tilt` (float): Planet's axial tilt in degrees, influencing seasons.
    *   `escape_velocity` (float): Escape velocity from the planet's surface.
    *   `surf_accel` (float): Surface acceleration (gravity).
    *   `rms_velocity` (float): Root mean square velocity of gases at the exosphere.
    *   `min_molec_weight` (float): Minimum molecular weight retainable by the planet.
    *   `volatile_gas_inventory` (float): Initial amount of gas-forming volatiles.
    *   `surf_pressure` (float): Atmospheric pressure at the surface.
    *   `greenhouse_effect` (bool): Indicates if a runaway greenhouse effect is active.
    *   `boil_point` (float): Boiling point of water at the surface pressure.
    *   `albedo` (float): Planet's overall albedo.
    *   `surf_temp` (float): Average surface temperature.
    *   `exospheric_temp` (float): Temperature at the exosphere.
    *   `estimated_temp` (float): Temperature estimate used during some calculations.
    *   `estimated_terr_temp` (float): Terrestrial temperature estimate.
    *   `surf_grav` (float): Surface gravity (alternate to surf_accel).
    *   `hydrosphere` (float): Fraction of surface covered by water.
    *   `cloud_cover` (float): Fraction of surface covered by clouds.
    *   `ice_cover` (float): Fraction of surface covered by ice.
    *   `atmosphere` (list): Detailed atmospheric composition, list of `Gas` objects with their partial pressures.
    *   `type` (`PlanetType` enum from `enviroment.py`): Classification like `TERRESTRIAL`, `GAS_GIANT`, `ICE`, etc.
    *   `minor_contaminants` (list): List of minor atmospheric contaminants.
    *   `gases` (int): Count of gases in the atmosphere.
    *   `breathable` (`BreathabilityPhrase` enum from `enviroment.py`): Atmospheric breathability.
    *   `moons` (list): A list of other `Planet` objects that serve as its moons.
    *   `parent_body` (Planet): Reference to parent planet if this is a moon.
*   **Relationship**: A `Planet` is the final stage of evolution for a `Protoplanet`. It orbits a `Star`. Importantly, a `Planet` can also *be* a moon, in which case its `orbit` is defined relative to its parent `Planet`.
*   The `Planet` class serves as a comprehensive container for a wide array of orbital, physical, and atmospheric data. Many attributes are populated progressively during the simulation stages. The structure and initialization of these attributes are subject to ongoing review to optimize for clarity, consistency, and simulation accuracy.

### `StellarSystem`
*   **Role**: A simple container class designed to group a `Star` object and its list of `Planet` objects.
*   **Key Attributes**:
    *   `star` (`Star` object).
    *   `planets` (list of `Planet` objects).
*   **Relationship**: Provides an overarching structure for a star and its planets. Its functionality might overlap with the `planets` list within the `Star` object itself, potentially serving as a convenient way to pass an entire system as a single entity.

## Module-Level Constants and Simplifications

*   **`STAR_MASS`**: A module-level constant `STAR_MASS` (currently set to 1 solar mass) is used as a simplifying placeholder for the central star's mass in certain calculations (e.g., `Planetoid.reduced_mass`). This is distinct from the `Star` object's own `mass` attribute. Future development aims to consistently utilize the specific `Star` object's mass throughout all relevant calculations.