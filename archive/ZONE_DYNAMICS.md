# Zone Dynamics & Environmental Systems
## Primordial Garden v0.9.0

## Overview
Zones are distinct environmental regions that shape evolution through energy availability, mutation pressure, and habitat specialization. Each zone type creates unique selective pressures that drive adaptive radiation.

---

## Zone Types

### 1. **Fertile Zone** (Green)
- **Energy Multiplier**: 1.2x base photosynthesis
- **Mutation Rate**: 1.0x (baseline)
- **Reproduction Difficulty**: 1.0x (normal)
- **Characteristics**: Abundant resources, stable environment
- **Selective Pressure**: Favors generalists and colonizers
- **Native Adaptation**: Species born here develop moderate tolerance to all conditions

### 2. **Ocean Zone** (Deep Blue)
- **Energy Multiplier**: 0.9x base photosynthesis
- **Mutation Rate**: 1.1x
- **Reproduction Difficulty**: 1.1x
- **Characteristics**: Moderate resources, fluid environment
- **Selective Pressure**: Favors mobile species and colonial clusters
- **Native Adaptation**: Enhanced movement efficiency, colonial behavior

### 3. **Desert Zone** (Tan/Brown)
- **Energy Multiplier**: 0.6x base photosynthesis
- **Mutation Rate**: 1.3x
- **Reproduction Difficulty**: 1.5x
- **Characteristics**: Scarce resources, extreme temperatures
- **Selective Pressure**: STRONG selection for heat tolerance and efficiency
- **Native Adaptation**: High heat tolerance (0.7-0.9), low energy decay

### 4. **Arctic Zone** (Light Blue)
- **Energy Multiplier**: 0.5x base photosynthesis
- **Mutation Rate**: 1.2x
- **Reproduction Difficulty**: 1.6x
- **Characteristics**: Very scarce resources, freezing conditions
- **Selective Pressure**: EXTREME selection for cold tolerance and clustering
- **Native Adaptation**: High cold tolerance, colonial clustering for warmth

### 5. **Toxic Zone** (Dark Olive Green)
- **Energy Multiplier**: 0.4x base photosynthesis
- **Mutation Rate**: 2.0x (VERY HIGH)
- **Reproduction Difficulty**: 1.8x
- **Characteristics**: Hostile chemistry, rapid evolution
- **Selective Pressure**: EXTREME selection for toxin resistance
- **Native Adaptation**: High toxin resistance (0.7-0.9), rapid mutation rates
- **Special**: Breeding ground for extremophiles and rapid speciation

### 6. **Volcanic Zone** (Brown/Red)
- **Energy Multiplier**: 0.3x base photosynthesis
- **Mutation Rate**: 2.5x (EXTREME)
- **Reproduction Difficulty**: 2.0x
- **Characteristics**: Extreme heat, volcanic chemistry, unstable
- **Selective Pressure**: BRUTAL selection, only hardiest survive
- **Native Adaptation**: Heat + toxin resistance, chemosynthesis potential
- **Special**: Extreme environment drives radical adaptations

---

## Environmental Dynamics

### Energy Availability
Each zone provides different baseline energy through photosynthesis:
```
Energy = base_photosynthesis * zone_multiplier * native_bonus * colony_bonus
```

**Native Bonus**: Species in their native zone get 1.5x reproduction bonus
**Colony Bonus**: Clustering with same species provides 1.0-1.2x energy multiplier

### Population Pressure
Zones have carrying capacity based on energy availability:
```
pressure = zone_energy / (population_density * avg_complexity)
```

Effects:
- **pressure > 1.2x**: Abundant resources, rapid reproduction
- **pressure 0.8-1.2x**: Balanced, stable populations
- **pressure 0.6-0.8x**: Crowded, reproduction slows
- **pressure < 0.6x**: Severe overcrowding, reproduction blocked for weak organisms

### Mutation Pressure
Harsh zones accelerate evolution:
- **Toxic Zone**: 2.0x mutation rate = rapid speciation
- **Volcanic Zone**: 2.5x mutation rate = extreme diversification
- **Desert/Arctic**: 1.3-1.5x = steady adaptation
- **Fertile**: 1.0x = slow, stable evolution

**Why This Matters**: Extremophiles evolve faster in harsh zones, then can colonize easier zones with their adaptations.

---

## Habitat Specialization (Phase 3)

### Native Zone Affinity
- Each species has a `native_zone_type` (zone where their lineage evolved)
- In native zones: **1.5x reproduction threshold bonus**
- Outside native zones: Normal reproduction costs
- Mutation can shift native zone (2% chance) = long-term adaptation

### Zone Transitions
Species can colonize new zones through:
1. **Migration**: Movement into adjacent zones
2. **Adaptation**: Mutations that increase tolerance
3. **Specialization**: Native zone shifts over generations

Example Evolution:
```
Gen 1: Fertile native (generalist) → moves to desert
Gen 50: Acquires heat_tolerance mutation (0.6 → 0.8)
Gen 100: Native zone mutates to "desert" (now specialist)
Result: Desert specialist with 1.5x reproduction there
```

---

## Strategic Movement & Zones

### Energy-Seeking (Complexity 1)
- Moves if zone poor (< 0.8x energy multiplier)
- Seeks better zones for photosynthesis
- Responds to: zone energy multiplier, population pressure

### Flee (Complexity 2)
- Flees predators across zones
- Also flees poor zones when energy low
- Zone boundaries offer escape routes

### Hunt (Complexity 3+)
- Pursues prey across zone boundaries
- Must balance hunting cost vs zone energy
- Predators can drive prey into harsh zones

---

## Ecological Interactions by Zone

### Competition
Species with overlapping niches compete more intensely in resource-poor zones:
- **Desert/Toxic**: Intense competition for scarce energy
- **Fertile**: Many niches available, less competition

### Predator-Prey Dynamics
Zone type affects hunting success:
- **Open zones** (ocean, fertile): Easier to hunt
- **Complex zones** (toxic, volcanic): Easier to hide

### Colonization Patterns
1. **Fertile → Desert**: Generalists test heat tolerance
2. **Desert → Toxic**: Heat-adapted species try toxin resistance
3. **Toxic → Volcanic**: Extremophiles challenge ultimate environment

---

## Reading the Visualization

### Cell Colors (NEW v0.9.0)
Colors encode species traits:

**HUE** (color family):
- **Green**: Photosynthesizers (complexity 1)
- **Cyan**: Advanced photosynthesizers (complexity 2)
- **Yellow**: Opportunists (complexity 2)
- **Orange**: Predators (complexity 3)
- **Red**: Apex predators (complexity 4+)

**SATURATION** (vividness):
- **Vivid**: Specialists (high zone adaptation)
- **Muted**: Generalists (low zone adaptation)

**BRIGHTNESS**:
- **Bright**: High energy level
- **Dim**: Low energy level

### Zone Backgrounds
- **Forest Green**: Fertile (abundant)
- **Midnight Blue**: Ocean (moderate)
- **Tan**: Desert (harsh)
- **Powder Blue**: Arctic (extreme)
- **Dark Olive**: Toxic (hostile)
- **Saddle Brown**: Volcanic (brutal)

---

## Key Insights

### 1. Harsh Zones Drive Evolution
Extreme environments (toxic, volcanic) have high mutation rates, creating biodiversity hotspots. Species that evolve there gain adaptations useful elsewhere.

### 2. Energy Gradients Shape Behavior
Organisms naturally migrate from poor to rich zones unless specialized for harsh environments.

### 3. Specialists vs Generalists
- **Specialists**: Thrive in native zone, struggle elsewhere
- **Generalists**: Moderate performance everywhere
- **Trade-off**: Specialization power vs adaptability

### 4. Zone Boundaries = Ecological Frontiers
Where different zones meet, you see:
- Highest species diversity
- Predator ambush points
- Migration corridors
- Evolutionary experimentation

---

## Design Philosophy

Zones create **environmental heterogeneity** that:
1. Prevents global monocultures (different winners in each zone)
2. Creates adaptive radiation (specialists fill niches)
3. Drives complex food webs (predators follow prey across zones)
4. Enables boom-bust cycles (migration between rich/poor zones)

The simulation isn't about one "best" organism - it's about creating an ecosystem where many strategies succeed in different contexts.
