# Changelog

All notable changes to Primordial Garden will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-19

### Added - Enhanced Mode (`main_enhanced.py`)
- **Energy System**: Cells have energy that decays over time and is regenerated through photosynthesis
  - Base energy, energy decay rate, and photosynthesis rate as species traits
  - Energy-based reproduction costs and thresholds
  - Starvation death when energy reaches zero
  - Visual feedback: cell brightness based on energy level
- **Environmental Zones**: Different regions with unique properties
  - 6 zone types: Fertile, Desert, Toxic, Neutral, Paradise, Void
  - Zone modifiers affect energy generation/decay, mutation rates, movement costs
  - Multiple zone layouts: Random, Quadrant (4 zones), Ring World (central paradise)
  - Zones rendered with distinct background colors
- **Cell Mobility**: Species can evolve movement capabilities
  - Movement as an energy-costly trait
  - Random walk movement pattern
  - Movement history tracking
  - Configurable movement range and cost per species
- **Species Designer**: Terminal-based species creation tool
  - Configure energy traits (base, decay, photosynthesis)
  - Set mobility options (can move, range, cost)
  - Customize reproduction parameters
  - Choose species colors
  - Quick presets: Balanced, Efficient, Mobile, Resilient
  - Support for multiple competing species (up to 5)
- **Enhanced Traits System**:
  - `SpeciesTraits` dataclass with 10+ configurable parameters
  - Overcrowding and isolation tolerance
  - Per-species mutation rates
  - Energy-based reproduction thresholds
- **Placement Patterns**: Seed species in specific formations
  - Random placement across grid
  - Center clustering
  - Edge/perimeter placement
- **Zone-Modified Mutations**: Mutation rates affected by environment (e.g., 3x in Toxic zones)

### Changed
- Classic mode (`main.py`) preserved and unmodified from v0.1.0
- Enhanced mode uses separate `enhanced_engine/` module structure
- Export filenames now prefixed with `enhanced_` for enhanced mode

### Technical Details
- New `Cell` class with energy mechanics and movement
- Enhanced `Species` class with comprehensive trait system
- `SpeciesRegistry` with extinction tracking
- `ZoneManager` for environmental region management
- `Grid` class supporting energy, zones, and mobility
- Conway's Life rules preserved but enhanced with energy constraints
- Births can occur with minimal energy even if parent can't afford reproduction cost

### Backwards Compatibility
- v0.1.0 classic mode fully functional via `main.py` or `run.bat`
- v0.2.0 enhanced mode accessible via `main_enhanced.py`
- Both modes use same optimized rendering and mutation fix from v0.1.0

## [0.1.0] - 2025-11-19

### Added
- Initial release of Primordial Garden
- Core cellular automata engine with Conway's Game of Life rules
- Species tracking system with genetic lineage
- Mutation system (0.1% rate during reproduction)
- Real-time pygame visualization with species colors
- Interactive controls (pause, speed control, reset)
- Statistics overlay showing:
  - Generation counter
  - Population and species counts
  - Species/population ratio
  - Birth/death/mutation counts per generation
  - Average species age
  - Top 5 species by population
- Configurable presets system (JSON-based)
- Data export to CSV with timestamped filenames
- Analysis script with matplotlib visualization
- Virtual environment setup scripts (Windows/Linux/Mac)
- Optimized rendering using numpy surfarray (100x+ faster)
- Frame skipping at high simulation speeds

### Fixed
- **CRITICAL**: Removed mutation-on-survival bug that caused infinite genetic drift
  - Mutations now only occur during reproduction, not when cells survive
  - This prevents stable oscillators from fragmenting into infinite species
  - Reduced typical species count from 946 → 23 in stable states

### Technical Details
- Grid-based simulation with numpy arrays
- Moore neighborhood (8 neighbors)
- Species inheritance through reproduction
- Genetic traits system (metabolism, reproduction, resilience)
- HSV-based color generation for species differentiation
- Shannon diversity index calculation
- Automatic extinct species cleanup

### Performance
- Handles 200x200 grids at 60 FPS (1x speed)
- Supports speeds up to 100x with frame skipping
- Optimized neighbor counting using numpy roll operations

### Known Limitations
- Simulation logic still uses Python loops (not GPU accelerated)
- No genetic compatibility checking between species
- Traits system exists but not yet used in survival rules
- Energy system designed but not implemented

---

## Future Roadmap

### v0.2.0 (Planned)
- Genetic compatibility system (prevent reproduction between distant species)
- GPU acceleration for simulation logic
- Real-time graphing of population/diversity
- Custom rule editor in UI

### v0.3.0 (Planned)
- Energy system implementation
- Predator/prey dynamics
- Environmental zones with different rules
- Cell migration/movement

### v1.0.0 (Planned)
- Full trait system integration
- Phylogenetic tree visualization
- Advanced analytics and metrics
- Performance optimizations for large grids (500x500+)
