# Primordial Garden

An emergent life simulation combining cellular automata with genetic evolution. Watch colorful species evolve, compete, hunt, adapt, age, and die in real-time.

**Eight evolutionary stages:**
- **Classic Mode** (v0.1.0): Pure Conway's Life with species tracking
- **Enhanced Mode** (v0.2.0): Energy system, environmental zones, mobility
- **Predator Mode** (v0.3.0): Intelligent movement, predator/prey dynamics, live graphs! 🦁
- **Evolution Mode** (v0.4.0): Environmental adaptation, sexual reproduction, dynamic zones! 🧬
- **Mortality Mode** (v0.5.0): Aging, death, food webs, environmental pressure! 💀
- **Intelligence Mode** (v0.6.0): Cognitive evolution, strategy mutations, natural emergence! 🧠
- **Ecosystem Mode** (v0.7.0): Carrying capacity, population limits, resource competition! 🌍
- **Habitat Mode** (v0.8.0): **TERRITORIAL EVOLUTION + ADAPTIVE CONWAY RULES!** 🏔️

## Quick Start

### Installation

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

### Running

```bash
# Classic Mode - Simple and fast
run.bat  # or: python main.py

# Habitat Mode - Full ecosystem with territorial evolution!
run_enhanced.bat  # or: python main_enhanced.py
```

## What's New in v0.8.0 - The Habitat Specialization Update 🏔️

### **FINALLY BREAKS CONWAY STASIS!**
Three-pronged attack on geometric pattern locks that froze populations for 1,000+ generations!

### The Problem We Solved
Conway's Life rules created mathematically stable patterns (gliders, oscillators, still lifes) that overpowered ALL biological features:
- ❌ Cells living 1,000+ generations despite aging limits
- ❌ Gen 80-100 stasis: 0 births/deaths for hundreds of generations
- ❌ Intelligence, carrying capacity, energy all failed to break locks

### The Solution: Adaptive Rules + Territory + Chaos

#### 1. Native Zone System 🏔️
**Species evolve home territories and local adaptation!**

```
Seeding → Zone Tracking → Native Zone Assignment
    ↓
"DesertDweller established in desert zone (67/100 cells)"
    ↓
1.5x reproduction bonus in native zones!
```

**How it works:**
- Species assigned native zone based on where most cells were seeded
- `native_zone_affinity`: 1.0-2.0x reproduction multiplier (default 1.5x)
- Lower energy threshold in home territory = territorial advantage
- Can slowly adapt to new zones (2% mutation rate, prefers adjacent zones)

**Expected behavior:**
- Species dominate their native zones
- Struggle to reproduce in foreign territories
- Territorial competition for prime zones
- Migration possible but costly over many generations

#### 2. Energy-Dependent Conway Rules ⚡
**Low energy = unstable patterns = BROKEN STASIS!**

| Energy Level | Survival Rules | Effect |
|--------------|----------------|--------|
| **High (>70%)** | Standard Conway (2-3 neighbors) | Stable patterns possible |
| **Medium (40-70%)** | Conway + 30% death at 4 neighbors | Stress mortality begins |
| **Low (<40%)** | Need 3-4 neighbors (not 2-3!) | **Patterns collapse** |

**Before:** Cells in stable patterns lived forever regardless of energy
**After:** Hungry cells can't maintain patterns → die → energy recovers → growth cycles

**This is the key breakthrough:** Conway geometry only works when cells are healthy!

#### 3. Geometry-Breaking Perturbations 🎲
**Random chaos prevents infinite locks:**
- Old cells (age >50) at max neighbors have 2% death chance per generation
- Subtle enough to preserve dynamics
- Prevents perfect mathematical stability
- Ensures no pattern lives forever

### What You'll See:

**Territorial Behavior:**
```
Gen 50: Species A dominates fertile zone (1.5x bonus)
Gen 100: Species B tries to invade, struggles to reproduce (no bonus)
Gen 150: Species A pushes boundaries into neutral zone
```

**Energy-Driven Dynamics:**
```
Gen 80:  Stable pattern forms, high energy (2-3 neighbors work)
Gen 120: Energy depletes from overcrowding (now need 3-4 neighbors)
Gen 140: Pattern collapses! Mass deaths free up resources
Gen 160: Survivors regrow with fresh energy
```

**No More 1,000+ Generation Locks:**
```
Before: Gen 1730: 72 cells (same for 100+ generations)
After:  Gen 1730: 85 → 62 → 94 → 71 → 89 (constant oscillation)
```

### Technical Details
- New traits: `native_zone_type`, `native_zone_affinity` (SpeciesTraits)
- Energy-dependent rules in `Grid.update()` - checks `energy_ratio`
- Zone tracking in all 3 seeding patterns (random/center/edge)
- Random perturbations: `if age > 50 and neighbors == max: 2% death`
- Comprehensive test suite: `test_habitat_specialization.py` (9/9 passing)

## Previous Updates

### v0.7.0 - The Carrying Capacity Update 🌍

### Complexity-Linked Intelligence
Organisms now **gain cognitive abilities** based on complexity level:

| Complexity | Intelligence | Available Strategies | Example Organisms |
|------------|--------------|---------------------|-------------------|
| **1** | Simple | `random` | Bacteria, single cells |
| **2** | Aware | `random`, `energy_seeking`, `flee` | Insects, simple animals |
| **3** | Strategic | All + `hunt` | Predators, smart animals |
| **4-5** | Advanced | All strategies | Social/intelligent life |

### Strategy Evolution
Movement behaviors now **mutate and evolve**:
- 10% chance per generation to change strategy
- New strategies unlock as complexity increases
- Invalid strategies auto-correct (complexity 1 can't hunt!)
- Species evolve from random → energy_seeking → hunting over time

### Natural Selection for Intelligence
**Intelligence now has survival value**:
- **Simple organisms**: Low cost, dumb behavior → good in stable environments
- **Complex organisms**: High cost, smart behavior → good in harsh environments
- Species in harsh zones naturally evolve higher complexity
- Creates **cognitive arms race**: prey evolve to flee, predators evolve to hunt

**Watch intelligence emerge naturally!** No forced evolution - just natural selection.

## Previous Updates

### v0.5.0 - The Mortality Update 💀

### 1. Aging and Finite Lifespan
Cells now **die of old age**:
- **Max Lifespan**: 150-500 generations (species-specific)
- **Aging Effects**: Energy costs increase up to 50% as cells age
- **Age Decline**: Begins at 70% of lifespan
- Predators: Short-lived (150 gen) | Resilient: Long-lived (500 gen)

### 2. Energy Source Diversification
Three distinct **feeding strategies**:
- **Photosynthesis**: Plants, algae (always gains energy)
- **Predation**: Pure carnivores (2x energy with prey, 0.1x without)
- **Hybrid**: Omnivores (1.5x with prey, 0.7x alone)
- Can **evolve** between strategies (5% mutation chance)

### 3. Environmental Pressure
Harsh survival **outside optimal niches**:
- Desert specialists **thrive in deserts** (heat_tolerance > 0.7)
- Toxic specialists **dominate toxic zones** (toxin_resistance > 0.7)
- Generalists prefer **fertile zones** (balanced tolerances)
- **Starvation threshold**: Die rapidly in wrong environment
- **Optimal zone bonus**: 2.0-2.5x energy in ideal habitat

### 4. Migration & Food Webs
**Predators must hunt or starve**:
- Scans for prey neighbors each generation
- No prey = severe energy penalty (90% reduction)
- Forces migration to prey-rich areas
- Creates natural **predator-prey cycles**
- Multi-level food chains emerge

## Features from v0.4.0 - The Evolution Update 🧬

### 1. Environmental Adaptation
Species evolve **specialized adaptations** to different zones:
- **Heat Tolerance**: Desert survival (0.5x to 1.5x energy)
- **Cold Tolerance**: Arctic/cold zone survival
- **Toxin Resistance**: Thrive in toxic environments (0.3x to 1.5x)
- Well-adapted species **dominate** their niches!

### 2. Dynamic Environments
Zones now **shift and change** over time:
- Zone types transform (Fertile → Toxic, Desert → Paradise)
- Boundaries move and resize
- Forces **continuous adaptation pressure**
- Enable with configurable intervals (default 100 generations)

### 3. Organism Complexity
Energy costs scale with sophistication:
- **Complexity 1-5**: Simple microbes to complex predators
- **Metabolic Efficiency**: 0.5x to 2.0x energy usage
- Complex organisms need **more energy** but unlock advanced features
- Trade-off between efficiency and capabilities

### 4. Sexual Reproduction
Evolve dual-parent reproduction:
- Requires **2 neighbors** of same species
- Both parents contribute energy
- **50% lower mutation** rate (genetic stability)
- Can evolve to/from asexual modes

## Features from v0.3.0 - The Predator Update 🦁

### Intelligent Movement
Cells have **strategic AI**:
- **Energy Seeking**: Moves toward fertile zones
- **Flee**: Detects and avoids predators  
- **Hunt**: Actively pursues prey
- **Random**: Classic random walk

### 2. Predator/Prey System
Complete food chain mechanics:
- Predators consume adjacent prey
- Energy transfer (configurable efficiency)
- Prey death on consumption
- New species presets: Predator & Seeker

### 3. Real-Time Graphs
Press **G** to toggle live visualization:
- Population over time
- Species diversity
- Births/deaths/mutations
- 500-generation history

See `CHANGELOG_v0.3.0.md` for full details!

### Controls

- **SPACE**: Pause/Resume simulation
- **1-5**: Set simulation speed (1x, 5x, 10x, 50x, 100x)
- **S**: Toggle statistics overlay
- **R**: Reset simulation with new random seed
- **Q / ESC**: Quit (will prompt to export data)

## What You're Watching

Each colored cell represents a living organism. Colors indicate species—organisms of the same species share the same color.

**Life Rules (Conway-style):**
- Cells survive if they have 2-3 living neighbors
- New cells are born in empty spaces with exactly 3 living neighbors
- Cells with too few or too many neighbors die

**Evolution:**
- When cells reproduce, there's a small chance of mutation
- Mutations create new species (new colors)
- Species without living members go extinct
- Over time, the most adaptable species dominate

## Presets

The simulation comes with several presets (edit `config/presets.json` to change or add more):

- **primordial_soup** (default): Slow, stable evolution - good for long observation
- **volatile_garden**: High mutation rate, chaotic patterns
- **stable_ecosystem**: Very stable, minimal mutations
- **rapid_evolution**: Fast-paced, high diversity
- **minimal**: Small grid, quick experiments

To change presets, edit this line in `main.py`:
```python
params = load_preset("primordial_soup")  # Change to any preset name
```

## Usage Tips

### Species Creation
- **No limit**: Create as many species as you want (prompts at 10+)
- **Replay last run**: Answer 'y' when prompted to reuse previous species configuration
- **Quick presets**: Type 'quick' then choose 1-6 for instant species
- **Custom traits**: Type a name and configure all parameters manually

### Placement Strategies
- **random**: Scattered across the grid (high initial mortality)
- **center**: Seeded in 2x2 stable blocks spiraling from center (best survival)
- **edge**: Placed around perimeter

### Configuration Files
- `last_species_config.json`: Automatically saves your species setup
- Replay any previous run by selecting 'y' at startup
- Edit the JSON file to create custom starting conditions

### Performance
- Start with 3-5 species for balanced gameplay
- 10+ species can create complex ecosystems
- Center placement gives better initial survival
- Enable zone shifting for dynamic environments

## Understanding the Stats

**Generation**: Number of simulation steps executed

**Population**: Total number of living cells

**Species**: Number of distinct species currently alive

**Diversity Index**: Shannon diversity index (higher = more even distribution of species)

**Top Species Panel**: Shows the 5 most populous species with their colors and population counts

## Data Export

When you quit (Q or ESC), you'll be asked if you want to export simulation data. This creates a CSV file with:
- Generation number
- Total population over time
- Species count over time
- Diversity index
- Dominant species tracking

Perfect for graphing in Excel, Python, or any analysis tool.

## Tweaking Parameters

Edit `config/presets.json` to create custom scenarios:

```json
{
  "grid_size": [200, 200],        // Width x Height
  "solar_radiation": 0.3,         // (not used yet, reserved for energy system)
  "mutation_rate": 0.001,         // Probability of mutation (0.0-1.0)
  "survival_range": [2, 3],       // [min, max] neighbors to survive
  "birth_range": [3, 3],          // [min, max] neighbors to birth
  "cosmic_events": 0.0,           // (not used yet, for extinction events)
  "initial_density": 0.15         // Starting life density (0.0-1.0)
}
```

**Interesting experiments:**
- Set `mutation_rate` to 0.0 for no evolution (pure Conway's Game of Life)
- Set `survival_range` to [1, 4] and `birth_range` to [2, 4] for different life dynamics
- Increase `initial_density` to 0.5 for crowded starting conditions
- Try large grids (500x500+) with speed 100x for macro patterns

## Project Structure

```
primordial_garden/
├── main.py                  # Entry point
├── engine/
│   ├── grid.py             # Cellular automata core
│   ├── species.py          # Species traits and lineage
│   └── rules.py            # Environmental parameters
├── visualization/
│   └── renderer.py         # Pygame display
├── analysis/
│   └── tracker.py          # Data recording
└── config/
    └── presets.json        # Simulation parameters
```

## Future Expansions

The architecture supports adding:
- **Energy systems**: Cells consume/produce energy
- **Predator/prey dynamics**: Species interactions beyond competition
- **Environmental zones**: Different rules in different regions
- **Migration**: Cell movement/mobility
- **Better analytics**: Real-time graphs, lineage trees
- **Custom visualizations**: Heat maps, flow fields

## Tips for Zen Observation

- Start with `primordial_soup` preset at 1x speed
- Let it run for 10,000+ generations
- Watch for stable patterns that emerge and persist
- Notice extinction events (sudden drops in diversity)
- Look for "boom-bust" cycles in population
- Sometimes a single mutant species takes over everything—evolutionary bottleneck

## Tips for Analysis

- Run same preset multiple times—emergence is chaotic, results vary
- Export data from interesting runs
- Graph population vs. diversity over time
- Compare different mutation rates
- Look for phase transitions (sudden changes in system behavior)

---

**Enjoy watching life emerge from simple rules.**

The beauty is in the patterns you don't predict.
