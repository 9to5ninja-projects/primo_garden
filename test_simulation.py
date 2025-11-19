"""
Quick demo/test script for Primordial Garden 2.0
Runs a headless simulation to test all systems
"""
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.grid import Grid
from enhanced_engine.zones import ZoneType


def create_test_species(name: str, color: tuple, can_move: bool = False) -> Species:
    """Create a test species with reasonable defaults"""
    traits = SpeciesTraits(
        base_energy=150,  # Higher starting energy
        energy_decay=1,   # Lower decay
        photosynthesis_rate=5,  # Higher generation
        energy_from_birth=30,   # Lower reproduction cost
        reproduction_threshold=50,  # Lower threshold
        can_move=can_move,
        movement_cost=8 if can_move else 5,
        mutation_rate=0.02,
        color=color
    )
    return Species(name, traits)


def run_test_simulation(generations: int = 100):
    """Run a quick test simulation"""
    print("=== Primordial Garden 2.0 - Test Simulation ===\n")
    
    # Create grid
    grid = Grid(100, 100, wrap=True)
    print(f"Created {grid.width}x{grid.height} grid")
    
    # Setup zones
    grid.setup_zones("quadrant")
    print(f"Created quadrant zone layout")
    print(f"  Zones: {len(grid.zone_manager.get_all_zones())}")
    
    # Create test species
    species_a = create_test_species("Phototrophs", (50, 255, 50), can_move=False)
    species_b = create_test_species("Nomads", (50, 150, 255), can_move=True)
    species_c = create_test_species("Volatiles", (255, 100, 50), can_move=False)
    
    # Modify volatiles to have higher mutation
    species_c.traits.mutation_rate = 0.05
    
    # Seed species
    grid.seed_species(species_a, 80, "center")
    grid.seed_species(species_b, 60, "edge")
    grid.seed_species(species_c, 50, "random")
    
    print(f"\nSeeded species:")
    print(f"  {species_a.name}: stationary, moderate mutation")
    print(f"  {species_b.name}: mobile, moderate mutation")
    print(f"  {species_c.name}: stationary, high mutation")
    
    print(f"\n{'='*60}")
    print(f"{'Gen':>6} | {'Pop':>6} | {'Species':>7} | {'Births':>6} | {'Deaths':>6} | {'Mut':>4}")
    print(f"{'='*60}")
    
    # Run simulation
    for _ in range(generations):
        grid.step()
        
        if grid.generation % 10 == 0:
            stats = grid.get_stats()
            print(f"{stats['generation']:>6} | "
                  f"{stats['population']:>6} | "
                  f"{stats['species_count']:>7} | "
                  f"{stats['births']:>6} | "
                  f"{stats['deaths']:>6} | "
                  f"{stats['mutations']:>4}")
    
    # Final report
    print(f"{'='*60}\n")
    final_stats = grid.get_stats()
    
    print("FINAL STATISTICS:")
    print(f"  Total Generations: {final_stats['generation']}")
    print(f"  Final Population: {final_stats['population']}")
    print(f"  Living Species: {final_stats['species_count']}")
    print(f"  Extinct Species: {len(grid.species_registry.extinct_species)}")
    print(f"  Avg Species Age: {final_stats['avg_species_age']:.1f} generations")
    
    if final_stats['dominant_species']:
        dom = final_stats['dominant_species']
        print(f"\nDominant Species:")
        print(f"  Name: {dom.name}")
        print(f"  Population: {dom.population} ({100*dom.population/final_stats['population']:.1f}%)")
        print(f"  Age: {final_stats['generation'] - dom.generation_born} generations")
        print(f"  Total Births: {dom.total_births}")
        print(f"  Total Deaths: {dom.total_deaths}")
    
    print(f"\nTop 5 Species by Population:")
    species_list = sorted(grid.species_registry.get_living_species(),
                         key=lambda s: s.population, reverse=True)[:5]
    for i, sp in enumerate(species_list, 1):
        print(f"  {i}. {sp.name}: {sp.population} cells")
    
    # Test energy mechanics
    print(f"\nENERGY SAMPLE (random living cells):")
    count = 0
    for row in grid.cells:
        for cell in row:
            if cell and cell.is_alive:
                species = grid.species_registry.get(cell.species_id)
                zone = grid.zone_manager.get_zone_at(cell.x, cell.y)
                print(f"  Cell at ({cell.x},{cell.y})")
                print(f"    Species: {species.name}")
                print(f"    Energy: {cell.energy}/{cell.max_energy}")
                print(f"    Age: {cell.age} generations")
                print(f"    Zone: {zone.properties.name}")
                count += 1
                if count >= 3:
                    break
        if count >= 3:
            break
    
    print("\n✓ Test simulation complete!")
    return grid


if __name__ == "__main__":
    import sys
    
    gens = 100
    if len(sys.argv) > 1:
        try:
            gens = int(sys.argv[1])
        except ValueError:
            print(f"Invalid generation count, using default: {gens}")
    
    grid = run_test_simulation(gens)
    
    print("\nRun with: python test_simulation.py [generations]")
    print("For full UI: python main_enhanced.py")
