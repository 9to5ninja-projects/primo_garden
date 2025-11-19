# Primordial Garden v0.3.0 - The Predator Update

## 🔥 NEW FEATURES - ALL THREE IMPLEMENTED 🔥

### 1. INTELLIGENT MOVEMENT 🧠
Cells no longer wander aimlessly. They now have **movement strategies**:

#### Movement Strategies:
- **`random`** - Classic random walk (default for mobile cells)
- **`energy_seeking`** - Moves toward zones with better energy generation (Fertile > Paradise > Neutral > Desert > Toxic)
- **`flee`** - Detects predators and moves away from danger
- **`hunt`** - Predators actively pursue prey

#### How It Works:
- Each mobile species has a `movement_strategy` trait
- Strategy is checked every generation during `process_movement()`
- Cells evaluate neighbors and choose optimal direction
- Movement still costs energy (configurable per species)

#### Code Changes:
- `enhanced_engine/grid.py`: Replaced simple random walk with strategic movement
- Added 3 new methods:
  - `_move_energy_seeking()` - Seeks better zones
  - `_move_flee()` - Avoids predators
  - `_move_hunt()` - Pursues prey

---

### 2. PREDATOR/PREY SYSTEM 🦁🐰
The Garden now has a food chain!

#### Predator Mechanics:
- **Consumption**: Predators can eat adjacent prey
- **Energy Transfer**: Predator gains energy from prey (configurable efficiency)
- **Hunting Behavior**: If `movement_strategy="hunt"`, actively pursues prey
- **Prey Death**: Consumed cells die immediately

#### New Species Traits:
```python
is_predator: bool = False           # Can this species hunt?
hunting_efficiency: float = 0.8     # % of prey energy gained (0.0-1.0)
can_be_consumed: bool = True        # Can be eaten by predators?
```

#### Predation Phase:
New `process_predation()` step added to simulation cycle:
1. **Age** → cells decay/photosynthesize
2. **Move** → intelligent positioning
3. **Hunt** → predators consume prey ⭐ NEW
4. **Reproduce** → Conway rules + energy
5. **Update** → population counts

#### Code Changes:
- `enhanced_engine/species_enhanced.py`: Added predator traits
- `enhanced_engine/cell.py`: Added `consume_prey()` method
- `enhanced_engine/grid.py`: Added `process_predation()` phase

---

### 3. REAL-TIME GRAPHS 📊
Live visualization of simulation dynamics!

#### Press **G** to toggle graph window

#### 4 Graphs Displayed:
1. **Population Over Time** - Total living cells
2. **Species Count Over Time** - Active species diversity
3. **Births/Deaths/Mutations** - Generational events
4. **Species Diversity** - Species/Population ratio

#### Features:
- Tracks last 500 generations (configurable)
- Updates every frame
- Matplotlib integration with pygame
- Export graphs with `graphs.save(filename)`

#### Code Changes:
- **NEW FILE**: `visualization/live_graphs.py` - Complete graphing system
- `main_enhanced.py`: Integrated `LiveGraphs` class
- Added **G key** toggle between simulation and graphs

#### Technical Details:
- Uses `matplotlib.use('Agg')` for non-blocking rendering
- Renders to numpy array, converts to pygame surface
- Separate window mode for cleaner visualization
- Auto-cleanup on exit

---

## 🎮 UPDATED CONTROLS

```
SPACE     Pause/Resume
1-5       Set speed (1x, 5x, 10x, 50x, 100x)
G         Toggle Graphs ⭐ NEW
S         Export data to CSV
Q         Quit (auto-saves)
```

---

## 🧬 NEW SPECIES PRESETS

### Preset 5: Predator 🦁
```python
Base Energy: 120
Energy Decay: 4 (hungry!)
Photosynthesis: 1 (carnivore)
Can Move: True
Movement Strategy: hunt
Is Predator: True
Hunting Efficiency: 0.75
Color: Red (255, 0, 0)
```

### Preset 6: Seeker 🔍
```python
Base Energy: 100
Energy Decay: 2
Photosynthesis: 2
Can Move: True
Movement Strategy: energy_seeking
Is Predator: False
Color: Yellow (255, 255, 0)
```

---

## 🔬 EXPERIMENT IDEAS

### Predator/Prey Dynamics:
1. **Classic Arms Race**
   - 100 "Prey" (Efficient, can_move=True, strategy="flee")
   - 20 "Predators" (Predator preset)
   - Zone: Quadrant (creates refuges)
   - **Watch**: Do prey survive? Do predators starve?

2. **Energy Competition**
   - 50 "Seekers" (energy_seeking strategy)
   - 50 "Random Movers" (random strategy)
   - Zone: Random (varied energy availability)
   - **Watch**: Does intelligence win?

3. **Three-Way Dynamics**
   - 100 Stationary prey (no movement)
   - 30 Fleeing prey (flee strategy)
   - 20 Predators (hunt strategy)
   - **Watch**: Which prey strategy survives?

### Graph Analysis:
- Run 10,000+ generations
- Press **G** to view graphs
- Look for:
  - Population boom/bust cycles
  - Predator-prey oscillations (classic Lotka-Volterra)
  - Extinction cascades
  - Equilibrium points

---

## 🏗️ ARCHITECTURE UPDATES

### Simulation Phases (in order):
```python
def step(self):
    self.generation += 1
    
    # Phase 1: Aging & Energy
    self.process_aging()
    
    # Phase 2: Movement (intelligent)
    self.process_movement()
    
    # Phase 3: Predation ⭐ NEW
    self.process_predation()
    
    # Phase 4: Reproduction
    self.process_reproduction()
    
    # Phase 5: Statistics
    self.species_registry.update_populations(self)
```

### New Files:
- `visualization/live_graphs.py` - Graphing system

### Modified Files:
- `enhanced_engine/species_enhanced.py` - Predator traits
- `enhanced_engine/cell.py` - Consumption mechanics
- `enhanced_engine/grid.py` - Movement AI + predation
- `main_enhanced.py` - Graph integration

---

## 🚀 QUICK START

### Run with defaults:
```bash
python main_enhanced.py
# Choose "quick" presets
# Try preset 5 (Predator) + preset 2 (Efficient prey)
```

### Create predator scenario:
1. Start simulation
2. Choose "quick" → 5 (Predator) → Population: 20
3. Choose "quick" → 3 (Mobile) → Population: 100
4. Choose quadrant zones (creates hunting grounds)
5. Watch the chase!
6. Press **G** to view population graphs

### Test movement intelligence:
1. Start simulation
2. Choose "quick" → 6 (Seeker) → Population: 50
3. Choose ring world zones (energy gradient)
4. Watch seekers migrate to paradise center
5. Compare to random movers

---

## 📊 EXPECTED BEHAVIORS

### Stable Predator/Prey:
- Population oscillations (predator lags prey)
- Spatial patterns (prey cluster, predators patrol)
- Equilibrium around 60-80% prey, 20-40% predators

### Extinction Events:
- **Prey extinction**: Predators too efficient or too many
- **Predator extinction**: Not enough prey or hunt failure
- **Mutual extinction**: Usually from poor energy balance

### Movement Advantages:
- **Energy-seekers**: Dominate in varied zones
- **Flee strategy**: Survive predators better
- **Hunters**: Catch more prey, need less photosynthesis
- **Random**: Loses to strategic movement over time

---

## 🐛 KNOWN QUIRKS

1. **Graph Toggle**: Switching to graph window stops rendering main sim (by design)
2. **Predation Chaos**: High predator efficiency can crash populations fast
3. **Movement Energy**: Mobile species need more photosynthesis or favorable zones
4. **Mutation Surprise**: Predators can mutate into non-predators (5% chance)

---

## 🔮 FUTURE EXPANSIONS (Not Yet Implemented)

### Sexual Reproduction:
- Two-parent genome mixing
- Trait recombination
- Hybrid vigor effects

### Advanced Predation:
- Pack hunting (multiple predators coordinate)
- Venom/weakening mechanics
- Size-based predation (only eat smaller prey)

### Smarter Movement:
- Pheromone trails
- Memory of good zones
- Group migration

---

## 🎯 THE BOTTOM LINE

**All three requested features are FULLY FUNCTIONAL:**

✅ **Intelligent Movement** - 4 strategies implemented  
✅ **Predator/Prey** - Complete consumption mechanics  
✅ **Real-Time Graphs** - 4-panel live visualization  

**Press G. Watch the Garden burn.** 🔥🌱

---

## 📝 VERSION HISTORY

- **v0.3.0** (Current) - Predator/Prey, Smart Movement, Live Graphs
- **v0.2.0** - Energy System, Zones, Mobility, Species Designer
- **v0.1.0** - Classic Conway + Species Tracking

---

**The Primordial Garden has teeth now.**  
**Let evolution eat itself.** 🦁🌿
