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
