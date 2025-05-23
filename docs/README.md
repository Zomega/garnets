# Project Documentation

This project is composed of several Python modules, each responsible for a specific part of the planetary formation and environment simulation. Below is a list of these modules and links to their detailed documentation:

*   [`accrete.py`](accrete.md) - Simulates the accretion of dust and gas by planetesimals in a circumstellar disk.
*   [`chemtable.py`](chemtable.md) - Defines a table of chemical and physical properties for various atmospheric gases.
*   [`constants.py`](constants.md) - Contains a comprehensive list of physical, astronomical, and simulation-specific constants.
*   [`enviroment.py`](enviroment.md) - Calculates detailed environmental characteristics of planets, including temperature, pressure, and atmospheric properties.
*   [`garnets.py`](garnets.md) - Orchestrates the generation of entire stellar systems, from planetesimal formation to the detailed characterization of planets and moons.
*   [`stellar_system.py`](stellar_system.md) - Defines the core data structures for stars, planets, and their components.

## Original StarGen C Code

The `StarGenCode/` 

## Potential Future Enhancements

The Python port currently provides the core engine for planetary system generation. The original C StarGen application had a rich set of features that could inspire future enhancements for this Python version, transforming it from a core library into a more comprehensive tool:

*   **Develop a User-Friendly Interface:**
    *   Create a command-line interface (CLI) for `garnets.py` to allow users to specify parameters like stellar mass, random seed, number of systems to generate, and feature toggles (e.g., for gas or moon generation) without needing to write Python code.
    *   Consider options for generating multiple systems in a single run, similar to the C version's batch capabilities.

*   **Implement Diverse Output Generation Modules:**
    *   **Textual Reports:** Generate detailed, human-readable text summaries of generated stellar systems. (Partially implemented: Current system prints a tabulated summary via `__repr__` methods).
    *   **HTML Output:** Create HTML pages for systems, potentially including graphical representations (see below).
    *   **Graphical System Diagrams:** Integrate capabilities to produce visual system diagrams. (Implemented: An SVG representation of the system is generated when `garnets/garnets.py` is run directly).
    *   **Data Export:** Implement CSV (Comma Separated Values) output for easy data analysis of planetary properties across multiple generated systems.
    *   **Celestia Support:** Add functionality to generate `.ssc` files for importing generated systems into the Celestia space simulator.

*   **Integrate Star Catalog Functionality:**
    *   Develop a system to use predefined star catalogs (e.g., from local files or built-in sets similar to Dole's or SolStation lists in the C version) to seed the generation process with known stars.
    *   Allow iteration through catalog stars to generate their potential planetary systems.

*   **Enhance Logging and Verbosity Controls:**
    *   Expand Python logging for more granular diagnostic output. (Partially implemented: Basic Python `logging` is used; however, the C version's `flag_verbose` bitmask system for fine-grained control is not present).

*   **Add Advanced Filtering and System Analysis:**
    *   Implement mechanisms to filter generated systems and perform analyses. (Minimally implemented: Planets are classified with types, but capabilities for filtering collections of systems based on criteria or summarizing statistics across batches are not yet developed).

*   **Implement Seed System Functionality:**
    *   Allow the use of predefined planetary configurations (like the Solar System or other known exoplanetary systems) as a "seed" or template to influence or directly replicate certain aspects during the generation of new systems.

*   **Review and Refine Simulation Depth for Specific Scenarios:**
    *   Further investigate and potentially implement more detailed checks or logging for specific scenarios, such as the conditions for habitability on moons of gas giants or the specific criteria that defined "Sphinx-like" planets in the original.

## Remaining Tasks and TODOs

**For `chemtable.py`:**
*   The accuracy of `melt` and `boil` points for gases is an area for future enhancement, potentially using phase diagrams that consider pressure variations (current model detailed in `docs/chemtable.md`).
*   Modeling of complex chemical reactions between atmospheric gases and planetary surfaces is a planned area of development.
*   The `abunde` and `abunds` gas abundance metrics are documented in `docs/chemtable.md` based on current code structure; their precise distinction may be refined in future model updates.

**For `constants.py`:**
*   The `constants.py` file may be refactored in the future for improved organization.
*   The documentation for several physical and simulation constants (including various coefficients, albedos, and `FREEZING_POINT_OF_WATER`) has been updated in `docs/constants.md` to reflect their current usage; their derivations and sources are areas for ongoing review and documentation enhancement.

**For `enviroment.py`:**
*   The `enviroment.py` file is extensive and may be refactored in the future for better modularity.
*   Several functions and enumerations within `enviroment.py` (such as those related to `PlanetType` definitions, orbital zones, density calculations, escape velocity, atmospheric processes, and temperature iteration) are documented in `docs/enviroment.md` reflecting their current implementation. These areas are subject to ongoing review for model refinement and enhanced physical accuracy (e.g., implementation of full Jeans Escape for `gas_life`, review of the `min_molec_weight` model, ensuring unit consistency in `PlanetType` logic).

**For `stellar_system.py`:**
*   The attributes within the `Planet` class are documented in `docs/stellar_system.md`; their structure and initialization are part of ongoing efforts to optimize clarity and simulation accuracy.
*   Properties of the `Star` class (like `luminosity_ratio`, `stellar_dust_limit`, `r_ecosphere`, `life`) are described in `docs/stellar_system.md`; their calibration against the latest astrophysical models is an area for future refinement.
*   The usage of a global `STAR_MASS` constant as a placeholder in some calculations is noted in `docs/stellar_system.md`. Future development aims to consistently use the specific `Star` object's mass.
*   Properties of the `Planetoid` class (such as `reduced_mass`, effect limits, `critical_mass`) are documented in `docs/stellar_system.md` based on their current implementation; these are subject to ongoing model review.

**For `garnets.py` (related to source code):**
*   The `random_star()` function (detailed in `docs/garnets.md`) currently uses a basic model for star generation. Future enhancements include adding a seed parameter for reproducibility and incorporating more realistic stellar property distributions.
