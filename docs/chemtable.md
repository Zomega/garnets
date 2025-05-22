# `chemtable.py` Documentation

## Overview

The `chemtable.py` file is a crucial data module for the planetary simulation. Its primary role is to provide a comprehensive list of various atmospheric gases and their fundamental properties. This information is essential for other modules (like `enviroment.py` and `garnets.py`) when they model planetary atmospheres, calculate their composition, determine gas retention, and assess environmental conditions such as breathability.

The module defines a `Gas` class to structure the information for each gas and then populates a list named `gases` with instances of this class for many common atmospheric components. It also imports related constants (like atomic numbers and maximum inspired partial pressures) from `constants.py`.

## The `Gas` Class: Storing Chemical Properties

The `Gas` class serves as a container to hold a standardized set of properties for each individual gas. Instead of scattering these values throughout the code, the `Gas` class ensures that all relevant information for a substance is grouped together.

Key types of information stored in a `Gas` object include:

*   **Identification:** Chemical `symbol` (e.g., "O2", "CH4"), common `name` (e.g., "Oxygen", "Methane"), and a unique numerical identifier (`num`, often an atomic number or a predefined constant).
*   **Physical Properties:** These include `weight` (atomic or molecular), `melt` (melting point), `boil` (boiling point), and `density`. These are vital for determining the state of the gas at different planetary temperatures and for calculating how easily a planet's gravity can retain the gas.
*   **Abundance Metrics:** Fields like `abunde` and `abunds` provide data on the typical abundance of the gas in stellar or solar system environments, which helps in estimating its initial availability.
*   **Chemical Behavior:** The `reactivity` attribute gives an indication of how readily the gas will engage in chemical reactions.
*   **Physiological Impact:** The `max_ipp` (maximum inspired partial pressure) attribute stores information about the breathable limits of the gas, important for assessing habitability.

## The `gases` List: A Chemical Compendium

The `gases` list is the main data structure provided by this module. It is a predefined collection of `Gas` objects, effectively acting as a lookup table or a chemical compendium for the simulation. Each entry in this list represents a specific gas (e.g., Hydrogen, Helium, Oxygen, Carbon Dioxide, Methane, etc.) and is populated with the properties described above.

### How the `gases` List is Used

Other parts of the simulation rely heavily on this list:

*   **Atmosphere Calculation:** When a planet's atmosphere is being modeled, the simulation iterates through the `gases` list. For each gas, it checks if the planet's conditions (temperature, gravity, escape velocity) would allow it to retain that gas.
*   **Property Lookup:** If the simulation needs to know the molecular weight of Oxygen, for instance, it can find the Oxygen entry in the `gases` list and access its `weight` attribute.
*   **Environmental Assessment:** Properties like `max_ipp` are used to determine if a calculated atmosphere would be breathable or toxic. The boiling points help determine if a substance would be a gas, liquid, or solid on the planet's surface.

### Example Conceptual Gas Entry

Here's a conceptual look at how an entry in the `gases` list might be structured (values are illustrative):

```python
# Conceptual structure of a Gas object within the 'gases' list
# Real entries are created using the Gas class, e.g.:
# Gas(num=AN_O, symbol="O2", name="Oxygen", weight=32.0, boil=90.2, ...)

# Example for Oxygen:
# - num: AN_O (from constants.py)
# - symbol: "O2"
# - name: "Oxygen"
# - weight: 32.00 (g/mol)
# - melt: 54.8 K
# - boil: 90.2 K
# - density: 0.001429 (g/cm^3 at STP)
# - abunde: (some solar system abundance value)
# - abunds: (some stellar abundance value)
# - reactivity: 10 (highly reactive)
# - max_ipp: MAX_O2_IPP (max breathable partial pressure, from constants.py)

# Example for Methane:
# - num: AN_CH4 (from constants.py)
# - symbol: "CH4"
# - name: "Methane"
# - weight: 16.04 (g/mol)
# - ... (other properties like boil, density, reactivity, etc.)
```

## Limitations and Considerations

The source code notes some simplifications and areas for future enhancement, for instance, regarding phase diagrams and complex chemical reactions. The specific contexts for some abundance metrics could also be further clarified.

## Accessing Gas Data

To use this data, other modules typically import the `gases` list and then iterate through it or look up specific gases by their properties (like `symbol` or `num`).

```python
from chemtable import gases # Assuming chemtable.py is in the python path
from constants import AN_N # Example: Atomic number for Nitrogen from constants.py

# Find Nitrogen in the list
nitrogen = None
for gas in gases:
    if gas.num == AN_N:
        nitrogen = gas
        break

if nitrogen:
    print(f"Found: {nitrogen.name}")
    print(f"  Molecular Weight: {nitrogen.weight}")
    print(f"  Boiling Point: {nitrogen.boil} K")
else:
    print("Nitrogen not found in the list.")
```
This example shows a common way to retrieve specific gas information for use in other simulation calculations.
