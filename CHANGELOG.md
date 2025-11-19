# Changelog

All notable changes to Primordial Garden will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
