# `garnets.py` Documentation

## Overall Purpose

`garnets.py` serves as the primary engine for constructing entire stellar systems within the simulation. It orchestrates the complex sequence of events that leads from a single star to a system of fully characterized planets, potentially with moons. This module acts as a conductor, initiating processes and calling upon other specialized modules (`stellar_system.py` for data structures, `accrete.py` for material gathering, `enviroment.py` for environmental calculations, `chemtable.py` for gas data, and `constants.py` for physical values) to perform detailed calculations.

The simulation flow generally follows these major stages:
1.  Creation of a central star.
2.  Formation of protoplanets (planetary embryos) from a circumstellar disk around the star.
3.  Development of these protoplanets into fully detailed planets, including their physical and environmental characteristics, and potentially, the formation of moons.

## Core Orchestration Functions

Here's how the main functions in `garnets.py` collaborate to achieve this:

### 1. Starting with a Star: `random_star()`

*   **Purpose**: To create the central `Star` object that will be the anchor of the new planetary system.
*   **Inputs**: Typically none (though it can be seeded for reproducibility).
*   **Outputs**: A `Star` object (defined in `stellar_system.py`), usually initialized with a randomized age and a default (solar) mass.
*   **Role**: This is often the first step, providing the stellar context (mass, luminosity, age) which heavily influences how planets form and evolve.

### 2. Generating the Entire System: `generate_stellar_system()`

*   **Purpose**: This is the top-level function that, given a star, generates all its planets and (optionally) their moons and atmospheres.
*   **Inputs**:
    *   `star` (`Star` object): The star created by `random_star()` or provided otherwise.
    *   `do_gases` (bool, optional): Flag to enable/disable detailed atmospheric composition generation.
    *   `do_moons` (bool, optional): Flag to enable/disable moon generation.
*   **Outputs**: The input `Star` object, but now its `planets` attribute is populated with a list of fully characterized `Planet` objects.
*   **Role**: It coordinates the overall generation by:
    1.  Calling `generate_planetary_masses()` to simulate the formation of planetary embryos (protoplanets) from the star's disk.
    2.  Iterating through each resulting `Protoplanet` and calling `generate_planet()` to develop it into a complete `Planet`.

### 3. Forming Planetary Embryos: `generate_planetary_masses()`

*   **Purpose**: To simulate the initial stage of planet formation: the emergence of `Protoplanet` objects from a circumstellar disk of dust and gas.
*   **Inputs**:
    *   `star` (`Star` object): The central star, which dictates disk properties.
    *   `inner_dust`, `outer_dust` (float): Boundaries of the dust disk.
    *   `do_moons` (bool, optional): Influences whether moon capture is considered during early interactions.
*   **Outputs**: A list of `Protoplanet` objects, representing planetary embryos with basic mass and orbital properties.
*   **Role**: This function sets up a `CircumstellarDisk` (from `accrete.py`) and then simulates:
    *   The introduction of small `Planetesimal`s into the disk at random locations (using the helper `random_planetesimal()`).
    *   The growth of these planetesimals as they gather material from the disk (using `disk.accrete_dust()` from `accrete.py`).
    *   If a planetesimal grows substantially, `coalesce_planetesimals()` is called to manage its interactions with other bodies.

### 4. Handling Interactions and Growth: `coalesce_planetesimals()`

*   **Purpose**: To manage the dynamic interactions between a newly grown, significant `Planetesimal` (the "candidate") and any existing `Protoplanet`s in the system.
*   **Inputs**:
    *   `disk` (`CircumstellarDisk` object): The current state of the circumstellar disk.
    *   `planets` (list): The current list of `Protoplanet` objects.
    *   `candidate` (`Planetesimal` object): The new, substantial planetesimal.
    *   `do_moons` (bool): Flag indicating if moon capture is possible.
*   **Outputs**: The list of `Protoplanet`s, potentially modified by mergers or by the addition of the candidate as a new protoplanet or a moon.
*   **Role**: This function determines the fate of the `candidate`:
    *   **Collision/Merger**: If the candidate overlaps orbitally with an existing `Protoplanet`, they might merge, combining their mass and adjusting the orbit.
    *   **Moon Capture**: If `do_moons` is true and conditions are favorable (e.g., mass ratios), the candidate might be captured as a moon by a larger `Protoplanet` (converted to a `Protomoon`).
    *   **New Protoplanet**: If no interaction occurs, the candidate becomes a new, independent `Protoplanet` in the system.

### 5. Developing Full Planets (and Moons): `generate_planet()`

*   **Purpose**: To transform a basic `Protoplanet` (which is essentially just a mass at a certain orbit) into a fully detailed `Planet` object with a complete set of physical and environmental characteristics.
*   **Inputs**:
    *   `protoplanet` (`Protoplanet` object): The planetary embryo to develop.
    *   `star` (`Star` object): The parent star.
    *   `do_gases`, `do_moons` (bool, optional): Flags for atmospheric and moon generation.
    *   `is_moon` (bool, optional): Indicates if this planet itself is being generated as a moon of another.
*   **Outputs**: A `Planet` object, fully characterized, and potentially including its own list of `Planet` objects as moons.
*   **Role**: This is where the detailed planetary science happens. For each `Protoplanet`, this function:
    *   Calculates its size, density, core properties, and whether it's rocky or a gas giant.
    *   Determines its atmospheric retention capabilities, surface pressure, and temperature through an iterative process that balances stellar energy input, albedo, and greenhouse effects (heavily relying on functions from `enviroment.py`).
    *   If `do_gases` is enabled, it calls `calculate_gases()` to determine the specific atmospheric composition.
    *   If `do_moons` is enabled and the input `protoplanet` has associated `Protomoon`s, it recursively calls itself (`generate_planet` with `is_moon=True`) for each protomoon to fully characterize it, then adds it to the parent planet's list of moons. Stability checks like `roche_limit` and `hill_sphere` (helper functions) are used here.

### 6. Defining Atmospheric Composition: `calculate_gases()`

*   **Purpose**: To determine the detailed composition of a planet's atmosphere.
*   **Inputs**:
    *   `star` (`Star` object): For context like stellar age.
    *   `planet` (`Planet` object): The planet whose atmosphere is being defined (must have basic properties like temperature, escape velocity, etc., already calculated by `generate_planet`).
*   **Outputs**: Modifies the input `Planet` object by populating its `atmosphere` attribute with a list of constituent gases and their partial pressures.
*   **Role**: It iterates through a list of known gases (from `chemtable.py`) and, for each one, assesses if the planet can retain it based on its molecular weight, the planet's temperature and gravity, and other factors like gas reactivity and abundance.

## Conceptual Flow of System Generation

```
1. Start:
   random_star()
     --> Star_Object (mass, age, luminosity, etc.)

2. Orchestration:
   generate_stellar_system(Star_Object, do_gases, do_moons)
     |
     |--> Calls: generate_planetary_masses(Star_Object, ...)
     |      |
     |      |--> Creates: CircumstellarDisk (from accrete.py)
     |      |--> Loop:
     |      |      random_planetesimal() --> Candidate_Planetesimal
     |      |      disk.accrete_dust(Candidate_Planetesimal) (from accrete.py)
     |      |      IF Candidate_Planetesimal grew significantly:
     |      |         coalesce_planetesimals(disk, existing_Protoplanets, Candidate_Planetesimal, ...)
     |      |           --> existing_Protoplanets (list is modified with mergers/new additions/moons)
     |      |
     |      --> Returns: List_of_Protoplanets
     |
     |--> Loop for each Protoplanet_in_List:
     |      Calls: generate_planet(Protoplanet, Star_Object, do_gases, do_moons, ...)
     |             |
     |             |--> Uses many functions from enviroment.py (for radius, density, temp, etc.)
     |             |--> IF do_gases:
     |             |      Calls: calculate_gases(Star_Object, Planet_being_generated)
     |             |             --> Planet_being_generated.atmosphere is populated
     |             |--> IF do_moons and Protoplanet has Protomoon objects:
     |             |      Recursively calls: generate_planet(Protomoon, Star_Object, ..., is_moon=True)
     |             |                         --> Moon_Planet_Object
     |             |      Adds Moon_Planet_Object to parent Planet's moon list.
     |             |
     |             --> Returns: Fully_Characterized_Planet_Object
     |
     --> Star_Object.planets is populated with list of Fully_Characterized_Planet_Objects

3. End:
   Star_Object (now with a full system of planets and moons) is the final result.
```

This layered approach allows `garnets.py` to manage the complex process of stellar system generation by delegating specialized tasks to other modules while maintaining overall control of the simulation flow. The `if __name__ == '__main__':` block provides a smoke test to run this entire pipeline.
