# Primordial Garden

An emergent life simulation combining cellular automata with genetic evolution. Watch colorful species evolve, compete, and adapt in real-time.

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the simulation
python main.py
```

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
