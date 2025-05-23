# `constants.py` Documentation

## Overview

The `constants.py` file is a crucial part of the planetary formation and environment simulation. It serves as a centralized repository for a wide array of numerical values that are used throughout the various calculations. These constants ensure consistency and make it easier to understand the basis for the simulation's parameters. The file imports `pi` from the `math` module for use in calculations.

The constants are broadly grouped into several categories, each serving a distinct purpose in the simulation:

### Categories of Constants

*   **Universal Constants:**
    These are fundamental physical constants that are universally applicable, such as the `GRAV_CONSTANT` (Gravitational constant) and `MOLAR_GAS_CONST` (Molar gas constant). They form the bedrock of many physical calculations within the simulation.

*   **Tunable Simulation Parameters & Initial Conditions:**
    This group includes values that can be adjusted to fine-tune the simulation's behavior or define starting conditions. Examples include `PROTOPLANET_MASS` (the initial mass for planetary embryos) and `K` (the gas/dust ratio in the protoplanetary disk). These parameters allow for experimentation with different scenarios of planet formation.

*   **Solar System Body Masses & Ratios:**
    This category provides standard masses for celestial bodies, primarily the Sun, and their equivalents in other units (e.g., `SOLAR_MASS_IN_GRAMS`, `SUN_MASS_IN_EARTH_MASSES`). These are essential for scaling calculations relative to known astronomical bodies.

*   **Earth-Specific Physical Constants:**
    A comprehensive set of values related to Earth's physical characteristics, such as `EARTH_RADIUS`, `EARTH_DENSITY`, `EARTH_AXIAL_TILT`, and `EARTH_ALBEDO`. These constants are often used as benchmarks or reference points for comparing generated planets to Earth.

*   **Time and Distance Units/Ratios:**
    This section defines conversion factors and standard units for time (e.g., `DAYS_IN_A_YEAR`, `SECONDS_PER_HOUR`) and distance (e.g., `CM_PER_AU`, `KM_PER_AU`). They ensure that all calculations are performed with consistent units.

*   **Pressure Units/Ratios:**
    Contains conversion factors for various units of pressure, such as `MMHG_TO_MILLIBARS` and `PSI_TO_MILLIBARS`. This is important for atmospheric calculations where pressure is a key variable.

*   **Atmospheric Composition & Chemistry Constants:**
    This is a large group of constants vital for modeling planetary atmospheres. It includes:
    *   *Gas Retention & Cloud Formation:* Parameters like `GAS_RETENTION_THRESHOLD` which helps determine if a planet can hold onto a particular gas.
    *   *Atomic/Molecular Weights:* Approximate weights for common gases (e.g., `MOL_HYDROGEN`, `CARBON_DIOXIDE`), used for calculating gas velocities and atmospheric escape.
    *   *Atomic Numbers:* Identifiers for elements and compounds (e.g., `AN_H`, `AN_CO2`), used by the `chemtable.py` module.
    *   *Inspired Partial Pressure Tolerances:* Values like `MIN_O2_IPP` (minimum breathable partial pressure of Oxygen) and `MAX_CO2_IPP` (maximum tolerable partial pressure of Carbon Dioxide), crucial for assessing the potential habitability of an atmosphere.

*   **Albedo Values:**
    This category provides estimated albedo (reflectivity) values for different types of surfaces and conditions, such as `ICE_ALBEDO`, `WATER_ALBEDO`, and `CLOUD_ALBEDO`. Albedo is a key factor in calculating a planet's energy balance and surface temperature.
