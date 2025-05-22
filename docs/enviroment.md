# `enviroment.py` Documentation

## Overall Purpose

The `enviroment.py` module is a critical component of the planetary simulation. Once a planet's basic mass and orbital path are established (often by modules like `accrete.py` and `garnets.py`), `enviroment.py` takes over to determine the detailed physical and environmental conditions that characterize the planet. It's responsible for painting a picture of the planet, from its size and density to its atmospheric properties, surface temperature, the presence of water or ice, and ultimately, its potential for habitability. This module uses a wide range of physics and empirical formulas, drawing heavily on constants defined in `constants.py`.

## Key Calculation Areas and Example Functions

The process of defining a planet's environment involves numerous calculations, grouped into several key areas:

### Planetary Body Properties
This involves figuring out the basic physical nature of the planet itself.
*   **`kothari_radius`**: This function calculates a planet's radius. The calculation differs based on whether the planet is primarily rocky or a gas giant, reflecting the different ways these body types compress under gravity.
*   **`empirical_density`**: Estimates the planet's density based on its mass and where it's located in the stellar system, as distance from the star influences composition.

### Orbital and Rotational Characteristics
These functions define the planet's "day" and "year" and its seasons.
*   **`period`**: Calculates the length of the planet's year (its orbital period around the star).
*   **`day_length`**: Determines how long a planet's day is. This is complex, as it considers the planet's initial rotation, its mass, radius, and the tidal forces from its star, which can slow down rotation over time, potentially leading to tidal locking (one side always facing the star).
*   **`inclination`**: Calculates the planet's axial tilt, which is the cause of seasons.

### Atmospheric Retention and Properties
A major part of this module is determining if a planet can have an atmosphere and what that atmosphere might be like.
*   **`escape_vel`**: Calculates the escape velocity of the planet – how fast something needs to be moving to escape its gravitational pull. This is fundamental for holding onto an atmosphere.
*   **`rms_vel` (Root Mean Square Velocity)**: Calculates how fast, on average, gas molecules of a certain type are moving at a given temperature (typically the exospheric temperature).
*   **`molecule_limit` / `min_molec_weight`**: By comparing the escape velocity to the RMS velocity of gases, these functions determine the lightest types of gases (lowest molecular weights) that a planet can retain over long periods. Lighter gases like hydrogen and helium are harder to hold onto.
*   **`pressure`**: Once the amount of volatile gases a planet is likely to have is estimated (its "volatile gas inventory"), this function calculates the resulting surface atmospheric pressure, considering the planet's gravity.

### Surface Temperature Calculation
Determining a planet's surface temperature is one of the most complex and iterative parts of the simulation. Several factors are at play:
*   **`eff_temp` (Effective Temperature)**: Calculates the planet's base temperature as if it were a simple black body, based on the energy received from its star and its overall reflectivity (albedo).
*   **`planet_albedo`**: This function calculates the planet's overall albedo. Albedo is crucial because it determines how much stellar energy is reflected back into space versus absorbed. The albedo itself depends on what covers the surface: rock, water, ice, or clouds.
*   **`green_rise`**: If the planet has an atmosphere with greenhouse gases, this function calculates how much additional warming those gases will cause.
*   **`calculate_surface_temp` and `iterate_surface_temp`**: These are the core functions for surface temperature. `iterate_surface_temp` repeatedly calls `calculate_surface_temp`. In each step, `calculate_surface_temp` adjusts the planet's surface temperature, then recalculates the fractions of water, ice, and cloud cover based on that temperature. These fractions, in turn, affect the `planet_albedo`. The albedo and the calculated `green_rise` then lead to a new surface temperature. This loop continues until the temperature stabilizes, creating a self-consistent model.

### Surface Conditions and Habitability
With temperature and atmospheric properties determined, the module then assesses surface conditions and potential habitability.
*   **`boiling_point`**: Calculates the boiling point of water at the planet's surface pressure. This, along with the surface temperature, determines if liquid water can exist.
*   **`hydro_fraction`, `cloud_fraction`, `ice_fraction`**: These functions estimate the percentage of the planet's surface covered by liquid water, clouds, and ice, respectively, based on the calculated temperature and volatile inventory.
*   **`breathability`**: Evaluates the atmosphere's composition (calculated elsewhere, often in `garnets.py` using data from `chemtable.py`) to determine if it's breathable, poisonous, or simply unbreathable for human-like life. This involves checking the partial pressures of gases like oxygen and known toxins.

## Classifying Planets and Environments: The Role of Enumerations

To make sense of the vast amount of data calculated, `enviroment.py` uses several enumerations (Enums) to classify the planets and their environments:

*   **`PlanetType`**: After all calculations are done, a planet is assigned a `PlanetType` (e.g., `ROCK`, `VENUSIAN`, `TERRESTRIAL`, `GAS_GIANT`, `MARTIAN`, `WATER`, `ICE`, `ASTEROIDS`). This provides a quick summary of its overall nature. For example, a very hot planet with high surface pressure might be classified as `VENUSIAN`, while a cold world with a thin atmosphere might be `MARTIAN`. A temperate world with liquid water could be `TERRESTRIAL`.
*   **`BreathabilityPhrase`**: This enum (`NONE`, `BREATHABLE`, `UNBREATHABLE`, `POISONOUS`) gives a direct assessment of the atmosphere's suitability for human-like life.
*   **`Zone`**: This categorizes the planet's orbit (`ZONE_1` - inner, `ZONE_2` - intermediate/habitable, `ZONE_3` - outer) based on the amount of energy it receives from its star. This is a primary factor influencing a planet's potential to be habitable.

## Iterative Nature of Environmental Modeling

It's important to note that many of these environmental calculations are interdependent. For example, surface temperature depends on albedo, but albedo (due to ice/water/clouds) depends on surface temperature. This is why the simulation, particularly in `iterate_surface_temp`, uses an iterative approach, refining the values over several cycles until they reach a stable, self-consistent state.

*Note: The source code itself contains comments indicating areas for future refinement, such as potentially breaking this large file into smaller, more focused modules.*
