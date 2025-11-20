"""
Quick test of population management system
Creates intentionally large population to test culling
"""

from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.population_manager import PopulationManager

print("=" * 60)
print("POPULATION MANAGEMENT TEST")
print("=" * 60)

# Create small grid
grid = Grid(50, 50, wrap=True)
grid.setup_zones("random")

# Create population manager with low limits for testing
pop_manager = PopulationManager(
    max_cells_per_species=50,
    total_cell_limit=500
)

# Create diverse species
species_list = []
for i in range(10):
    traits = SpeciesTraits(
        complexity=i % 5 + 1,
        metabolic_efficiency=0.5 + (i * 0.05),
        photosynthesis_rate=0.3 + (i * 0.03)
    )
    species = Species(f"Species{i}", traits)
    species_list.append(species)

# Seed heavy populations
print("\n📦 Seeding populations...")
for species in species_list:
    grid.seed_species(species, 100, "random")

initial_stats = pop_manager.get_population_stats(grid.cells)
print(f"Initial: {initial_stats['total']} cells, {initial_stats['species']} species")

# Run a few generations to let populations explode
print("\n⏱️  Running 20 generations...")
for gen in range(20):
    grid.step()
    if gen % 5 == 0:
        stats = pop_manager.get_population_stats(grid.cells)
        print(f"  Gen {gen}: {stats['total']} cells, {stats['species']} species")

# Check if culling needed
pre_cull_stats = pop_manager.get_population_stats(grid.cells)
print(f"\nBefore culling: {pre_cull_stats['total']} cells")

if pop_manager.should_cull_population(pre_cull_stats['total'], pre_cull_stats['species']):
    print("\n🔪 CULLING POPULATION...")
    grid.cells = pop_manager.cull_population_intelligent(
        grid.cells, 
        grid.generation,
        grid.species_registry
    )
    
    post_cull_stats = pop_manager.get_population_stats(grid.cells)
    print(f"After culling: {post_cull_stats['total']} cells")
    print(f"Species preserved: {post_cull_stats['species']}/{pre_cull_stats['species']}")
    
    # Verify all species survived
    if post_cull_stats['species'] == pre_cull_stats['species']:
        print("✅ SUCCESS: All species preserved!")
    else:
        print(f"❌ WARNING: Lost {pre_cull_stats['species'] - post_cull_stats['species']} species")
    
    # Show per-species breakdown
    print("\nPer-species populations after culling:")
    for species_id, count in sorted(post_cull_stats['per_species_breakdown'].items()):
        print(f"  Species {species_id}: {count} cells")
else:
    print("\n✓ Population under control, no culling needed")

# Test adaptive birth control
print("\n🎚️  ADAPTIVE BIRTH CONTROL TEST:")
for pop_level in [0, 250, 350, 425, 475, 495]:
    multiplier = pop_manager.adaptive_birth_control(pop_level, pre_cull_stats['species'])
    pressure = pop_level / pop_manager.total_cell_limit
    print(f"  {pop_level:>4} cells ({pressure:>4.0%} capacity) -> {multiplier:>4.0%} birth rate")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
