# Project Documentation

This project is composed of several Python modules, each responsible for a specific part of the planetary formation and environment simulation. Below is a list of these modules and links to their detailed documentation:

*   [`accrete.py`](accrete.md) - Simulates the accretion of dust and gas by planetesimals in a circumstellar disk.
*   [`chemtable.py`](chemtable.md) - Defines a table of chemical and physical properties for various atmospheric gases.
*   [`constants.py`](constants.md) - Contains a comprehensive list of physical, astronomical, and simulation-specific constants.
*   [`enviroment.py`](enviroment.md) - Calculates detailed environmental characteristics of planets, including temperature, pressure, and atmospheric properties.
*   [`garnets.py`](garnets.md) - Orchestrates the generation of entire stellar systems, from planetesimal formation to the detailed characterization of planets and moons.
*   [`stellar_system.py`](stellar_system.md) - Defines the core data structures for stars, planets, and their components.
*   [`util.py`](util.md) - Provides miscellaneous utility functions, some of which are placeholders or wrappers for standard Python functionality.

## Original StarGen C Code

The `StarGenCode/` 

## Potential Future Enhancements

The Python port currently provides the core engine for planetary system generation. The original C StarGen application had a rich set of features that could inspire future enhancements for this Python version, transforming it from a core library into a more comprehensive tool:

*   **Develop a User-Friendly Interface:**
    *   Create a command-line interface (CLI) for `garnets.py` to allow users to specify parameters like stellar mass, random seed, number of systems to generate, and feature toggles (e.g., for gas or moon generation) without needing to write Python code.
    *   Consider options for generating multiple systems in a single run, similar to the C version's batch capabilities.

*   **Implement Diverse Output Generation Modules:**
    *   **Textual Reports:** Generate detailed, human-readable text summaries of generated stellar systems.
    *   **HTML Output:** Create HTML pages for systems, potentially including graphical representations (see below).
    *   **Graphical System Diagrams:** Integrate capabilities to produce visual system diagrams (e.g., using SVG or libraries like Matplotlib).
    *   **Data Export:** Implement CSV (Comma Separated Values) output for easy data analysis of planetary properties across multiple generated systems.
    *   **Celestia Support:** Add functionality to generate `.ssc` files for importing generated systems into the Celestia space simulator.

*   **Integrate Star Catalog Functionality:**
    *   Develop a system to use predefined star catalogs (e.g., from local files or built-in sets similar to Dole's or SolStation lists in the C version) to seed the generation process with known stars.
    *   Allow iteration through catalog stars to generate their potential planetary systems.

*   **Enhance Logging and Verbosity Controls:**
    *   Expand the current Python logging to offer more granular control over diagnostic output, similar to the C version's `flag_verbose` bitmask system. This would aid in debugging and detailed tracing of the simulation.

*   **Add Advanced Filtering and System Analysis:**
    *   Implement mechanisms to filter generated systems based on specific criteria (e.g., presence of habitable planets, Earth-like planets, multiple habitable worlds, Jovian planets in habitable zones).
    *   Incorporate more specialized planetary classification checks, such as the "Earth-like" or "Sphinx-like" categories found in the C version.
    *   Provide options for collecting and summarizing statistics across batches of generated systems.

*   **Implement Seed System Functionality:**
    *   Allow the use of predefined planetary configurations (like the Solar System or other known exoplanetary systems) as a "seed" or template to influence or directly replicate certain aspects during the generation of new systems.

*   **Review and Refine Simulation Depth for Specific Scenarios:**
    *   Further investigate and potentially implement more detailed checks or logging for specific scenarios, such as the conditions for habitability on moons of gas giants or the specific criteria that defined "Sphinx-like" planets in the original.

## Remaining Tasks and TODOs

**For `chemtable.py`:**
*   Improve accuracy of `melt` and `boil` points, potentially using phase diagrams that consider pressure variations.
*   Enhance the simulation to model complex chemical reactions between atmospheric gases and with planetary surfaces.
*   Clarify the specific contexts and precise meanings of the `abunde` and `abunds` (abundance) metrics for gases.

**For `constants.py`:**
*   Consider refactoring the extensive `constants.py` file into smaller, more thematically focused modules for better organization and maintainability.
*   Review and clarify the meaning or source of some specific constants within `constants.py` that have existing `TODO` notes in the source code.

**For `enviroment.py`:**
*   Consider refactoring the large `enviroment.py` file into smaller, more specialized modules to improve code organization and readability (as suggested by comments in the source code).

**For `stellar_system.py`:**
*   Conduct a thorough review of the attributes in the `Planet` class. Many may be outdated, only relevant during initialization, or could be better implemented as properties (as suggested by comments in the source code).

**For `util.py`:**
*   Implement the `random_eccentricity()` function properly to generate realistic, varied orbital eccentricities, as it currently returns a placeholder value.
*   Refactor the `util.py` module. Many of its functions are simple wrappers for standard Python features or basic mathematical operations and could potentially be removed or integrated directly where used.

**For `garnets.py` (related to source code):**
*   The `random_star()` function could be improved by adding a seed parameter for reproducibility and by basing star generation on more realistic distributions.
