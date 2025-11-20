# Changelog

All notable changes to Primordial Garden will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-20 - The Performance Update 🚀

### Major Achievement: 127x Performance Improvement
Successfully optimized simulation to handle massive populations (15k+ cells) at playable framerates WITHOUT population limits or feature sacrifices.

### Performance Results
- **Before:** 11,949ms per generation (0.08 gens/sec) = <0.1 FPS at 3k cells
- **After:** 94ms per generation (10.59 gens/sec) = **10+ FPS at 3k cells**
- **12,826 cells:** 545ms/gen = **1.8 FPS** (user's original problem scenario)
- **22,057 cells:** 852ms/gen = **1.2 FPS** (stress test maximum)
- **127x speedup overall!**

### Added
- **Numba JIT Compilation**: Parallel neighbor counting
  - New file: `enhanced_engine/grid_numba.py`
  - `count_all_neighbors()` - Vectorized operation with parallel processing
  - Eliminates 3.3 seconds of neighbor counting per generation
  - Result: Neighbor counting time → 0ms
  
- **Intelligent Caching System**: Zone and population pressure caches
  - `_build_zone_caches()` - Caches zone lookups once per generation
  - `_build_neighbor_cache()` - Builds neighbor counts once, reuses everywhere
  - `_zone_cache`, `_zone_pressure_cache` - O(1) lookups vs expensive calculations
  - Cache invalidation per generation to maintain accuracy
  
- **Performance Profiling**: Built-in timing system
  - Timing stats for each simulation phase (aging, movement, predation, reproduction)
  - Prints performance breakdown every 10 generations
  - Helps identify bottlenecks for future optimization
  - New fields: `Grid.timing_stats` dictionary
  
- **Testing Tools**:
  - `profile_performance.py` - Benchmark tool for 50-gen tests
  - `stress_test.py` - Large population testing (300x300 grid, 100+ gens)
  - `verify_mechanics.py` - Validates all game mechanics after optimization
  - `quick_test.py` - Fast validation of imports and basic functionality

### Changed
- `Grid.count_living_neighbors()` now uses cached values
- `Grid.process_aging()` uses cached zones and population pressure
- `Grid.process_movement()` uses cached zones for pathfinding
- `Grid.process_reproduction()` builds neighbor cache before processing births/deaths
- All zone lookups in hot paths replaced with cache access
- Fixed Unicode emoji in performance output (Windows console compatibility)
- Fixed Unicode arrow in zone transformation messages (→ replaced with ->)

### Technical Details
- Numba JIT compilation with `@jit(nopython=True, parallel=True, cache=True)`
- Neighbor cache: 2D numpy bool array → 2D numpy int32 array (parallel prange)
- Zone cache: Dict (x,y) → Zone object (O(1) lookup)
- Pressure cache: Dict Zone → float (pre-calculated per generation)
- Cache generation tracking prevents stale data
- All game mechanics preserved - zero feature loss

### Performance Breakdown (22k cells @ Gen 100)
| Phase | Time | % | Notes |
|-------|------|---|-------|
| Movement | 417ms | 48% | Main bottleneck at high populations |
| Aging | 184ms | 21% | Down from 56% thanks to caching |
| Reproduction | 189ms | 22% | Neighbor cache eliminates overhead |
| Predation | 64ms | 7% | Efficient with cached zones |
| Neighbor Counting | 0ms | 0% | Fully optimized with Numba |

### Verified Working
All game mechanics tested and confirmed functional:
- ✓ Population dynamics (births/deaths)
- ✓ Species evolution and mutations
- ✓ Predation and hunting mechanics
- ✓ Movement strategies (energy-seeking, fleeing, hunting)
- ✓ Zone effects and bonuses
- ✓ Energy system with photosynthesis/predation
- ✓ Reproduction with energy costs
- ✓ Carrying capacity and population pressure
- ✓ Habitat specialization and native zones

### Real-World Validation
User ran simulation for 2,550 generations with optimizations:
- Population range: 1,274 - 15,153 cells
- Average population: 14,320 cells
- Final: 14,876 cells with 80 species
- Stable performance throughout entire run
- No crashes, no slowdowns, all mechanics working

### Documentation
- `OPTIMIZATION_COMPLETE.md` - Complete optimization guide and results
- Performance profiling built into Grid class
- Timing statistics printed every 10 generations

### Migration Notes
- No breaking changes - optimizations are transparent
- Existing simulations work immediately with new performance
- No configuration needed - caching is automatic
- All previous features preserved exactly

# Changelog

## [0.8.0] - 2025-11-19 - The Habitat Specialization Update 🏔️

### Problem Addressed
**Conway's Life Geometric Stability** was overpowering all biological features:
- Stable patterns (gliders, oscillators, still lifes) locking cells for 1,000+ generations
- Gen 80-100 stasis: 0 births/deaths despite aging, intelligence, carrying capacity
- All features failed because Conway's mathematical rules never changed

### Solution: Three-Pronged Attack on Stasis

#### Added - Phase 3: Habitat Specialization & Territorial Evolution
- **Native Zone System**: Species evolve home territories and local adaptation
  - **Native Zone Type**: Tracks where a species' lineage originated (paradise, fertile, neutral, desert, toxic)
  - **Native Zone Affinity**: 1.0-2.0x reproduction bonus in home territory (default 1.5x)
  - **Territorial Advantage**: Lower energy threshold for reproduction in native zones
  - **Auto-Assignment**: Species automatically assigned native zone based on seeding location
  - Fields: `SpeciesTraits.native_zone_type`, `SpeciesTraits.native_zone_affinity`

- **Native Zone Evolution**: Species can slowly adapt to new territories over generations
  - **2% Mutation Rate**: Native zone can change during speciation
  - **Adjacent Zone Preference**: 70% chance to adapt to neighboring zones vs 30% random
  - **Long-Term Adaptation**: Enables species to migrate and establish new territories
  - Zone adjacency hierarchy: paradise ↔ fertile ↔ neutral ↔ desert ↔ toxic
  - Method: `Species._mutate_native_zone()`

- **Zone Tracking During Seeding**: All three seeding patterns now track placement
  - Random scatter: Counts cells placed per zone
  - Center pattern: Tracks 2x2 blocks and fallback scatter
  - Edge pattern: Monitors zone distribution around perimeter
  - Native zone = zone with most cells seeded
  - Displays: "Species established in [zone] zone (X/Y cells)"

#### Changed - Energy-Dependent Conway Survival Rules
- **High Energy Cells (>70%)**: Standard Conway rules (2-3 neighbors survive)
  - Healthy, well-fed cells follow normal patterns
  - Can form stable structures when energy is abundant

- **Medium Energy Cells (40-70%)**: Conway rules + stress mortality
  - Standard 2-3 neighbor survival range
  - **30% random death at 4 neighbors** (overcrowding stress)
  - Begins to destabilize patterns as energy depletes

- **Low Energy Cells (<40%)**: Harder survival requirements
  - Need **3-4 neighbors instead of 2-3** to survive
  - Unstable: Patterns collapse when cells get hungry
  - Forces cells to seek better zones or die
  - **Breaks Conway geometric locks** - low energy = pattern collapse

#### Changed - Geometry-Breaking Perturbations
- **Random Death for Old, Stable Cells**: 2% death chance per generation
  - Only applies to cells at max neighbor count (perfectly stable)
  - Only triggers for cells aged > 50 generations
  - Prevents infinite geometric patterns
  - Subtle enough to preserve interesting dynamics
  - Ensures no pattern locks forever

### Technical Details
- Comprehensive test suite: `test_habitat_specialization.py` (9 tests, all passing)
- Zone name extraction: `zone.properties.name.lower().split()[0]` → "fertile"
- Native zone reproduction bonus: `threshold / native_zone_affinity`
- Energy-dependent neighbor requirements vary by `energy / max_energy` ratio
- Random perturbations use `random.random() < 0.02` for 2% death chance
- Grid tracks zone_counts during seeding to determine most common placement

### Expected Impact
- **No More 1,000+ Generation Locks**: Energy depletion forces pattern instability
- **Territorial Competition**: Species dominate home zones, struggle elsewhere
- **Dynamic Population**: Low energy → unstable patterns → deaths → energy recovery → growth cycles
- **Natural Selection Pressure**: Only well-adapted species persist in each zone
- **Continuous Evolution**: Random perturbations + energy dynamics prevent permanent stasis

## [0.7.0] - 2025-11-19 - The Carrying Capacity Update 🌍

### Added - Phase 4: Carrying Capacity & Population Limits
- **Carrying Capacity Per Zone**: Each zone now has a maximum sustainable population
  - **Paradise**: 150 cells (abundant resources)
  - **Fertile Plains**: 120 cells (rich environment)
  - **Neutral Ground**: 100 cells (standard capacity)
  - **Desert Wastes**: 60 cells (harsh conditions)
  - **Toxic Zone**: 40 cells (very harsh)
  - Field: `ZoneProperties.carrying_capacity`

- **Population Pressure System**: Dynamic resource availability based on crowding
  - **< 50% capacity**: 1.3x energy bonus (plenty of resources)
  - **50-100% capacity**: 1.3-0.7x gradual decline (approaching limits)
  - **100-150% capacity**: 1.0-0.8x moderate penalty (overcrowding)
  - **> 150% capacity**: 0.5-0.8x harsh penalty (severe overcrowding)
  - Smoother gradients prevent sudden population crashes
  - Method: `Zone.get_population_pressure()`

- **Population Tracking**: Zones count living cells in real-time
  - Method: `Zone.get_cell_count()` - counts cells within zone boundaries
  - Grid reference set on zone initialization for cell access

### Changed
- **Energy Gain Affected by Overcrowding**: Population pressure multiplies energy generation
  - `Cell.age_one_generation()` now takes `population_pressure` parameter
  - Overcrowded zones: Cells gain less energy (down to 50% at severe overcrowding)
  - Empty zones: Cells gain bonus energy (up to 130% under 50% capacity)
  - Gradual pressure curve prevents sudden die-offs
  - Encourages migration to less crowded areas

- **Reproduction Moderately Harder in Crowded Zones**: Gradual increase in energy threshold
  - Reproduction difficulty scales with pressure (max 1.5x at extreme overcrowding)
  - At 150% capacity: ~1.3x reproduction threshold
  - Severe overcrowding (< 0.6x pressure): blocks low-energy reproduction
  - Prevents runaway growth without causing total collapse

### Technical Details
- Added comprehensive test suite: `test_carrying_capacity.py`
- All zone presets updated with appropriate capacities
- Zone-grid integration for real-time cell counting
- Population pressure calculated per-zone, applied per-cell

### Expected Impact - SOLVES STASIS PROBLEM
This update directly addresses the 1,000+ generation stasis locks:

**Before (v0.6.0)**: Cells form stable Conway patterns, never need to move, simulation freezes
- Gen 1730: 72 cells, 0 births/deaths for 100+ generations
- Cells living 1,300+ generations (far exceeding lifespan limits)
- Geometric stability overpowers all biological systems

**After (v0.7.0)**: Carrying capacity disrupts stable patterns
1. **Overcrowding Kills Patterns**: Stable blocks become overcrowded → energy penalty → cells starve
2. **Forces Migration**: Cells in crowded zones must move to survive
3. **Prevents Stasis**: Can't maintain stable patterns when resources deplete
4. **Creates Cycles**: Population grows → hits capacity → die-off → regrowth
5. **Spatial Competition**: Species fight for territory, not just food

**Expected Behavior**:
- Populations oscillate around carrying capacity (no runaway growth)
- Overcrowded zones see die-offs and mass migration
- Species spread across zones seeking empty space
- Constant turnover even in "stable" patterns
- No more 1,000+ generation locks!

This is **Phase 4 of 6** in the natural emergence roadmap (see `EMERGENCE_PROPOSAL.md`).

## [0.6.0] - 2025-11-19 - The Intelligence Update 🧠

### Added - Phase 1: Complexity-Linked Intelligence
- **Cognitive Abilities Based on Complexity**: Organisms now gain intelligence with complexity
  - **Complexity 1** (Simple): Random movement only - bacteria, single cells
  - **Complexity 2** (Aware): Can sense energy zones and flee predators - insects, simple animals
  - **Complexity 3** (Strategic): Can hunt prey - predators, smart animals
  - **Complexity 4-5** (Advanced): All strategies available - social/intelligent life
  - Method: `SpeciesTraits.get_available_strategies()` returns available strategies by complexity
  - Method: `SpeciesTraits.is_strategy_valid()` validates strategy matches complexity

- **Strategy Evolution System**: Movement strategies now mutate and evolve
  - Strategies can change during mutation (10% chance per generation)
  - New strategies only unlock when complexity is sufficient
  - Invalid strategies auto-correct to match complexity level
  - Species can evolve from "random" → "energy_seeking" → "hunt" over time
  - Method: `Species._mutate_movement_strategy()` handles intelligent strategy mutations

- **Natural Selection for Intelligence**: Creates evolutionary pressure for complexity
  - Simple organisms: Low energy cost, limited behavior (good in stable environments)
  - Complex organisms: High energy cost, smart behavior (good in harsh/competitive environments)
  - **No more random complexity** - intelligence has actual survival value!
  - Species in challenging environments will naturally evolve higher complexity

### Changed
- `Species.mutate()` now enables movement_strategy mutations (was disabled)
- Strategy mutations respect complexity constraints (can't have "hunt" with complexity 1)
- Complexity changes trigger automatic strategy validation and correction
- `SpeciesTraits.__post_init__()` auto-corrects invalid strategy/complexity combinations

### Technical Details
- Added comprehensive test suite: `test_complexity_intelligence.py`
- All preset species validated for correct complexity/strategy pairings
- Mutation system ensures strategies always match cognitive abilities
- Backward compatible: existing saves auto-correct invalid combinations

### Expected Emergence Patterns
With this update, simulations should show:
1. **Early gens**: Simple organisms (complexity 1-2) dominate with low costs
2. **Middle gens**: Environmental pressure drives complexity mutations
3. **Late gens**: Smart organisms (complexity 3+) emerge in harsh zones
4. **Endgame**: Strategic predators hunting, prey fleeing, energy seekers optimizing
5. **Natural arms race**: Prey evolve to flee, predators evolve to hunt

This is **Phase 1 of 6** in the natural emergence roadmap (see `EMERGENCE_PROPOSAL.md`).

## [0.5.0] - 2025-11-19 - The Mortality Update 💀

### Added
- **Aging and Lifespan System**: Cells now have finite lifespans
  - New trait: `max_lifespan` (0-1000 generations, 0=immortal)
  - New trait: `age_decline_start` (0.0-1.0) - When aging effects begin
  - Old age death - cells die after reaching max lifespan
  - Aging penalty - energy costs increase up to 50% as cells age
  - Different species have different lifespans (Predator=150, Resilient=500)
  
- **Energy Source Diversification**: Three feeding strategies
  - New trait: `energy_source` - "photosynthesis", "predation", or "hybrid"
  - **Photosynthesis**: Always gains energy from light (plants, algae)
  - **Predation**: Needs nearby prey or starves (2x energy with prey, 0.1x without)
  - **Hybrid**: Flexible omnivores (1.5x with prey, 0.7x without)
  - Can mutate between energy sources (5% chance)
  
- **Environmental Pressure & Optimal Zones**: Harsh survival outside niches
  - New trait: `starvation_threshold` - Die if energy drops below this outside optimal zone
  - New trait: `optimal_zone_bonus` - Energy multiplier in ideal environment (default 2.0x)
  - `is_optimal_zone()` method checks if species thrives in current zone
  - Desert specialists (heat_tolerance>0.7) thrive in deserts
  - Toxic specialists (toxin_resistance>0.7) dominate toxic zones
  - Generalists (balanced tolerances) prefer fertile/paradise zones
  - Species die rapidly in non-optimal zones without food
  
- **Migration Pressure for Predators**: Must find prey to survive
  - Predators/hybrid feeders check for nearby prey each generation
  - `_has_prey_nearby()` scans neighbors for consumable species
  - No prey = severe energy penalty (0.1x photosynthesis for pure predators)
  - Forces predators to move or starve
  - Creates natural predator-prey cycles
  
- **Food Web Dynamics**: Complex energy flow
  - Photosynthesizers are primary producers (base of food chain)
  - Predators are consumers (must hunt to survive)
  - Hybrids adapt to available resources
  - Energy cascades through trophic levels

- **Species Configuration System**: Save and replay setups
  - `save_species_config()` - Saves species to `last_species_config.json`
  - `load_species_config()` - Loads previous configuration
  - Automatic save after species creation
  - "Replay last configuration?" prompt on startup
  - Manual JSON editing supported for custom scenarios

### Changed
- **Removed 5 species limit**: Can now create unlimited species
  - Prompts to continue after 10 species
  - Allows complex multi-species ecosystems
- `Cell.age_one_generation()` now takes `has_prey_nearby` parameter
- Energy gain calculation includes food source multiplier and optimal zone bonus
- Starvation occurs at threshold (not just 0 energy) outside optimal zones
- All preset species assigned appropriate lifespans and energy sources
- Predator preset: `energy_source="predation"`, `max_lifespan=150`
- Seeker preset: `energy_source="hybrid"`, `max_lifespan=350`
- Other presets: `energy_source="photosynthesis"`, lifespans 250-500

### Technical
- `SpeciesTraits` expanded with 5 new parameters (19 → 24 total)
- `Grid._has_prey_nearby()` helper method for predator detection
- Aging penalty calculation: `1.0 + decline * 0.5` (up to 50% cost increase)
- Energy source multiplier system integrated into photosynthesis calculation
- Optimal zone detection compares traits to zone type

### Balance Changes
- Efficient: Lifespan 400, optimal_zone_bonus 2.5x (specialization reward)
- Resilient: Lifespan 500, optimal_zone_bonus 2.0x (longevity champion)
- Predator: Lifespan 150, starvation_threshold 20 (high pressure)
- Mobile: Lifespan 250 (moderate)
- Balanced: Lifespan 300 (baseline)

## [0.4.0] - 2025-11-19 - The Evolution Update 🧬

### Added
- **Environmental Adaptation System**: Species adapt to different zones
  - New traits: `heat_tolerance` (0.0-1.0) - Desert survival
  - New trait: `cold_tolerance` (0.0-1.0) - Arctic/cold zone survival
  - New trait: `toxin_resistance` (0.0-1.0) - Toxic zone tolerance
  - `get_adaptation_bonus()` method calculates zone fitness
  - Well-adapted species thrive (up to 1.5x energy), poor adaptation suffers (down to 0.3x)
  - Adaptation traits mutate over time, enabling natural selection
  
- **Dynamic Environmental Changes**: World evolves over time
  - Zones shift position every N generations (configurable)
  - Zone types can change (Fertile → Toxic, Desert → Paradise, etc.)
  - Zone boundaries expand and contract
  - Forces continuous adaptation pressure
  - Enable with `grid.zone_manager.enable_shifting(interval)`
  
- **Organism Complexity System**: Energy costs scale with sophistication
  - New trait: `complexity` (1-5) - Organism sophistication level
  - New trait: `metabolic_efficiency` (0.5-2.0) - Energy usage multiplier
  - `get_complexity_cost()` calculates energy penalty
  - Higher complexity = more energy needed but enables advanced features
  - Simple organisms (complexity 1) = 30% less energy cost
  - Complex organisms (complexity 5) = 120% more energy cost
  
- **Sexual Reproduction**: Dual-parent reproduction option
  - New trait: `sexual_reproduction` (bool) - Requires two parents
  - Must have 2+ neighbors of same species to reproduce
  - Both parents contribute energy to offspring
  - Reduces mutation rate by 50% (genetic stability)
  - Can mutate to/from asexual reproduction
  
- **Enhanced Energy System**: Multi-factor metabolic simulation
  - Energy costs affected by: complexity, adaptation, metabolism, zone modifiers
  - Energy gains boosted by: adaptation, photosynthesis, metabolic efficiency
  - Formula: `decay = base_decay * zone_mult * complexity_cost / adaptation_bonus`
  - Formula: `gain = base_photo * zone_mult * adaptation_bonus / metabolic_efficiency`

### Changed
- Updated all preset species with new traits (complexity, adaptations, efficiency)
- Cell aging now considers zone type for adaptation bonuses
- Reproduction system checks for sexual/asexual mode
- Zone manager now tracks generation and handles shifts
- Main menu adds environmental shifting configuration

### Technical
- `SpeciesTraits` expanded from 13 to 18 parameters
- `Cell.age_one_generation()` now takes `zone_type` parameter
- `ZoneManager` gains `step()`, `enable_shifting()`, `shift_zones()` methods
- Grid step process adds environmental change phase (Phase 0)

## [0.3.0] - 2025-11-19 - The Predator Update 🦁

### Added
- **Intelligent Movement System**: 4 movement strategies for mobile cells
  - `random` - Classic random walk (default)
  - `energy_seeking` - Moves toward better energy zones
  - `flee` - Detects and avoids predators
  - `hunt` - Actively pursues prey
- **Predator/Prey System**: Complete food chain mechanics
  - New trait: `is_predator` - Species can consume other cells
  - New trait: `hunting_efficiency` - Energy transfer rate (0.0-1.0)
  - New trait: `can_be_consumed` - Protection from predation
  - `consume_prey()` method in Cell class
  - New simulation phase: `process_predation()`
  - Energy transfer from prey to predator
- **Real-Time Graphs**: Live visualization with matplotlib
  - Press **G** to toggle graph window
  - 4 panels: Population, Species Count, Events, Diversity
  - 500-generation rolling window
  - Auto-updates every frame
  - New file: `visualization/live_graphs.py`
- **New Species Presets**:
  - Preset 5: Predator (hunts, low photosynthesis, red)
  - Preset 6: Seeker (energy_seeking strategy, yellow)

### Changed
- Movement system completely rewritten with strategic AI
- Simulation cycle now includes predation phase (between movement and reproduction)
- Species mutation can now change predator status (5% chance)
- Movement strategy rarely mutates (preserves behavioral consistency)

### Technical
- `Grid.process_movement()` now evaluates movement strategies
- New methods: `_move_energy_seeking()`, `_move_flee()`, `_move_hunt()`
- `SpeciesTraits` expanded with predator/movement fields
- Predation events logged per generation

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
