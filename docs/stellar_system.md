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
*   **Relationship**: The top-level object in a system. `Planet` objects are associated with a `Star`.

### `Planetoid` (Base Class)
*   **Role**: This is a general base class for any celestial body that is not a star but orbits one. It establishes the core properties common to all such bodies.
*   **Key Attributes**:
    *   `orbit` (`Orbit` object): Defines its path around the central star.
    *   `dust_mass` (float): Mass of solid materials (rock, ice).
    *   `gas_mass` (float): Mass of gaseous materials.
    *   (Calculated `mass` property: total mass).
*   **Relationship**: Serves as the parent class for `Planetesimal`, `Protoplanet`, `Protomoon`, and indirectly for `Planet`. It defines the concept of having mass and an orbit.

### `Planetesimal`
*   **Role**: Represents the earliest, smallest building blocks of planets, akin to asteroids or cometesimals in a young protoplanetary disk.
*   **Key Attributes (inherits from `Planetoid`)**:
    *   `disk` (`CircumstellarDisk` object): A reference to the disk it resides in, used for calculating its `critical_mass`.
*   **Properties**:
    *   `critical_mass` (float): The mass threshold at which it can begin to rapidly accrete gas.
*   **Relationship**: A `Planetesimal` is a type of `Planetoid`. It interacts with the `CircumstellarDisk` (defined in `accrete.py`) to grow.

### `Protoplanet`
*   **Role**: Represents a more developed planetary embryo, larger and more massive than a planetesimal. It's an intermediate stage towards becoming a full planet and can start to gather its own small satellites (protomoons).
*   **Key Attributes (inherits from `Planetoid`)**:
    *   `star` (`Star` object): Reference to its parent star.
    *   `moons` (list): A list to hold `Protomoon` objects that may be captured or formed around it.
*   **Properties**:
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
    *   `atmosphere` (list): Detailed atmospheric composition.
    *   `moons` (list): A list of other `Planet` objects that serve as its moons.
*   **Relationship**: A `Planet` is the final stage of evolution for a `Protoplanet`. It orbits a `Star`. Importantly, a `Planet` can also *be* a moon, in which case its `orbit` is defined relative to its parent `Planet`. The `Planet` class contains a very large number of attributes; the source code itself includes comments suggesting many of these should be reviewed for relevance or potential conversion to properties.

### `StellarSystem`
*   **Role**: A simple container class designed to group a `Star` object and its list of `Planet` objects.
*   **Key Attributes**:
    *   `star` (`Star` object).
    *   `planets` (list of `Planet` objects).
*   **Relationship**: Provides an overarching structure for a star and its planets. Its functionality might overlap with the `planets` list within the `Star` object itself, potentially serving as a convenient way to pass an entire system as a single entity.