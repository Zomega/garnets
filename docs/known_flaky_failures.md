# Known Flaky Failures

Known stack traces for failures that seem to occur only some of the time.

```
Traceback (most recent call last):
  File "garnets/garnets.py", line 716, in <module>
    system = generate_stellar_system(random_star())
  File "garnets/garnets.py", line 92, in generate_stellar_system
    for p in protoplanets
  File "garnets/garnets.py", line 93, in <listcomp>
    if p.mass > 0*kg
  File "garnets/garnets.py", line 575, in generate_planet
    iterate_surface_temp(planet)
  File "/Users/woursler/Code/garnets/garnets/enviroment.py", line 783, in iterate_surface_temp
    calculate_surface_temp(planet, True, 0, 0, 0, 0, 0)
  File "/Users/woursler/Code/garnets/garnets/enviroment.py", line 690, in calculate_surface_temp
    planet.boil_point = boiling_point(planet.surf_pressure)
  File "/Users/woursler/Code/garnets/garnets/enviroment.py", line 380, in boiling_point
    ) * K
  File "/Users/woursler/Code/xatu/xatu/core.py", line 389, in dimensionless_with_units
    assert_dimensionally_consistent(quantity, unit)
  File "/Users/woursler/Code/xatu/xatu/core.py", line 382, in assert_dimensionally_consistent
    raise UnitsError(quantity.unit, unit)
xatu.core.UnitsError: Units do not match!
```