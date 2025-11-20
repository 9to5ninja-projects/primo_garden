"""
Large population stress test
Test performance with high cell counts (target: 5k-10k cells)
"""
from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
import time

# Create larger grid
width, height = 300, 300
grid = Grid(width, height, wrap=True)
grid.setup_zones("random")

# Create multiple species with higher populations
traits1 = SpeciesTraits(
    complexity=1,
    base_energy=120,
    energy_decay=1,
    reproduction_threshold=100,
    photosynthesis_rate=4,
    mutation_rate=0.01,
    color=(0, 255, 0)
)
species1 = Species("Greens", traits1)
species1.generation_born = 0

traits2 = SpeciesTraits(
    complexity=2,
    base_energy=130,
    energy_decay=2,
    reproduction_threshold=120,
    photosynthesis_rate=5,
    mutation_rate=0.01,
    color=(0, 200, 200)
)
species2 = Species("Cyans", traits2)
species2.generation_born = 0

traits3 = SpeciesTraits(
    complexity=3,
    base_energy=160,
    energy_decay=3,
    reproduction_threshold=180,
    mutation_rate=0.015,
    energy_source="predation",
    color=(255, 0, 0)
)
species3 = Species("Reds", traits3)
species3.generation_born = 0

# Seed multiple species with larger populations
print("Seeding species...")
grid.seed_species(species1, 300, pattern="center")
grid.seed_species(species2, 200, pattern="center")
grid.seed_species(species3, 50, pattern="random")

print("\n" + "="*70)
print("LARGE POPULATION STRESS TEST")
print("="*70)
print(f"Grid: {width}x{height} = {width*height:,} cells")
print(f"Initial population: {len([c for row in grid.cells for c in row if c and c.is_alive]):,}")
print("\nRunning 100 generations...\n")

# Run simulation
start_time = time.perf_counter()
max_pop = 0
gen_times = []

for i in range(100):
    gen_start = time.perf_counter()
    grid.step()
    gen_time = time.perf_counter() - gen_start
    gen_times.append(gen_time)
    
    stats = grid.get_stats()
    if stats['population'] > max_pop:
        max_pop = stats['population']
    
    # Print stats every 10 generations
    if (i + 1) % 10 == 0:
        avg_time = sum(gen_times[-10:]) / 10 * 1000  # Last 10 gens avg
        fps_equivalent = 1000 / avg_time if avg_time > 0 else 0
        print(f"Gen {stats['generation']:3d}: {stats['population']:5d} cells, {stats['species_count']:2d} species | "
              f"Avg: {avg_time:6.1f}ms/gen ({fps_equivalent:4.1f} FPS)")

total_time = time.perf_counter() - start_time
avg_gen_time = sum(gen_times) / len(gen_times) * 1000

print("\n" + "="*70)
print("STRESS TEST RESULTS")
print("="*70)
print(f"Total time:          {total_time:.2f}s")
print(f"Avg per generation:  {avg_gen_time:.1f}ms")
print(f"Target FPS achieved: {1000/avg_gen_time:.1f} FPS")
print(f"Max population:      {max_pop:,} cells")
final_stats = grid.get_stats()
print(f"Final population:    {final_stats['population']:,} cells")
print(f"Final species:       {final_stats['species_count']}")
print()
print("Performance targets:")
print("  ✓ 1+ FPS  = Playable")
print("  ✓ 5+ FPS  = Smooth")
print("  ✓ 10+ FPS = Excellent")
