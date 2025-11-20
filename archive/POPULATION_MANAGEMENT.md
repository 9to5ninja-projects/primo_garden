# Population Management System

## Problem
When populations grow to **10,000+ cells with 300+ species**, the simulation becomes unplayable (<1 FPS) due to Python loops iterating over thousands of objects every generation.

## Solution
Intelligent population culling that maintains biodiversity while keeping performance acceptable.

## How It Works

### 1. Adaptive Monitoring
- Checks population every 50 generations
- Triggers culling when population > 5000 (configurable)
- Or when species count > 100

### 2. Intelligent Culling
When culling is needed, the system:

**Preserves Diversity:**
- Keeps at least 1 representative of every species
- Never wipes out entire species

**Fitness-Based Selection:**
Each organism gets a fitness score based on:
- **Energy Level (0-100 pts)**: Higher energy = more likely to survive
- **Complexity (0-50 pts)**: More complex = more valuable
- **Age (0-30 pts)**: Younger organisms = fresher genes
- **Metabolic Efficiency (0-40 pts)**: Better metabolism = fitter
- **Predator Bonus (+20 pts)**: Ecological importance
- **Random Factor (0-10 pts)**: Ensures diversity

**Balanced Strategy:**
- Keeps top 70% by fitness score (elite performers)
- Keeps 30% random sampling (genetic diversity)
- Per-species limits adjust based on total species count

### 3. Adaptive Birth Control
As population approaches limits, birth rates automatically reduce:
- < 50% capacity: 100% birth rate (normal)
- 50-70%: 80% birth rate (slight reduction)
- 70-85%: 50% birth rate (moderate)
- 85-95%: 25% birth rate (heavy reduction)
- > 95%: 10% birth rate (emergency brakes)

This prevents explosive growth before culling is needed.

## Configuration

In `main_enhanced.py`:

```python
pop_manager = PopulationManager(
    max_cells_per_species=200,  # Limit per species
    total_cell_limit=5000        # Total population cap
)
```

### Adjusting for Your Hardware

**Fast PC (modern CPU/GPU):**
```python
total_cell_limit=10000  # More organisms, lower FPS
```

**Slow PC:**
```python
total_cell_limit=2000   # Fewer organisms, smoother
```

**Testing/Development:**
```python
total_cell_limit=1000   # Very fast, good for testing
```

## Performance Impact

### Without Population Management:
- 12,000 cells = **<1 FPS** at 1x speed
- 6,000 cells = ~3-5 FPS at 1x speed

### With Population Management (5000 limit):
- 5,000 cells = ~10-15 FPS at 1x speed
- Maintains playable performance indefinitely
- Biodiversity preserved (all species survive)

### With JAX Optimization (future):
- CPU: 5,000 cells = **50-100 FPS** at 1x speed
- GPU (if available): 10,000+ cells = **100+ FPS**

## What Gets Culled

**Priority for Removal:**
1. Low energy organisms (starving)
2. Older organisms (past reproductive prime)
3. Inefficient metabolism
4. Duplicate genotypes in overcrowded species

**Never Culled:**
1. Last member of a species
2. Recently mutated organisms
3. High-fitness individuals
4. Predators (ecological importance)

## Statistics

The PopulationManager tracks:
- Total organisms culled over time
- Culls per species
- Culling frequency

Access with:
```python
pop_manager.print_culling_report()
```

## UI Indicators

In the stats panel:
- **Normal**: `Population: 2,450`
- **Busy**: `Population: 3,800 ⚠️ BUSY`
- **High Load**: `Population: 4,850 🔥 HIGH LOAD`

When culling occurs, console shows:
```
🔪 CULLED: Removed 1,247 cells, kept 3,753 (87 species)
```

## Future Enhancements

1. **JAX Vectorization** (in progress)
   - 5-10x speedup on CPU
   - 20-50x speedup on GPU (if available)
   - Raises population limits significantly

2. **Spatial Culling**
   - Remove organisms from overcrowded areas first
   - Keep organisms in sparse zones

3. **Competitive Exclusion**
   - Automatically cull when two species are too similar
   - Drives speciation and niche differentiation

4. **User Controls**
   - Hotkey to manually trigger culling
   - Real-time adjustment of population limits
   - Species protection (mark species as "protected")
