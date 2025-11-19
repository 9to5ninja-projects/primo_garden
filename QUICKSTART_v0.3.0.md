# 🚀 Quick Start Guide - Primordial Garden v0.3.0

## Installation

```bash
# Install dependencies (if not already done)
pip install pygame matplotlib numpy

# Or use the setup script
python setup.py  # Windows: setup.bat
```

## Running the Simulation

```bash
python main_enhanced.py
```

---

## 🎯 5-Minute Predator Demo

### Fastest way to see the new features:

1. **Start the simulation:**
   ```bash
   python main_enhanced.py
   ```

2. **Configuration prompts:**
   - Grid size: `200` (press Enter for default)
   - Zone layout: `3` (Quadrants - creates hunting territories)

3. **Create species:**
   - First species: `quick` → `5` (Predator) → Population: `30`
   - Second species: `quick` → `2` (Efficient) → Population: `120`
   - Third species: `done`

4. **Placement:**
   - Predator placement: `edge` (start at borders)
   - Efficient placement: `center` (cluster in middle)

5. **Watch the simulation:**
   - Press `5` for 100x speed
   - Press `G` to view graphs
   - Watch predator-prey dynamics unfold!

---

## 🧪 Experiment Templates

### Template 1: Classic Predator-Prey
**Goal:** See Lotka-Volterra population cycles

**Setup:**
- Zones: Quadrant (type `3`)
- Species 1: Predator preset (`quick` → `5`) - Pop: 25
- Species 2: Mobile preset (`quick` → `3`) - Pop: 100

**What to watch:**
- Press `G` to see population graphs
- Look for oscillations: prey population spikes, then predator population rises, prey crashes, predator starves, repeat
- Typical cycle: 500-2000 generations

---

### Template 2: Intelligence vs Chaos
**Goal:** Does smart movement beat random?

**Setup:**
- Zones: Random (type `2`)
- Species 1: Seeker preset (`quick` → `6`) - Pop: 50
- Species 2: Mobile preset (`quick` → `3`) - Pop: 50

**What to watch:**
- Seekers should migrate to energy-rich zones (Fertile, Paradise)
- Random movers waste energy on poor zones
- Check population graphs - seekers should dominate over time

---

### Template 3: Three-Way Food Web
**Goal:** Complex ecosystem dynamics

**Setup:**
- Zones: Ring world (type `4`)
- Species 1: Stationary prey (`quick` → `1`) - Pop: 150
- Species 2: Mobile prey (`quick` → `3`) - Pop: 75
- Species 3: Predator (`quick` → `5`) - Pop: 25

**What to watch:**
- Which prey strategy survives better?
- Do predators prefer stationary or mobile prey?
- Does Paradise zone become a refuge?

---

## 🎨 Custom Species Builder

### Creating a Custom Predator:

When prompted for species name, type a name (e.g., `Apex`)

Then configure:
```
Base energy: 150          # High starting energy
Energy decay: 5           # Hungry hunters
Photosynthesis: 1         # Carnivores don't need sun
Can move: y              # Yes, mobile
Movement strategy: hunt   # Actively pursue prey
Is predator: y           # Yes, can consume others
Color R/G/B: 255/0/0     # Red
```

### Creating Custom Prey (Flee Strategy):

Name: `Survivor`
```
Base energy: 100
Energy decay: 2
Photosynthesis: 4        # Need good energy
Can move: y
Movement strategy: flee  # Run from predators!
Is predator: n
Color R/G/B: 0/255/0     # Green
```

---

## 📊 Reading the Graphs

Press **G** to toggle graph view.

### Graph 1: Population Over Time
- **Y-axis**: Total living cells
- **Look for**: Boom/bust cycles, stable equilibrium, extinction events

### Graph 2: Species Count
- **Y-axis**: Number of distinct species
- **Look for**: Increasing diversity (mutations accumulating) or decreasing (extinction pressure)

### Graph 3: Births/Deaths/Mutations
- **Green line**: Births per generation
- **Red line**: Deaths per generation
- **Purple line**: Mutations per generation
- **Look for**: Births matching deaths = stable oscillator

### Graph 4: Species Diversity Ratio
- **Y-axis**: Species count ÷ Population (0.0 to 1.0)
- **Low (0.1-0.3)**: Few dominant species (stable ecosystem)
- **High (0.7-1.0)**: Extreme fragmentation (every cell unique species)

---

## ⚡ Speed Tips

### For Fast Evolution:
1. Start with small grid: `100 x 100`
2. Use fewer initial species: 2-3
3. Higher mutation rate (custom species with mutation_rate=0.05)
4. Press `5` for 100x speed

### For Detailed Observation:
1. Larger grid: `300 x 200`
2. More species: 4-5
3. Press `1` for 1x speed
4. Watch individual cells move and hunt

### For Analysis:
1. Run at high speed (`5`) for 10,000+ generations
2. Export data with `S` key
3. Press `G` to review graphs
4. Look for phase transitions and equilibria

---

## 🔑 Keyboard Controls

| Key | Action |
|-----|--------|
| **SPACE** | Pause/Resume simulation |
| **1-5** | Set speed (1x, 5x, 10x, 50x, 100x) |
| **G** | Toggle between simulation and graphs ⭐ NEW |
| **S** | Export CSV data immediately |
| **Q** | Quit (auto-saves data) |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'matplotlib'"
```bash
pip install matplotlib numpy
```

### "pygame.error: No video mode has been set"
- Make sure you're not running in headless mode
- Try: `export SDL_VIDEODRIVER=x11` (Linux)

### Graphs not showing
- Press `G` to toggle graph window
- If graphs appear black, wait a few generations for data to accumulate
- Need at least 2 data points for graphs to render

### Everything dies immediately
- Energy decay too high or photosynthesis too low
- Try Efficient preset (`quick` → `2`)
- Use Fertile or Paradise zones
- Reduce predator population

### Predators starve
- Not enough prey
- Increase prey population to 3-4x predator count
- Give prey higher photosynthesis rate
- Use zones with better energy generation

---

## 💡 Pro Tips

### Discovering Emergent Behaviors:
1. **Run long**: 20,000+ generations
2. **Mix strategies**: 2 prey types + 1 predator
3. **Vary zones**: Ring world creates interesting migrations
4. **Watch mutations**: Species adapt to pressures

### Creating Stable Ecosystems:
- Prey:Predator ratio of 4:1 or higher
- Give prey some advantage (speed, energy efficiency, or flee strategy)
- Use zones with refuges (Paradise zones predators avoid)

### Causing Chaos:
- Equal predator and prey populations
- High mutation rates (0.05+)
- Toxic zones everywhere
- Multiple predator species competing

---

## 📈 Success Indicators

### You're doing it right if you see:
✅ Population oscillations in graphs  
✅ Predators actively chasing prey  
✅ Prey clustering in safe zones  
✅ Species count evolving over time  
✅ Energy-seekers migrating to fertile areas  

### Something's wrong if you see:
❌ Everything dies in <100 generations  
❌ Population stuck at 0  
❌ No movement visible  
❌ Graphs completely flat  

---

## 🔥 THE PRIMORDIAL CHALLENGE

**Can you create a stable 3-species food chain?**

Requirements:
- 1 Stationary prey species (survives >5000 gens)
- 1 Mobile prey species (survives >5000 gens)
- 1 Predator species (survives >5000 gens)
- All three coexist without extinction

**Hint:** Balance is everything. Predators need to be *slightly* inefficient.

---

## 📚 Next Steps

1. **Run Template 1** - See predator/prey in action
2. **Press G** - Watch the graphs
3. **Export data** - Analyze in Excel/Python
4. **Create custom species** - Experiment with traits
5. **Share results** - What emergent behaviors did you find?

---

**Welcome to the food chain.** 🦁🌿

**Now go forth and evolve.**
