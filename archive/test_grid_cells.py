"""
Quick test to see if optimized grid cells survive
"""

from grid_optimized import GridOptimized
from enhanced_engine.species_enhanced import Species, SpeciesTraits

# Create small grid
grid = GridOptimized(50, 50)
grid.setup_zones("neutral")

# Create simple species
species = Species("TestSpecies", SpeciesTraits(
    photosynthesis_rate=10.0,
    energy_decay=3.0
))

# Seed cells
grid.seed_species(species, 50, "random")

print(f"After seeding:")
print(f"  Python cells: {sum(1 for row in grid.cells for c in row if c)}")
print(f"  Numpy alive: {grid.alive_grid.sum()}")
print(f"  get_stats: {grid.get_stats()}")

# Run one step
print(f"\nRunning 1 generation...")
grid.step()

print(f"\nAfter 1 generation:")
print(f"  Python cells: {sum(1 for row in grid.cells for c in row if c and c.is_alive)}")
print(f"  Numpy alive: {grid.alive_grid.sum()}")
print(f"  get_stats: {grid.get_stats()}")

# Run more
print(f"\nRunning 5 more generations...")
for i in range(5):
    grid.step()
    stats = grid.get_stats()
    print(f"  Gen {grid.generation}: pop={stats['population']}, births={stats['births']}, deaths={stats['deaths']}")
