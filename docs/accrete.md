# `accrete.py` Documentation

## Overview

The `accrete.py` module is responsible for simulating a key phase in planetary formation: the accretion of material by young planetesimals from a circumstellar disk. This disk, composed of dust and gas, surrounds a newly formed star. As planetesimals orbit the star, they sweep through the disk, gathering material and growing in mass. This module defines the necessary structures and processes to model this phenomenon, relying on physical constants from `constants.py`.

## The Accretion Model

The simulation of accretion in this module revolves around two primary classes: `CircumstellarDisk` and `CircumstellarDustLane`.

### `CircumstellarDustLane`

A `CircumstellarDustLane` represents a specific ring or segment of the larger circumstellar disk. Each lane is defined by an inner and outer edge from the central star and keeps track of whether dust and gas are currently present within its boundaries. This allows the disk to have a non-uniform distribution of material.

*   **Key Attributes:**
    *   `inner_edge` (float): The inner radius of the dust lane.
    *   `outer_edge` (float): The outer radius of the dust lane.
    *   `dust_present` (bool): Indicates if dust is in this lane.
    *   `gas_present` (bool): Indicates if gas is in this lane.

### `CircumstellarDisk`

The `CircumstellarDisk` class represents the entire expanse of dust and gas surrounding the central star. It is composed of one or more `CircumstellarDustLane` objects, which together define the structure and content of the disk.

*   **Key Responsibilities:**
    *   **Initialization**: When created (based on a `Star` object), it establishes the overall boundaries for planet formation and sets up initial dust lanes.
    *   **Dust Density Calculation**: Provides the `dust_density()` method to determine the density of dust at a given orbital distance. This is crucial for calculating how much material a planetesimal can accrete.
    *   **Tracking Material**: Keeps track of whether dust is still available anywhere in the disk (`dust_left` property) and whether it's available within a specific orbital range (`dust_available()`).
    *   **Orchestrating Accretion**: Manages the core accretion process through its methods.

## The Accretion Process

1.  **Planetesimal Interaction**: A `Planetoid` (representing a planetesimal or protoplanet, defined in `stellar_system.py`) is introduced into the `CircumstellarDisk`.
2.  **Material Collection (`collect_dust()` method on `CircumstellarDisk`)**:
    *   The disk determines which of its `CircumstellarDustLane`s overlap with the `Planetoid`'s gravitational sphere of influence.
    *   For each overlapping lane, the disk calculates the amount of dust the `Planetoid` can accrete based on the lane's dust density and the volume of the swept region.
    *   If the `Planetoid` has reached a "critical mass" (sufficient to gravitationally capture gas) and gas is present in the lane, gas accretion is also calculated.
    *   This method returns the total new dust and gas mass collected by the `Planetoid`.
3.  **Iterative Growth (`accrete_dust()` method on `CircumstellarDisk`)**:
    *   This method simulates the continuous growth of a `Planetoid`.
    *   It repeatedly calls `collect_dust()` to gather material, updating the `Planetoid`'s mass.
    *   This iterative process continues until the amount of mass accreted in one pass becomes negligible compared to the `Planetoid`'s total mass, indicating that it has effectively cleared its orbital path or the available material is exhausted.
4.  **Updating the Disk (`update_dust_lanes()` method on `CircumstellarDisk`)**:
    *   After a `Planetoid` has accreted material (typically after the `accrete_dust()` process completes), the disk's structure must be updated.
    *   The lanes that the `Planetoid` swept through are modified. Often, a lane is split into new lanes: one for the region now cleared of dust by the `Planetoid`, and potentially new lanes for any remaining portions of the original lane that were outside the `Planetoid`'s influence.
    *   The swept portion is marked as `dust_present = False`. Gas presence is also updated based on whether the `Planetoid` accreted gas.

This cycle of collection and disk update allows the simulation to model the gradual depletion of the circumstellar disk as planetesimals grow into larger bodies.

## Conceptual Code Example

The following illustrates how these classes might be used in a simplified, conceptual manner. Note that `Star` and `Planetoid` would be defined in other modules like `stellar_system.py`.

```python
# Assume Star and Planetoid classes are defined elsewhere
# from stellar_system import Star, Planetoid, Orbit
# from accrete import CircumstellarDisk # CircumstellarDustLane is used internally by CircumstellarDisk

# 1. Initialize a Star (details depend on the Star class definition)
# star = Star(mass_ratio=1.0, age=1e9) # Example values
# star.stellar_dust_limit = 50.0 # AU, example

# 2. Create the Circumstellar Disk around the Star
# disk = CircumstellarDisk(star=star)

# 3. Define a Planetoid (details depend on the Planetoid class definition)
# initial_orbit = Orbit(a=1.0, e=0.05) # Example orbit at 1 AU
# planetoid = Planetoid(orbit=initial_orbit, dust_mass=1e-10, gas_mass=0.0) # Example initial mass
# # Other necessary planetoid attributes like inner_effect_limit, outer_effect_limit, critical_mass
# # would also need to be set or calculated.
# planetoid.inner_effect_limit = 0.9 # Example
# planetoid.outer_effect_limit = 1.1 # Example
# planetoid.critical_mass = 0.0001 # Example (in solar masses)

# 4. Simulate the accretion process for the Planetoid
# if disk.dust_available(planetoid.inner_effect_limit, planetoid.outer_effect_limit):
#     disk.accrete_dust(planetoid) # This method handles iterative collection and updates the planetoid's mass

# 5. After accretion, the planetoid's mass will have changed,
#    and the disk's dust lanes will be updated.
# print(f"Planetoid final dust mass: {planetoid.dust_mass}, final gas mass: {planetoid.gas_mass}")
# print(f"Is there still dust left in the disk? {disk.dust_left}")
```
This conceptual example shows the main interaction: creating a disk, introducing a planetesimal, and then letting the `accrete_dust` method handle the growth and subsequent changes to the disk. The actual implementation in `garnets.py` involves more detailed setup and iteration.
