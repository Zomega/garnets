# Porting Whole-Planet Evolution (Gilbert-Janizek et al. 2026 / VPLanet) into `garnets`

This document outlines how to port the coupled 1D interior–surface–ocean–climate evolution model from **Gilbert-Janizek et al. (2026)** (*"A Whole-planet Model of the Earth without Life for Terrestrial Exoplanet Studies"*, PSJ 7:216; [PDF](references/Gilbert-Janizek_2026_Planet._Sci._J._7_216.pdf)) into `garnets`.

---

## 1. Reference Repositories in `docs/references/`

All external codebases referenced by Gilbert-Janizek et al. (2026) have been cloned into gitignored directories under `docs/references/`:

| Directory | Upstream Repository | Role in Gilbert-Janizek et al. (2026) |
| :--- | :--- | :--- |
| [`docs/references/vplanet-samrosegilbert/`](references/vplanet-samrosegilbert/) | `samrosegilbert/vplanet` (`samdev` branch) | Lead author's fork containing the C implementation of the coupled carbon cycle (Foley 2015), deep water cycle (Seales & Lenardic 2020), and moisture/precipitation partitioning (Driscoll & Bercovici 2013) inside [`src/thermint.c`](references/vplanet-samrosegilbert/src/thermint.c) and [`src/thermint.h`](references/vplanet-samrosegilbert/src/thermint.h). |
| [`docs/references/vplanet/`](references/vplanet/) | `VirtualPlanetaryLaboratory/vplanet` (`main`) | Upstream VPLanet framework containing base `ThermInt` ([`src/thermint.c`](references/vplanet/src/thermint.c)), `RadHeat` ([`src/radheat.c`](references/vplanet/src/radheat.c)), `Stellar` ([`src/stellar.c`](references/vplanet/src/stellar.c)), `AtmEsc` ([`src/atmesc.c`](references/vplanet/src/atmesc.c)), and `MagmOc` ([`src/magmoc.c`](references/vplanet/src/magmoc.c)). |
| [`docs/references/photochem/`](references/photochem/) | `Nicholaswogan/photochem` | Photochemical & radiative-convective climate package (Wogan et al. 2025b) providing the `Clima` module used in Section 3.8. |
| [`docs/references/clima/`](references/clima/) | `Nicholaswogan/clima` | Standalone two-stream correlated-$k$ radiative-convective climate model (`AdiabatClimate`) used to compute OLR and ASR grids. |
| [`docs/references/picaso/`](references/picaso/) | `natashabatalha/picaso` | Radiative-transfer code used in Section 3.9 to generate synthetic HWO reflected-light spectra. |

### Differences Between `vplanet-samrosegilbert` (`samdev`) and the Published Paper

The `samdev` branch in [`docs/references/vplanet-samrosegilbert/`](references/vplanet-samrosegilbert/) ends at commit `1edaec7` (*"last commit before handoff to vplanet-private"*, Oct 2024). Comparing [`src/thermint.c`](references/vplanet-samrosegilbert/src/thermint.c) against Section 3 of the 2026 paper reveals exactly what is already in C versus what was finalized in `vplanet-private` (and is fully specified mathematically in the paper):

1. **Already in `vplanet-samrosegilbert/src/thermint.c`**:
   - Core and mantle thermal evolution (`fdTDotMan`, `fdTDotCore`), thermal boundary layers (`fdBLUMan`, `fdBLLMan`), cubic solidus–geotherm intersection (`cubicroot`, `fdDepthMeltMan`, `fdFMeltUMan`), Costa et al. (2009) melt-viscosity reduction (`fdMeltfactorUMan`), inner-core growth (`fdRIC`, `fdRICDot`), core buoyancy fluxes, magnetic dipole moment (`fdMagMom`), and magnetopause radius (`fdMagPauseRad`).
   - Foley (2015) 3-reservoir carbon cycle ODEs (`fdDCarbManDtThermint`, `fdDCarbPlateDtThermint`, `fdDCarbSurfDtThermint`) and fluxes (`fdCarbSubFlux`, `fdCarbArcFlux`, `fdCarbDegasFlux`, `fdCarbSFWFlux`, `fdCarbWeathFlux`).
   - Seales & Lenardic (2020) deep water cycle ODEs (`fdDWaterManDtThermint`, `fdDWaterOceanDtThermint`, `fdDWaterAtmDtThermint`) and fluxes (`fdPlateSpeedSeales`, `fdWaterInMelt`, `fdSerpLayerThickness`, `fdWaterMORFlux`, `fdWaterSubFlux`).
2. **Upgraded in the 2026 Paper (Equations 9, 15, 21–34)**:
   - **Water-weakened mantle viscosity (Eq. 15):** `fdViscUManArr` in `samdev` only uses temperature activation $\exp(E_{a,\text{man}} / R_g T_{\text{UM}})$; Eq. 15 subtracts water-weakening $E_{\text{H}_2\text{O}} (w_{\text{man}} / M_{\text{man}}) / (R_g T_{\text{UM}})$.
   - **Temperature-dependent seafloor weathering (Eq. 9):** `fdCarbSFWFlux` in `samdev` implements Eq. 8; the paper multiplies by the Krissansen-Totton et al. (2018) Arrhenius factor $\exp[\frac{E_{\text{bas}}}{R_g}(\frac{1}{T_{\text{pore},0}} - \frac{1}{T_{\text{pore}}})]$.
   - **Calcite-saturated ocean carbonate speciation (Eqs. 21–29):** `fdPartialCO2` in `samdev` uses a fixed effective `CO2SOLUBILITY`; the paper solves Henry's law coupled with Millero (2005) / Pilson (2012) carbonate dissociation ($(\text{CO}_2)_{\text{aq}}, [\text{HCO}_3^-], [\text{CO}_3^{2-}], \text{DIC}, \text{pH}$) assuming calcite saturation ($\Omega_{\text{cal}} / [\text{Ca}^{2+}] = 408.1\text{ kg mol}^{-1}$).
   - **Surface & Eddington Cloud Albedo (Eqs. 30–34):** Replaces constant `ALBEDO` with conical-basin ocean fraction $x_{\text{oc}}(w_{\text{ocean}})$, ice fraction $x_i(T_{\text{surf}}, x_{\text{oc}})$, rock fraction $x_r$, and two-stream Eddington cloud reflectivity $\phi$.
   - **Radiative-Convective Climate Grid (Section 3.8):** Replaces the gray-atmosphere ODE `fdDTSurfDtThermint` with Brent root-finding ($\text{ASR}(T_{\text{surf}}) = \text{OLR}(T_{\text{surf}})$) over a 6D precomputed `Clima` lookup table.

---

## 2. Conceptual Comparison: Current `garnets` vs. Gilbert-Janizek (2026)

Currently, [`garnets/garnets.py`](../garnets/garnets.py) and [`garnets/enviroment.py`](../garnets/enviroment.py) characterize rocky planets in [`generate_planet()`](../garnets/garnets.py#L391-L696) using a **single-snapshot empirical equilibrium** at `star.age` derived from Dole (1964), Hart (1978), and Fogg (1985):

```
Current garnets rocky planet pipeline (Static Snapshot at t = star.age):
  Protoplanet (mass, orbit) + Star (mass, age, static luminosity)
    --> kothari_radius() & volume_density()
    --> day_length() & min_molec_weight()
    --> vol_inventory() [Fogg eq. 17 heuristic]
    --> surf_pressure [currently hardcoded to 1 atm in garnets.py:547!]
    --> iterate_surface_temp() [26-step fixed-point loop over hydro/cloud/ice/albedo + gray green_rise()]
    --> calculate_gases() [heuristic retention & reactivity rules in garnets.py:252]
```

Several open `TODO(woursler)` comments in [`garnets/enviroment.py`](../garnets/enviroment.py) and [`garnets/garnets.py`](../garnets/garnets.py) highlight the limitations of this approach:
- `vol_inventory` ([`enviroment.py:325`](../garnets/enviroment.py#L325)): *"There is, best I can tell, an extremely poor justification for this number."*
- `surf_pressure` ([`garnets.py:547`](../garnets/garnets.py#L547)): `planet.surf_pressure = 1 * atm` (Fogg's `pressure()` was disabled because `vol_inventory` produces unrealistic pressures).
- `green_rise` & `opacity` ([`enviroment.py:484-576`](../garnets/enviroment.py#L484-L576)): Gray optical depth depends only on `min_molec_weight` and total `surf_pressure`, not actual $\text{CO}_2$ and $\text{H}_2\text{O}$ partial pressures.
- `calculate_gases` ([`garnets/chemtable.py:3`](../garnets/chemtable.py#L3)): *"does not consider reactions, either among gases in an atmosphere, or with regards to fixing in the crust."*
- Core & magnetic field: `Planet` has `core_radius = kothari_radius(...)`, but no internal heat flow, mantle convection, plate speed, or magnetic dynamo.

Porting Gilbert-Janizek et al. (2026) replaces those heuristics with a **coupled time-evolving ODE system** integrated from post-magma-ocean solidification ($t_0 = 50\text{ Myr}$) to `star.age`:

```
Proposed Whole-Planet Evolution Pipeline (ODE Integration t = 50 Myr -> star.age):
  State Vector y(t) = [T_man, T_core, c_man, c_plate, c_surf, w_man, w_surf]
    |
    +--> 1. Stellar Forcing: L_star(t), T_star(t), F_star(t) at orbit.a
    +--> 2. Radiogenic Heating: Q_rad,man(t), Q_rad,core+BMO(t) (40K, 232Th, 235U, 238U)
    +--> 3. Interior & Dynamo: T_UM, T_CMB, delta_UM, f_UM, d_melt, nu_UM(T_UM, w_man, f_UM),
    |                          Ra, plate speed v(Ra), R_IC, magnetic moment M, R_mp
    +--> 4. Surface & Ocean Partitioning:
    |       - Conical basin ocean fraction x_oc(w_ocean), ice fraction x_i(T_surf), rock x_r
    |       - Eddington cloud fraction phi(pH2O) & total albedo A_T(x_r, x_oc, x_i, phi)
    |       - Air-sea equilibrium: w_surf -> (w_ocean, w_atm, pH2O)
    |       - Calcite-saturated carbonate system: c_surf -> (pCO2, [CO2]_aq, [HCO3-], [CO3^2-], DIC, pH)
    +--> 5. Climate Solver: Solve ASR(T_surf, pCO2, pH2O, F_star, T_star, A_T) = OLR(T_surf, pCO2, pH2O)
    +--> 6. Geochemical Fluxes:
            - Carbon: F_sub,c, F_arc, F_degas, F_sfw(pCO2, v, T_surf), F_weather(pCO2, T_surf, x_r)
            - Water:  F_MOR(f_UM, d_melt, v, w_man), F_sub,w(T_surf, q_m, v)
            --> Returns dy/dt = [dT_man/dt, dT_core/dt, dc_man/dt, dc_plate/dt, dc_surf/dt, dw_man/dt, dw_surf/dt]
```

---

## 3. Subsystem-by-Subsystem Porting Guide

### 3.1. Scaling Earth Constants to Arbitrary Rocky Planets in `garnets`

In [`vplanet-samrosegilbert/src/thermint.h`](references/vplanet-samrosegilbert/src/thermint.h#L19-L80), interior geometry and mass reservoirs are hardcoded to Earth values (`EMASS`, `ERADIUS`, `ERCORE`, `GRAVSURF`). In `garnets`, `accrete.py` generates rocky planets of varying mass $M_p$ and radius $R_p$. When porting to Python, encapsulate planet structure in a `PlanetaryInteriorConfig` derived from the `Planet` instance:

- **Planet mass & radius:** $M_p = \text{planet.mass}$, $R_p = \text{planet.radius}$, $A_{\text{surf}} = 4\pi R_p^2$, $g_{\text{surf}} = \text{planet.surf\_grav}$.
- **Core mass & radius:** Use $M_{\text{core}} = f_{\text{core}} M_p$ (with Earth baseline $f_{\text{core}} = 0.325$, or iron/silicate fractionation by orbital zone) and $R_{\text{core}} \approx R_p (R_{\text{core},\oplus}/R_\oplus) \approx 0.546 R_p$ (or Kothari iron-core radius), giving mantle thickness $D_{\text{man}} = R_p - R_{\text{core}}$, mantle mass $M_{\text{man}} = M_p - M_{\text{core}}$, and mantle volume $V_{\text{man}} = \frac{4}{3}\pi (R_p^3 - R_{\text{core}}^3)$.
- **Trench/ridge length $L$:** Scale with planetary surface area or circumference: $L = L_\oplus (R_p / R_\oplus)$ where $L_\oplus = 6 \times 10^7\text{ m}$.
- **Initial volatile & radiogenic inventories:** Scale initial radiogenic powers ($^{40}\text{K}, ^{232}\text{Th}, ^{235}\text{U}, ^{238}\text{U}$ in Table 2) with $M_{\text{man}} / M_{\text{man},\oplus}$ and $M_{\text{core}} / M_{\text{core},\oplus}$, and scale initial volatile budgets ($w_{\text{total}}, c_{\text{total}}$) with $M_p / M_\oplus$ (modulated by `accrete.py` condensation/zone factors).

---

### 3.2. Module 1: Stellar Luminosity & Spectral Evolution (`garnets/stellar_evolution.py`)

Currently, [`Star.luminosity_ratio`](../garnets/stellar_system.py#L46-L55) in `stellar_system.py` is a static mass–luminosity power law. Because the carbonate–silicate thermostat responds to the secular brightening of the host star (e.g., solar flux rising ~30% from $943\text{ W m}^{-2}$ at $50\text{ Myr}$ to $1370\text{ W m}^{-2}$ at $4.5\text{ Gyr}$), `Star` needs a time-dependent method `star.luminosity_at(t)` and `star.effective_temp_at(t)`:

1. **Lightweight Analytical Option (Gough 1981 / StarGen scaling):**
   For main-sequence stars, luminosity evolves over main-sequence lifetime $t_{\text{MS}}$ as:
   ```math
   L_\star(t) = \frac{L_{\star,0}}{1 + \frac{2}{5}\left(1 - \frac{t}{t_{\text{MS}}}\right)}
   ```
   (Giving $L_\odot(0) \approx 0.71 L_\odot(4.5\text{ Gyr})$).
2. **Full VPLanet Option (Baraffe et al. 2015 Grids):**
   [`docs/references/vplanet/src/stellar.c`](references/vplanet/src/stellar.c) interpolates precomputed Baraffe et al. (2015) stellar evolution tracks (`src/tracks/`) for $0.07 \le M_\star/M_\odot \le 1.4$ to return $L_\star(t)$, $R_\star(t)$, and $T_{\text{eff},\star}(t)$.

---

### 3.3. Module 2: Radiogenic Heating & Core–Mantle Interior (`garnets/interior.py`)

Ported from [`vplanet-samrosegilbert/src/radheat.c`](references/vplanet-samrosegilbert/src/radheat.c) and [`vplanet-samrosegilbert/src/thermint.c`](references/vplanet-samrosegilbert/src/thermint.c#L6000-L6804):

1. **Radiogenic Heating (`RadHeat` + BMO, Section 3.2 & Table 2):**
   Track four isotopes $i \in \{^{40}\text{K}, ^{232}\text{Th}, ^{235}\text{U}, ^{238}\text{U}\}$ with decay constants $\lambda_i$:
   ```math
   Q_{\text{rad},\text{man}}(t) = \sum_i Q_{\text{man},i,0} e^{-\lambda_i t}, \qquad Q_{\text{rad},\text{BMO+C}}(t) = \sum_i Q_{\text{core},i,0} e^{-\lambda_i t}
   ```
2. **Thermal Boundary Layers & Mantle Temperatures:**
   Given prognostic average mantle temperature $T_{\text{man}}$ and core temperature $T_{\text{core}}$:
   - $T_{\text{UM}} = \epsilon_{\text{UM}} T_{\text{man}}$ (`ADJUMPM2UM = 0.7`), $T_{\text{LM}} = \epsilon_{\text{LM}} T_{\text{man}}$ (`ADJUMPM2LM = 1.3`), $T_{\text{CMB}} = \epsilon_c T_{\text{core}}$ (`ADJUMPC2CMB = 0.8`).
   - Temperature jumps across boundary layers: $\Delta T_{\text{UM}} = T_{\text{UM}} - T_{\text{surf}}$ and $\Delta T_{\text{LM}} = T_{\text{CMB}} - T_{\text{LM}}$.
3. **Water- and Melt-Dependent Viscosity (Equations 15–18 & `fdMeltfactorUMan`):**
   - Arrhenius kinematic viscosity with water weakening:
     ```math
     \nu_{\text{Arr}} = \nu_{\text{ref}} \exp\left(\frac{E_{a,\text{man}} - E_{\text{H}_2\text{O}} (w_{\text{man}} / M_{\text{man}})}{R_g T_{\text{UM}}}\right)
     ```
   - Upper-mantle melt fraction $f_{\text{UM}} = \text{clip}\left(\frac{T_{\text{UM}} - T_{\text{sol}}(\delta_{\text{UM}})}{T_{\text{liq}}(\delta_{\text{UM}}) - T_{\text{sol}}(\delta_{\text{UM}})}, 0, 1\right)$ and Costa et al. (2009) melt reduction factor $\varepsilon_{\text{melt}}(f_{\text{UM}})$ (Eqs. 16–18; [`thermint.c:6127-6142`](references/vplanet-samrosegilbert/src/thermint.c#L6127-L6142)).
   - Effective viscosities: $\nu_{\text{UM}} = \nu_{\text{Arr}} / \varepsilon_{\text{melt}}$, $\nu_{\text{LM}} = r_\nu \nu_{\text{UM}}$ ($r_\nu = 1.487$ in Table 2).
   - Note: Just as in [`fvPropsAuxThermint` (`thermint.c:2306-2326`)](references/vplanet-samrosegilbert/src/thermint.c#L2306-L2326), loop twice over $(\delta_{\text{UM}}, T_{\text{sol}}, f_{\text{UM}}, \varepsilon_{\text{melt}}, \nu_{\text{UM}})$ at each step because $\delta_{\text{UM}}$ depends on $\nu_{\text{UM}}$ and $f_{\text{UM}}$ depends on $\delta_{\text{UM}}$.
4. **Convection, Melt Depth, and Heat Flows:**
   - Upper/lower TBL thicknesses (`fdBLUMan`, `fdBLLMan` at [`thermint.c:6002-6024`](references/vplanet-samrosegilbert/src/thermint.c#L6002-L6024)):
     ```math
     \delta_{\text{UM}} = \left(\frac{Ra_{\text{crit}} \nu_{\text{UM}} \kappa_{\text{UM}}}{\alpha_{\text{man}} g_{\text{UM}} \Delta T_{\text{UM}}}\right)^{1/3}
     ```
   - Depth of melting $d_{\text{melt}}$: Solve cubic intersection of mantle solidus $T_{\text{sol}}(r) = A_{\text{sol}} r^3 + B_{\text{sol}} r^2 + C_{\text{sol}} r + D_{\text{sol}}$ with the mantle geotherm (`cubicroot` in [`thermint.c:6905-7029`](references/vplanet-samrosegilbert/src/thermint.c#L6905-L7029)).
   - Mantle Rayleigh number $Ra$ (`fdRayleighMan`, [`thermint.c:6227`](references/vplanet-samrosegilbert/src/thermint.c#L6227)) and Seales & Lenardic (2020) plate speed (Eq. 12):
     ```math
     v = \frac{a_2 \kappa}{2(R_{\text{man}} - R_c)} \left(\frac{Ra}{Ra_{\text{crit}}}\right)^{2\beta_2}
     ```
   - Mantle and core temperature ODEs (`fdTDotMan` and `fdTDotCore` at [`thermint.c:6781-6804`](references/vplanet-samrosegilbert/src/thermint.c#L6781-L6804)):
     ```math
     \frac{dT_{\text{man}}}{dt} = \frac{Q_{\text{rad},\text{man}} + Q_{\text{CMB}} + Q_{\text{latent},\text{man}} - Q_{\text{UM}} - Q_{\text{melt}}}{M_{\text{man}} c_{\text{man}}}
     ```
     ```math
     \frac{dT_{\text{core}}}{dt} = \frac{Q_{\text{rad},\text{BMO+C}} - Q_{\text{CMB}}}{M_C c_C - \frac{dM_{\text{IC}}}{dT_C}(L_H + E_G)}
     ```
5. **Inner Core Nucleation & Magnetic Dynamo (`thermint.c:6258-6522`):**
   - Computes inner-core radius $R_{\text{IC}}$ from the intersection of the core adiabat and depressed iron liquidus (`fdRIC`), thermal + compositional buoyancy flux (`fdCoreBuoyTotal`), dipole magnetic moment (`fdMagMom`), and magnetopause standoff distance (`fdMagPauseRad`).

---

### 3.4. Module 3: Deep Carbon & Water Cycles (`garnets/geochemistry.py`)

Ported from [`vplanet-samrosegilbert/src/thermint.c:7158-7391`](references/vplanet-samrosegilbert/src/thermint.c#L7158-L7391) and Sections 3.3–3.4 of the paper:

1. **Carbon Cycle ODEs (Equations 2–10):**
   - Reservoirs: $c_{\text{man}}$, $c_{\text{plate}}$, $c_{\text{surf}}$ (in kg of $\text{CO}_2$).
   - Fluxes:
     - Subduction: $F_{\text{sub},c} = 2 c_{\text{plate}} v L \frac{d_{\text{melt}}}{V_{\text{man}}}$ (or divided by oceanic plate area $A_p$ as in `fdCarbSubFlux`).
     - Arc volcanism: $F_{\text{arc}} = (1 - \chi_{\text{sub},c}) F_{\text{sub},c}$.
     - Mid-ocean ridge degassing: $F_{\text{degas}} = 2 f_{\text{UM}} \chi_{\text{degas},c} c_{\text{man}} \frac{v L d_{\text{melt}}}{V_{\text{man}}}$.
     - Temperature-dependent seafloor weathering (Eq. 9):
       ```math
       F_{\text{sfw}} = F_{\text{sfw},0} \left(\frac{p\text{CO}_2}{p\text{CO}_{2,0}}\right)^\alpha \left(\frac{v}{v_0}\right) \exp\left[\frac{E_{\text{bas}}}{R_g}\left(\frac{1}{T_{\text{pore},0}} - \frac{1}{T_{\text{pore}}}\right)\right]
       ```
       with $T_{\text{pore}} = 1.02 T_{\text{surf}} - 7.7\text{ K}$.
     - Supply-limited continental silicate weathering (Eq. 10; `fdCarbWeathFlux` at [`thermint.c:7205-7221`](references/vplanet-samrosegilbert/src/thermint.c#L7205-L7221)):
       ```math
       F_{\text{weather}} = F_{\text{weather},s} \left[1 - \exp\left(-\frac{F_{\text{weather},0}}{F_{\text{weather},s}} \frac{x_r}{x_{l,0}} \left(\frac{p\text{CO}_2}{p\text{CO}_{2,0}}\right)^{\beta_1} \left(\frac{P_{\text{sat}}}{P_{\text{sat},0}}\right)^{a_1} \exp\left[\frac{E_a}{R_g}\left(\frac{1}{T_{\text{surf},0}} - \frac{1}{T_{\text{surf}}}\right)\right]\right)\right]
       ```
   - Conservation equations:
     ```math
     \dot{c}_{\text{plate}} = \frac{1}{2} F_{\text{weather}} + F_{\text{sfw}} - F_{\text{sub},c}
     ```
     ```math
     \dot{c}_{\text{man}} = \chi_{\text{sub},c} F_{\text{sub},c} - F_{\text{degas}}
     ```
     ```math
     \dot{c}_{\text{surf}} = F_{\text{arc}} + F_{\text{degas}} - \frac{1}{2} F_{\text{weather}} - F_{\text{sfw}}
     ```

2. **Deep Water Cycle ODEs (Equations 13–20):**
   - Reservoirs: $w_{\text{man}}$, $w_{\text{surf}}$ (in kg of $\text{H}_2\text{O}$).
   - Serpentinized layer thickness: $D_{\text{hydr}} = \frac{k |T_{\text{surf}} - 973\text{ K}|}{q_m}$ (`fdSerpLayerThickness`, [`thermint.c:7312`](references/vplanet-samrosegilbert/src/thermint.c#L7312)).
   - Water mass fraction in melt: $X_{\text{melt}} = \frac{w_{\text{man}} / M_{\text{man}}}{D_{\text{H}_2\text{O}} + f_{\text{UM}}(1 - D_{\text{H}_2\text{O}})}$ (`fdWaterInMelt`, [`thermint.c:7297`](references/vplanet-samrosegilbert/src/thermint.c#L7297)).
   - Fluxes ($S = 2 L v$):
     ```math
     F_{\text{sub},w} = f_h \rho_{\text{man}} D_{\text{hydr}} S \chi_{\text{regas},w}, \qquad F_{\text{MOR}} = \rho_{\text{man}} f_{\text{UM}} X_{\text{melt}} d_{\text{melt}} S \chi_{\text{degas},w}
     ```
   - Conservation equations:
     ```math
     \dot{w}_{\text{man}} = F_{\text{sub},w} - F_{\text{MOR}}, \qquad \dot{w}_{\text{surf}} = F_{\text{MOR}} - F_{\text{sub},w}
     ```

---

### 3.5. Module 4: Ocean Chemistry, Air–Sea Partitioning & Surface Albedo (`garnets/ocean.py`)

Ported from Sections 3.5–3.7 of Gilbert-Janizek et al. (2026) and [`thermint.c:7092-7138`](references/vplanet-samrosegilbert/src/thermint.c#L7092-L7138):

1. **Water Partitioning ($w_{\text{surf}} = w_{\text{ocean}} + w_{\text{atm}}$):**
   - Saturation vapor pressure $P_{\text{sat}}(T_{\text{surf}}) = P_{\text{sat},\text{ref}} \exp\left[-\frac{\bar{m}_w L_w}{R_g}\left(\frac{1}{T_{\text{surf}}} - \frac{1}{T_{\text{sat},\text{ref}}}\right)\right]$ (Eq. 11).
   - Maximum atmospheric moisture $m_{\text{moist}} = \text{RH} \frac{P_{\text{sat}} A_{\text{surf}}}{g_{\text{surf}}}$, so $w_{\text{atm}} = \min(w_{\text{surf}}, m_{\text{moist}})$ and $w_{\text{ocean}} = w_{\text{surf}} - w_{\text{atm}}$.
2. **Carbon Partitioning & Ocean Carbonate Speciation ($c_{\text{surf}} = c_{\text{ocean}} + c_{\text{atm}}$, Eqs. 21–29):**
   - Given $c_{\text{surf}}$, $w_{\text{ocean}}$, and $T_{\text{surf}}$:
     - Temperature- and salinity-dependent equilibrium constants $H(T_{\text{surf}}), k_e(T_{\text{surf}}), k_f(T_{\text{surf}}), K_{\text{sp}}(T_{\text{surf}})$ from Millero (2005) / Pilson (2012) at $S = 35\text{ ppt}$.
     - Carbonate ion fixed by calcite saturation (Eq. 25):
       ```math
       [\text{CO}_3^{2-}] = \frac{\Omega_{\text{cal}}}{[\text{Ca}^{2+}]} K_{\text{sp}}(T_{\text{surf}}), \quad \text{with } \frac{\Omega_{\text{cal}}}{[\text{Ca}^{2+}]} = 408.1\text{ kg mol}^{-1}
       ```
     - Bicarbonate (Eq. 28): $[\text{HCO}_3^-] = \sqrt{(\text{CO}_2)_{\text{aq}} [\text{CO}_3^{2-}] \frac{k_e}{k_f}}$.
     - Total dissolved inorganic carbon: $\text{DIC} = (\text{CO}_2)_{\text{aq}} + [\text{HCO}_3^-] + [\text{CO}_3^{2-}]$.
     - Mass balance $c_{\text{surf}} = c_{\text{atm}}(p\text{CO}_2) + \bar{m}_c w_{\text{ocean}} \text{DIC}(p\text{CO}_2)$ is a quadratic in $\sqrt{p\text{CO}_2}$, yielding $p\text{CO}_2$, $(\text{CO}_2)_{\text{aq}}$, $[\text{HCO}_3^-]$, $\text{DIC}$, and $\text{pH} = -\log_{10}[\text{H}^+]$.
3. **Surface Fractions & Albedo (Section 3.7, Eqs. 30–34):**
   - Conical ocean basin geometry (Driscoll & Bercovici 2013): $x_{\text{oc}}$ scales with $w_{\text{ocean}}^{2/3}$ (calibrated so $x_{\text{oc}} = 0.71$ at $w_{\text{ocean}} = 1\text{ TO}$).
   - Ice fraction: $x_i = 1.0$ if $T_{\text{surf}} \le 240\text{ K}$, else $x_i = x_{i,\text{max}}(1 - x_{\text{oc}})(x_{\text{oc}} / x_{\text{oc},0})$ (or smooth temperature ramp).
   - Exposed rock fraction: $x_r = \max(0.0, 1.0 - x_{\text{oc}} - x_i)$.
   - Ground albedo: $A_g = x_r A_r + x_{\text{oc}} A_{\text{oc}} + x_i A_i$ ($A_r = 0.17, A_{\text{oc}} = 0.10, A_i = 0.60$).
   - Cloud reflectivity $\phi$ via two-stream Eddington approximation (Eqs. 31–34 with $\tau_{\text{cl}} = 4800\text{ Pa}$) and total albedo $A_T = A_g(1 - \phi) + A_{\text{cl}}\phi$ ($A_{\text{cl}} = 0.89$).

---

### 3.6. Module 5: Climate Solver (`garnets/climate.py`)

We should support a **two-tier climate architecture** in `garnets` so the system generator remains fast for multi-planet runs while supporting full radiative-transfer fidelity when desired:

1. **Tier 1 — Fast Analytical Gray/Semi-Gray Radiative Equilibrium (Zero External Dependencies):**
   - Uses the Driscoll & Bercovici (2013) optical depth parameterization already present in [`vplanet-samrosegilbert/src/thermint.c:7419-7433`](references/vplanet-samrosegilbert/src/thermint.c#L7419-L7433) (`OPACITYPRESSH2O = 3931 Pa`, `OPACITYPRESSCO2 = 6.919e4 Pa`), or solves $\text{ASR}(T_{\text{surf}}) = \text{OLR}(T_{\text{surf}}, p\text{CO}_2, p\text{H}_2\text{O})$ via `scipy.optimize.brentq` using a fast polynomial/analytic OLR parameterization (e.g., Kopparapu et al. 2013 / Foley 2015).
2. **Tier 2 — `Clima` Correlated-$k$ Lookup Grid (Full Gilbert-Janizek 2026 Fidelity):**
   - Precompute (or generate on demand via [`docs/references/clima/`](references/clima/)) the 6D `(T_surf, log10_pCO2, log10_PH2O, F_star, A_T, T_star)` OLR and ASR tables described in Section 3.8.
   - Use `scipy.interpolate.RegularGridInterpolator` + `scipy.optimize.brentq` on $[100, 600]\text{ K}$ to find $T_{\text{surf}}$ where $\text{ASR}(T_{\text{surf}}) - \text{OLR}(T_{\text{surf}}) = 0$.

---

## 4. Integration Plan for `garnets`

### Step 1: Add New Focused Modules Under `garnets/`
Rather than expanding [`garnets/enviroment.py`](../garnets/enviroment.py) (which already has a `# TODO(woursler): Break this file up` note at line 59), create modular files:
- `garnets/interior.py` — `RadHeat` + `ThermInt` mantle/core thermal & dynamo calculations.
- `garnets/geochemistry.py` — Foley (2015) carbon cycle + Seales & Lenardic (2020) water cycle fluxes.
- `garnets/ocean.py` — Conical ocean basin, moisture partitioning, and Millero/Pilson calcite-saturated carbonate speciation.
- `garnets/climate.py` — Albedo (Eqs. 30–34) + Tier 1 / Tier 2 `brentq` equilibrium $T_{\text{surf}}$ solver.
- `garnets/evolution.py` — `evolve_terrestrial_planet(planet, star, t_start=50e6*year, t_end=star.age)` wrapping `scipy.integrate.solve_ivp`.

### Step 2: Handle `xatu` Units Cleanly
`garnets` uses `xatu` quantities throughout [`garnets.py`](../garnets/garnets.py) and [`enviroment.py`](../garnets/enviroment.py). Because `scipy.integrate.solve_ivp` evaluates the ODE right-hand side thousands of times per planet:
- Convert `Planet` and `Star` `xatu` quantities to raw SI `float`s (`dimensionless_with_units(...)`) when initializing `evolve_terrestrial_planet()`.
- Run the ODE integration and `brentq` root-finding in pure SI `float`s / NumPy arrays for speed.
- Re-wrap the final evolved state (and optional time-series history `planet.evolution_history`) into `xatu` units (`K`, `atm`, `bar`, `Pa`, `kg`, `km`) when populating `Planet` attributes.

### Step 3: Populate `Planet` Attributes in `generate_planet()`
In [`garnets/garnets.py`](../garnets/garnets.py#L532-L631), for rocky planets (`PlanetType` not a gas giant):
- Call `evolve_terrestrial_planet(planet, star)` instead of the static `vol_inventory()` -> hardcoded `1 * atm` -> `iterate_surface_temp()` chain (or behind a `use_whole_planet_evolution=True` flag).
- Populate existing `Planet` fields directly from the evolved state at `t = star.age`:
  - `planet.surf_temp = T_surf * K`
  - `planet.surf_pressure = (P_N2 + pCO2 + pH2O) * Pa`
  - `planet.albedo = A_T`
  - `planet.hydrosphere = x_oc`
  - `planet.ice_cover = x_i`
  - `planet.cloud_cover = phi`
  - `planet.atmosphere = [(lookup_gas('N2'), P_N2), (lookup_gas('CO2'), pCO2), (lookup_gas('H2O'), pH2O)]`
- Add new interior/ocean/magnetic attributes to [`Planet`](../garnets/stellar_system.py#L211):
  - `planet.mantle_temp`, `planet.core_temp`, `planet.inner_core_radius`
  - `planet.magnetic_moment`, `planet.magnetopause_radius`
  - `planet.plate_speed`, `planet.surface_heat_flow`
  - `planet.ocean_mass`, `planet.ocean_ph`, `planet.ocean_dic`

### Step 4: Validation Test Against Table 3 (Preindustrial Earth)
Create `garnets/whole_planet_test.py` initialized with a $1\,M_\oplus$ planet at $1\text{ AU}$ around a $1\,M_\odot$ star using the Table 2 & Table A1 parameters from Gilbert-Janizek et al. (2026), evolving from $50\text{ Myr}$ to $4.5\text{ Gyr}$, and asserting that the 19 preindustrial Earth observables in Table 3 ($T_{\text{surf}} \approx 286.9\text{ K}$, $p\text{CO}_2 \approx 28.2\text{ Pa}$, $w_{\text{ocean}} \approx 1.4 \times 10^{21}\text{ kg}$, $\text{pH} \approx 8.28$, $T_{\text{UM}} \approx 1561\text{ K}$, $Q_{\text{UM}} \approx 38\text{ TW}$, $R_{\text{IC}} \approx 1221\text{ km}$, $\mathcal{M} \approx 1.01\text{ E.U.}$, etc.) are reproduced within tolerance.
