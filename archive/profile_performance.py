"""
Quick performance profiling test
Run simulation headless for 50 generations to measure bottlenecks
"""
from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
import time

# Create grid
width, height = 200, 200
grid = Grid(width, height, wrap=True)
grid.setup_zones("random")

# Create test species
traits1 = SpeciesTraits(
    complexity=2,
    base_energy=100,
    energy_decay=2,
    reproduction_threshold=120,
    movement_cost=5,
    mutation_rate=0.005,
    color=(0, 255, 0)
)
species1 = Species("Photosynthesizer", traits1)
species1.generation_born = 0

traits2 = SpeciesTraits(
    complexity=3,
    base_energy=150,
    energy_decay=3,
    reproduction_threshold=180,
    movement_cost=8,
    mutation_rate=0.01,
    energy_source="predation",
    color=(255, 0, 0)
)
species2 = Species("Predator", traits2)
species2.generation_born = 0

# Seed species
grid.seed_species(species1, 100, pattern="center")
grid.seed_species(species2, 30, pattern="random")

print("\n" + "="*60)
print("PERFORMANCE PROFILING TEST")
print("="*60)
print(f"Grid: {width}x{height}")
print(f"Initial population: {len([c for row in grid.cells for c in row if c and c.is_alive])}")
print("\nRunning 50 generations...\n")

# Run simulation
start_time = time.perf_counter()
for i in range(50):
    grid.step()
    
    # Print stats every 10 generations
    if (i + 1) % 10 == 0:
        stats = grid.get_stats()
        print(f"\nGen {stats['generation']}: {stats['population']} cells, {stats['species_count']} species")

total_time = time.perf_counter() - start_time

print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(f"Total time: {total_time:.2f}s")
print(f"Avg per generation: {total_time/50*1000:.1f}ms")
print(f"Generations per second: {50/total_time:.2f}")
final_stats = grid.get_stats()
print(f"Final population: {final_stats['population']}")
print(f"Final species: {final_stats['species_count']}")
