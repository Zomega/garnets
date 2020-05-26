# Kothari Radius

There's one particular bit of StarGen deep magic that took some time to port.

After accretion, there's a function, "`kothari_radius`", that's used to find the
size of the planet from just its mass and some metadata. Its very tangled, and
the rationale is unclear.

The original StarGen documentation says the following:

> Returns the radius of the planet in kilometers. The mass passed in is in
> units of solar masses. This formula is listed as eq.9 in Fogg's article,
> although some typos crop up in that eq. See
> "The Internal Constitution of Planets", by Dr. D. S. Kothari, Mon. Not. of
> the Royal Astronomical Society, vol 96 pp.833-843, 1936 for the derivation.
> Specifically, this is Kothari's eq.23, which appears on page 840.                                     

I ran into troubles porting it because the units of various constants are
somewhat unclear (cgs can do that to you).

I was able to locate a copy of the original paper, but the units are
somewhat unclear there too. However, I was able to find that equations
25, 26, and 26' are capable of reproducing the results of eq 23 in a much
more comprehesible way. This is what I used in this implementation.

## Developing an intuition

The basic thrust of Kothari's paper is that there are two competing forces
that affect "cold body" (e.g. planetary) size -- gravitation, and
intermolecular repulsion. For a given material, these forces compete -- when
the planet is sufficiently small, the repulsive forces dominate, but after a
certian point gravity begins to force the molecules ever closer together.

This implies, in particular, that there might be a maximum planetary size
(especially since, as Kothari points out, we know that white dwarfs shrink
in radius as they become more massive).

By considering only the most basic intermolecular forces, Kothari is able to
develop a model of how mass, material, and radius are related.


## Page 840

Equations 21-23 are derived from theory on the previous pages, and give
the radius directly as a function of mass and various observed constants.

Throughout $`Z`$ is the (unitless) average atomic number, $`A`$ is the
(unitless) average atomic weight. $`M`$ is the mass of material composing
the planet (Units are unspecified, but it may be convinent to consider
them as in solar masses ($`M_{\odot}`$) as Kothari does).

```math
R =
\frac{
 \frac{2 \beta}{a_1}
 \frac{\sqrt[3]{M_{\odot}}}{\sqrt[3]{ZA}}
}{
 1 +
 \frac{a_2}{a_1}
 \frac{A^\frac{4}{3}}{Z^2}
 \left( \sqrt[3]{\frac{M}{M_{\odot}}} \right) ^ 2
}
\sqrt[3]{\frac{M}{M_{\odot}}}

```

Equation 23 is what StarGen uses, but Kothari immediately simplified by
determining the maxium radius for a given material, and rewriting in terms
of that. Equations 24-28 summarize this rewriting, and I will reproduce them
here so the code is clear.

First, the mass which produces the maxium radius for the given material
is found by differentiating equation 23.

```math
M_{R_\text{max}}
= {\left( \frac{a_1}{a_2} \right)}^\frac{3}{2} \frac{Z^3}{A^2}
\approx  1.04 \times 10^{-3} \cdot \frac{Z^3}{A^2} \cdot M_{\odot}
```

This produces a maximum radius:

```math
R_\text{max}
= \frac{\beta}{\sqrt{a_1 a_2}} \frac{Z^\frac{2}{3}}{A}
\approx 1.12 \times 10^{10} \cdot \frac{Z^\frac{2}{3}}{A} \cdot \text{cm}
```

Finally, we can substitute these quantities back into equation 21 (A precursor to 23). For clarity, let $`\bar{m} = \frac{M}{M_{R_\text{max}}}`$.

```math
R = R_\text{max} \cdot \frac{
    2\bar{m}^{\frac{1}{3}}
}{
    1 + \bar{m}^{\frac{2}{3}}
}
```

Finally, in equations 27 and 28, Kothari notes the behaviors for extreme masses (when compared to $`M_{R_\text{max}}`$).

When $`M \ll M_{R_\text{max}}`$, $`R \propto \sqrt[3]{\bar{m}}`$. This makes sense as it is the same as the result obtained when the material maintains a constant density (intramolecular repulsion dominates).

Once $`M \gg M_{R_\text{max}}`$, gravity dominates, compressing the material more and more, so  $`R \propto \frac{1}{\sqrt[3]{\bar{m}}}`$.

This is a resonably good match with experimental data, though there are not may cold bodies massive enough to confirm the large mass model.

