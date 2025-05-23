# `util.py` Documentation

## Overview

The `util.py` file provides a collection of miscellaneous helper functions designed to support various calculations and processes within the planetary formation simulation. Many of these functions were inherited from an earlier system (possibly "stargen") and, as noted in the source code, might be redundant with standard Python features or are currently placeholders. The general sentiment in the source is that "Pretty much all of these should be removed."

This module imports the `random` library for its random number generation capabilities.

## Purpose of Utility Functions

The functions in this module can be broadly categorized by their purpose within the simulation:

### Mathematical Operations
These functions perform basic mathematical calculations that are frequently needed in the physics and geometry of planetary system modeling.
*   **`pow1_4(x)`**: Calculates the fourth root of a number.
*   **`pow2(x)`**: Calculates the square of a number (e.g., for area or energy calculations).
*   **`pow3(x)`**: Calculates the cube of a number (e.g., for volume calculations).

These are straightforward mathematical conveniences, though Python's built-in `**` operator (e.g., `x**0.25`, `x**2`, `x**3`) can achieve the same results.

### Random Number Generation
Introducing variability is key to generating diverse and unique stellar systems. These functions help inject randomness at various stages of the simulation.
*   **`random_number(a, b)`**: Generates a random floating-point number within a specified inclusive range `[a, b]`. This can be used for any parameter that needs to vary within defined limits. This is a direct wrapper for `random.uniform(a,b)`.
*   **`about(x, dx)`**: Generates a random floating-point number in a range centered around a value `x`, with a maximum deviation of `dx` (i.e., `x ± dx`). This is useful for creating slight variations around a standard or calculated value. This is equivalent to `random.uniform(x - dx, x + dx)`.

### Specialized Random Value Generation
This category is for functions that generate specific types of random values relevant to the simulation's domain.
*   **`random_eccentricity()`**: This function is intended to generate a random orbital eccentricity, which is a crucial parameter defining the shape of a planet's orbit (0 for circular, higher for more elliptical).
    *   **Current Status**: It's important to note that this function is currently a placeholder and always returns `0`. The source code itself indicates that it needs to be implemented properly.

## General Note on Redundancy and Future Development

As highlighted in the source code comments and by the direct equivalence of some functions to standard Python features, this module is likely to be refactored. Many of these utilities might be removed in favor of direct Python expressions, or they could be integrated into more specialized classes or functions where they are used. The `random_eccentricity` function, in particular, requires a proper implementation.

For now, they serve as simple helpers for common operations needed by the simulation algorithms.
