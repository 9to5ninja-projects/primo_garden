# Primordial Garden v0.4.0 - Quick Start Guide

## What's New in v0.4.0 - The Evolution Update

### 🧬 Environmental Adaptation
Species now have adaptation traits that affect survival in different zones:

- **Heat Tolerance** (0.0-1.0): Survival in desert/hot zones
- **Cold Tolerance** (0.0-1.0): Survival in cold zones  
- **Toxin Resistance** (0.0-1.0): Survival in toxic zones

**Example:**
- Desert-adapted species (heat_tolerance=0.9) gets 1.4x energy in deserts
- Same species in toxic zone (toxin_resistance=0.3) gets only 0.6x energy
- Natural selection favors well-adapted mutations!

### 🌍 Dynamic Environments
Zones now change over time, forcing continuous adaptation:

```python
grid.zone_manager.enable_shifting(interval=100)  # Shift every 100 generations
```

- Zone types can change (Fertile → Toxic, etc.)
- Boundaries shift position
- Sizes expand/contract
- Creates evolutionary pressure

### 🔬 Organism Complexity
Species have sophistication levels affecting energy costs:

- **Complexity** (1-5): How advanced the organism is
- **Metabolic Efficiency** (0.5-2.0): How efficiently it uses energy

**Energy Impact:**
- Complexity 1 (simple): 1.0x energy cost (baseline)
- Complexity 3 (moderate): 1.6x energy cost
- Complexity 5 (advanced): 2.2x energy cost

**Trade-off:** Complex organisms need more energy but can have advanced features (movement, predation, etc.)

### 👥 Sexual Reproduction
Species can evolve sexual reproduction requiring two parents:

- **Sexual species**: Need 2 neighbors of same species to reproduce
- Both parents contribute energy to offspring
- 50% lower mutation rate (genetic stability)
- Can mutate between sexual/asexual modes

### ⚡ Enhanced Energy System
Multi-factor energy calculation:

**Energy Decay:**
```
decay = base_decay × zone_mult × complexity_cost ÷ adaptation_bonus
```

**Energy Gain:**
```
gain = base_photosynthesis × zone_mult × adaptation_bonus ÷ metabolic_efficiency
```

## Running v0.4.0

```bash
python main_enhanced.py
```

### Configuration Options

1. **Grid Size**: Default 200x150
2. **Zone Layout**: Neutral, Random, Quadrants, Ring World
3. **Environmental Shifting**: Enable/disable zone changes
4. **Shift Interval**: How often zones change (default 100 generations)
5. **Species Setup**: Use presets or create custom

### Updated Presets

All presets now include adaptation and complexity:

1. **Balanced**: Simple organism (complexity 1), neutral adaptations
2. **Efficient**: Low metabolism, heat/toxin adapted
3. **Mobile**: Moderate complexity (2), random movement
4. **Resilient**: High energy, excellent all-around adaptation
5. **Predator**: Complex (3), high metabolism, hunting behavior
6. **Seeker**: Moderate complexity (2), energy-seeking, adapted

## Example Scenarios

### Scenario 1: Desert Survivors
- Use **Quadrant zones**
- Enable **shifting** (interval=50)
- Seed **Efficient** (heat-adapted) in top-right
- Watch adaptation traits evolve!

### Scenario 2: Complexity Trade-off
- Create custom species:
  - Simple (complexity=1, high photosynthesis)
  - Complex (complexity=4, can move + predator)
- See which survives with energy constraints

### Scenario 3: Sexual vs Asexual
- Create two similar species:
  - One with `sexual_reproduction=True`
  - One with `sexual_reproduction=False`
- Compare mutation rates and stability

## Key Controls

- **SPACE**: Pause/Resume
- **1-5**: Speed (1x to 100x)
- **G**: Toggle graphs (population, species, events)
- **S**: Export data to CSV
- **Q**: Quit

## Tips for Success

1. **Start simple**: Use presets first to understand mechanics
2. **Watch zones**: Press G to see how zones affect population
3. **Enable shifting**: Makes simulation more dynamic
4. **Mix complexity levels**: Simple and complex species create interesting dynamics
5. **Check exports**: CSV files show detailed adaptation/complexity stats

## Understanding Exports

CSV columns now include:
- `population`: Total living cells
- `species_count`: Number of active species
- `mutations`: Adaptations evolving
- `avg_species_age`: Evolutionary stability

Analyze with:
```bash
python analyze_export.py exports/enhanced_TIMESTAMP.csv
```

## Technical Details

### Adaptation Formula
```python
def get_adaptation_bonus(zone_type):
    if zone_type == "desert":
        return 0.5 + (heat_tolerance * 1.0)  # 0.5x to 1.5x
    elif zone_type == "toxic":
        return 0.3 + (toxin_resistance * 1.2)  # 0.3x to 1.5x
    # ... etc
```

### Complexity Formula
```python
def get_complexity_cost():
    return 1.0 + (complexity - 1) * 0.3
```

### Sexual Reproduction Logic
- Requires `sexual_reproduction=True`
- Checks for 2+ same-species neighbors
- Both parents pay energy cost
- Mutation rate × 0.5

## Troubleshooting

**Everything dies immediately:**
- Random placement doesn't form stable Conway patterns
- Use "center" placement for 2x2 stable blocks
- Increase photosynthesis rate
- Reduce complexity for simpler organisms

**No mutations:**
- Increase base `mutation_rate` (try 0.05-0.1)
- Use zones with high `mutation_rate_mult`
- Ensure population survives long enough

**Zones don't shift:**
- Check `enable_shifting()` was called
- Wait for shift interval generations
- Verify in console output

## Next Steps

- Experiment with custom species traits
- Create extreme specialists (high heat, low cold, etc.)
- Test evolutionary pressure with rapid zone shifting
- Compare sexual vs asexual in unstable environments

Enjoy exploring evolution! 🧬🌍
