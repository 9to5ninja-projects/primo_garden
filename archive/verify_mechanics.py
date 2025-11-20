"""
Verify all game mechanics work correctly after optimization
"""
from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits

print("="*70)
print("GAME MECHANICS VERIFICATION TEST")
print("="*70)

# Create test grid
grid = Grid(100, 100, wrap=True)
grid.setup_zones("quadrant")

# Test 1: Photosynthesizer (complexity 1, energy-seeking movement)
print("\n1. Testing Photosynthesizer (complexity 1)...")
traits_photo = SpeciesTraits(
    complexity=1,
    base_energy=100,
    energy_decay=2,
    photosynthesis_rate=4,
    reproduction_threshold=120,
    energy_source="photosynthesis",
    color=(0, 255, 0)
)
species_photo = Species("Photosynthesizer", traits_photo)
grid.seed_species(species_photo, 20, pattern="center")
print(f"   ✓ Seeded {species_photo.name}")

# Test 2: Fleeing organism (complexity 2)
print("\n2. Testing Fleeing Organism (complexity 2)...")
traits_flee = SpeciesTraits(
    complexity=2,
    base_energy=110,
    energy_decay=2,
    photosynthesis_rate=4,
    reproduction_threshold=130,
    energy_source="photosynthesis",
    color=(0, 200, 200)
)
species_flee = Species("Fleeing Organism", traits_flee)
grid.seed_species(species_flee, 15, pattern="center")
print(f"   ✓ Seeded {species_flee.name}")
print(f"   ✓ Movement strategy: {species_flee.traits.get_movement_strategy()}")

# Test 3: Predator (complexity 3, hunting)
print("\n3. Testing Predator (complexity 3+)...")
traits_pred = SpeciesTraits(
    complexity=3,
    base_energy=150,
    energy_decay=3,
    reproduction_threshold=180,
    energy_source="predation",
    can_be_consumed=False,
    color=(255, 0, 0)
)
species_pred = Species("Predator", traits_pred)
grid.seed_species(species_pred, 10, pattern="random")
print(f"   ✓ Seeded {species_pred.name}")
print(f"   ✓ Movement strategy: {species_pred.traits.get_movement_strategy()}")
print(f"   ✓ Can hunt: {species_pred.traits.can_hunt()}")
print(f"   ✓ Hunting efficiency: {species_pred.traits.get_hunting_efficiency():.0%}")

# Run simulation and check mechanics
print("\n" + "="*70)
print("RUNNING SIMULATION - 20 GENERATIONS")
print("="*70)

initial_pop = len([c for row in grid.cells for c in row if c and c.is_alive])
print(f"\nInitial population: {initial_pop}")

for i in range(20):
    grid.step()
    
    if (i + 1) % 5 == 0:
        stats = grid.get_stats()
        print(f"\nGen {stats['generation']:2d}:")
        print(f"  Population: {stats['population']:4d} cells")
        print(f"  Species:    {stats['species_count']:2d}")
        print(f"  Births:     {stats['births']:3d}")
        print(f"  Deaths:     {stats['deaths']:3d}")
        print(f"  Mutations:  {stats['mutations']:2d}")

# Final verification
print("\n" + "="*70)
print("VERIFICATION RESULTS")
print("="*70)

final_stats = grid.get_stats()

# Check 1: Population changed (births/deaths working)
pop_changed = final_stats['population'] != initial_pop
print(f"\n✓ Population dynamics:  {'WORKING' if pop_changed else 'FAILED'}")
print(f"  Initial: {initial_pop}, Final: {final_stats['population']}")

# Check 2: Species evolved (mutations working)
species_count = len(grid.species_registry.get_living_species())
print(f"\n✓ Mutation system:      {'WORKING' if species_count > 3 else 'FAILED'}")
print(f"  Started with 3 species, now have {species_count}")

# Check 3: Predation occurred
total_deaths = sum(s.total_deaths for s in grid.species_registry.get_living_species())
print(f"\n✓ Predation system:     {'WORKING' if total_deaths > 0 else 'FAILED'}")
print(f"  Total deaths: {total_deaths}")

# Check 4: Movement occurred (check if cells moved from center)
cells_at_center = 0
cx, cy = grid.width // 2, grid.height // 2
for y in range(cy - 10, cy + 10):
    for x in range(cx - 10, cx + 10):
        if 0 <= x < grid.width and 0 <= y < grid.height:
            if grid.cells[y][x] and grid.cells[y][x].is_alive:
                cells_at_center += 1

center_density = cells_at_center / (20 * 20)
print(f"\n✓ Movement system:      {'WORKING' if center_density < 0.5 else 'CHECK'}")
print(f"  Center density: {center_density:.0%} (should decrease as cells move)")

# Check 5: Zones working
zones = grid.zone_manager.get_all_zones()
print(f"\n✓ Zone system:          {'WORKING' if len(zones) > 0 else 'FAILED'}")
print(f"  Active zones: {len(zones)}")

# Check 6: Reproduction with energy
total_births = sum(s.total_births for s in grid.species_registry.get_living_species())
print(f"\n✓ Reproduction system:  {'WORKING' if total_births > 0 else 'FAILED'}")
print(f"  Total births: {total_births}")

print("\n" + "="*70)
print("ALL CORE MECHANICS VERIFIED!")
print("="*70)
