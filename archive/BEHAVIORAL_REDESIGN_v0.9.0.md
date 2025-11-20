# v0.9.0 Behavioral Redesign: Unified Movement & Colonial Intelligence

## Problem Statement

The previous system had fundamental design flaws:

1. **Movement was optional** (`can_move: bool = False`) - Most cells were static
2. **Intelligence was disconnected** - Strategy flags existed but didn't integrate with complexity
3. **Predation was a binary flag** (`is_predator: bool`) - Not emergent from organism development
4. **No colonial behavior** - Cells didn't benefit from clustering with their own species
5. **Population collapse** - Simulations ended in extinction (122→0 cells by gen 360)

## Core Philosophy Change

**OLD**: Organisms have flags that determine behavior  
**NEW**: Behavior emerges from organism complexity and environmental context

## Changes Implemented

### 1. Universal Movement (All Organisms Mobile)

**Before:**
```python
can_move: bool = False  # Most organisms couldn't move
movement_cost: int = 5
```

**After:**
```python
# ALL organisms can move (bacteria drift, cells swim, complex organisms hunt)
movement_cost: int = 3  # Auto-calculated: 2 + complexity
# Complexity 1: 3 energy/move (drift)
# Complexity 2: 4 energy/move  
# Complexity 3: 5 energy/move (active hunting)
```

**Rationale:** Even single-celled bacteria exhibit chemotaxis and drift. Movement is universal in life.

### 2. Complexity-Driven Intelligence (Emergent Strategies)

**Before:**
```python
movement_strategy: str = "random"  # Manual flag
is_predator: bool = False  # Manual flag
```

**After:**
```python
def get_movement_strategy(self) -> str:
    if complexity == 1: return "energy_seeking"  # Phototropism/chemotaxis
    elif complexity == 2: return "flee"          # Danger sensing
    else: return "hunt"                          # Active predation (3+)

def can_hunt(self) -> bool:
    return complexity >= 3  # Hunting requires sophistication

def get_hunting_efficiency(self) -> float:
    return min(0.8, 0.35 + (complexity * 0.15))
    # Complexity 3: 50% efficiency
    # Complexity 4: 65% efficiency
    # Complexity 5: 80% efficiency
```

**Behavior Progression:**
- **Complexity 1** (Single cells): Seek energy sources (sunlight, nutrients)
- **Complexity 2** (Simple organisms): Can sense and flee from danger
- **Complexity 3** (Complex organisms): Can hunt prey (50% energy transfer)
- **Complexity 4+** (Advanced): Better hunting (65-80% efficiency)

### 3. Colonial Clustering (Emergent Group Behavior)

**NEW Traits:**
```python
colonial_affinity: float = 1.2         # Energy bonus when adjacent to same species (1.0-1.5x)
cluster_reproduction_bonus: float = 1.3 # Reproduction boost in colonies (1.0-2.0x)
```

**Energy Bonus:** Cells surrounded by same-species neighbors gain up to 20-50% more energy
```python
def _get_colony_bonus(x, y, species_id, species):
    same_species_ratio = same_neighbors / total_neighbors
    return 1.0 + (same_species_ratio * (colonial_affinity - 1.0))
```

**Reproduction Bonus:** Clusters of 3+ same-species cells reproduce easier
```python
def _get_cluster_reproduction_bonus(x, y, species_id, species):
    cluster_size = count_same_species_neighbors(x, y)
    cluster_ratio = min(1.0, cluster_size / 3.0)
    return 1.0 + (cluster_ratio * (cluster_reproduction_bonus - 1.0))
```

**Expected Emergence:**
- Cells form beneficial same-species clusters
- Colony centers have high energy and reproduction rates
- Peripheral cells compete with other species
- Natural selection favors organisms that cluster together

### 4. Integrated Predation System

**Before:**
```python
if species.traits.is_predator:
    hunt_prey()
```

**After:**
```python
if species.traits.can_hunt():  # complexity >= 3
    efficiency = species.traits.get_hunting_efficiency()
    energy_gained = prey.energy * efficiency
```

**Progressive Hunting:**
- Complexity 1-2: Cannot hunt (photosynthesis/flee only)
- Complexity 3: Basic hunting (50% energy transfer)
- Complexity 4: Improved hunting (65% transfer)
- Complexity 5: Advanced hunting (80% transfer)

**Prevents:**
- Cannibalism (can't eat same species)
- Simple organisms from hunting (requires complexity)
- Static cells from being predators

## Expected Behavioral Changes

### Before v0.9.0:
```
Gen 10:  122 cells (mix of static and mobile)
Gen 50:  116 cells (0 births, 0 deaths - static patterns)
Gen 100: 36 cells (gradual decline)
Gen 360: 0 cells (extinction)
```

**Problem:** Static cells formed Conway patterns. No movement, no interaction, no dynamics.

### After v0.9.0:
```
Gen 10:  120 cells (ALL mobile, seeking energy)
Gen 50:  135 cells (clusters forming, active reproduction)
Gen 100: 142 cells (colonies established, some hunters)
Gen 360: 158 cells (dynamic equilibrium, territorial boundaries)
```

**Expected:** 
- All cells actively seeking better zones
- Colonial clusters forming naturally
- Complex organisms hunting simpler ones
- Territorial competition between species
- Dynamic population oscillations (not stasis or extinction)

## Migration Guide

### Removed Traits:
- `can_move` - DELETE (all organisms move now)
- `movement_strategy` - DELETE (auto-determined by complexity)
- `is_predator` - DELETE (use `can_hunt()` method)

### New Traits:
- `colonial_affinity: float = 1.2` - Energy bonus from same-species neighbors
- `cluster_reproduction_bonus: float = 1.3` - Reproduction bonus in colonies

### Updated Methods:
- `SpeciesTraits.get_movement_strategy()` - Returns strategy based on complexity
- `SpeciesTraits.can_hunt()` - True if complexity >= 3
- `SpeciesTraits.get_hunting_efficiency()` - Returns efficiency based on complexity
- `Grid._get_colony_bonus()` - Calculates energy bonus from clustering
- `Grid._get_cluster_reproduction_bonus()` - Calculates reproduction bonus

### Old Preset Species:
```python
# v0.8.0 - WRONG
traits = SpeciesTraits(
    can_move=True,
    movement_strategy="hunt",
    is_predator=True,
    ...
)
```

### New Preset Species:
```python
# v0.9.0 - CORRECT
traits = SpeciesTraits(
    complexity=3,  # Auto-enables hunting
    colonial_affinity=1.2,
    cluster_reproduction_bonus=1.3,
    ...
)
# Movement and hunting emerge from complexity!
```

## Technical Details

### Files Modified:
1. `enhanced_engine/species_enhanced.py`:
   - Removed `can_move`, `movement_strategy`, `is_predator` traits
   - Added `colonial_affinity`, `cluster_reproduction_bonus` traits
   - Added `get_movement_strategy()`, `can_hunt()`, `get_hunting_efficiency()` methods
   - Removed `_mutate_movement_strategy()` method
   - Updated `mutate()` to work with new system

2. `enhanced_engine/cell.py`:
   - Removed `can_move` check (all cells can move if they have energy)

3. `enhanced_engine/grid.py`:
   - Updated `process_movement()` to use `get_movement_strategy()`
   - Updated `process_predation()` to use `can_hunt()` and `get_hunting_efficiency()`
   - Added `_get_colony_bonus()` for energy clustering bonus
   - Added `_get_cluster_reproduction_bonus()` for reproduction clustering bonus
   - Integrated colony bonuses into `process_aging()` and `process_reproduction()`

4. `main_enhanced.py`:
   - Updated all preset species to remove old flags
   - Added colony traits to presets

### Complexity → Behavior Mapping:
```python
COMPLEXITY_BEHAVIORS = {
    1: {
        "movement": "energy_seeking",  # Phototropism, chemotaxis
        "can_hunt": False,
        "movement_cost": 3,
        "description": "Single-celled, seeks nutrients"
    },
    2: {
        "movement": "flee",           # Danger detection
        "can_hunt": False,
        "movement_cost": 4,
        "description": "Simple organism, flees predators"
    },
    3: {
        "movement": "hunt",           # Active predation
        "can_hunt": True,
        "hunting_efficiency": 0.50,
        "movement_cost": 5,
        "description": "Complex organism, hunts prey"
    },
    4: {
        "movement": "hunt",
        "can_hunt": True,
        "hunting_efficiency": 0.65,
        "movement_cost": 6,
        "description": "Advanced hunter"
    },
    5: {
        "movement": "hunt",
        "can_hunt": True,
        "hunting_efficiency": 0.80,
        "movement_cost": 7,
        "description": "Apex predator"
    }
}
```

## Testing Checklist

- [x] Code compiles without errors
- [ ] All organisms move (even complexity 1)
- [ ] Complexity 1 organisms seek energy
- [ ] Complexity 2 organisms flee from predators
- [ ] Complexity 3+ organisms hunt prey
- [ ] Same-species clusters form naturally
- [ ] Clusters have higher energy gain
- [ ] Clusters have higher reproduction rates
- [ ] Hunting efficiency scales with complexity
- [ ] No more static cells
- [ ] No more population extinction
- [ ] Dynamic territorial competition emerges

## Expected Simulation Dynamics

### Early Game (Gen 0-50):
- Random seeding → all cells actively seeking better zones
- Movement toward energy-rich zones (paradise, fertile)
- Initial deaths from movement cost + poor positioning

### Mid Game (Gen 50-200):
- Colonial clusters forming in optimal zones
- Complexity 2 organisms fleeing from complexity 3+ hunters
- Territorial boundaries emerging between species
- Competition for prime real estate

### Late Game (Gen 200+):
- Stable colonies with high reproduction rates
- Complex predators hunting around colony edges
- Continuous evolution of hunting efficiency
- Dynamic equilibrium (not stasis!)

## Success Metrics

**v0.8.0 (Before):**
- Gen 360: 0 cells (extinction)
- 0% movement rate
- Static Conway patterns

**v0.9.0 (Target):**
- Gen 360: 100+ cells (sustainable)
- 100% movement rate (all cells mobile)
- Dynamic territorial colonies
- Active predator-prey cycles
- No extinction events

---

**Version:** 0.9.0  
**Date:** November 19, 2025  
**Status:** Implementation Complete, Testing Required
