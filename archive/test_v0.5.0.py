"""
Test script for v0.5.0 features
Tests: Aging/death, energy sources, environmental pressure, prey detection
"""

from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.cell import Cell


def test_aging_and_lifespan():
    """Test that cells die of old age"""
    print("\n=== Testing Aging and Lifespan ===")
    
    # Short-lived species
    short_lived = Species("ShortLived", SpeciesTraits(
        max_lifespan=10,
        age_decline_start=0.5
    ))
    
    # Create cell
    cell = Cell(0, 0, short_lived)
    
    # Age cell beyond lifespan
    alive_count = 0
    for gen in range(15):
        is_alive = cell.age_one_generation(short_lived, 1.0, "neutral", False)
        if is_alive:
            alive_count += 1
        else:
            print(f"Cell died at age {cell.age} (lifespan={short_lived.traits.max_lifespan})")
            break
    
    assert cell.age >= short_lived.traits.max_lifespan, "Cell should die at max lifespan"
    assert not cell.is_alive, "Cell should be dead"
    print("✓ Aging system working")


def test_energy_sources():
    """Test different energy source types"""
    print("\n=== Testing Energy Sources ===")
    
    # Photosynthesis (always gains energy)
    photo_traits = SpeciesTraits(energy_source="photosynthesis")
    photo_mult = photo_traits.get_energy_source_multiplier(has_prey_nearby=False)
    print(f"Photosynthesis (no prey): {photo_mult}x multiplier")
    assert photo_mult == 1.0, "Photosynthesis should always be 1.0x"
    
    # Predation (needs prey)
    pred_traits = SpeciesTraits(energy_source="predation")
    pred_with_prey = pred_traits.get_energy_source_multiplier(has_prey_nearby=True)
    pred_no_prey = pred_traits.get_energy_source_multiplier(has_prey_nearby=False)
    print(f"Predation (with prey): {pred_with_prey}x multiplier")
    print(f"Predation (no prey): {pred_no_prey}x multiplier")
    assert pred_with_prey == 2.0, "Predators should get 2x with prey"
    assert pred_no_prey == 0.1, "Predators should get 0.1x without prey"
    
    # Hybrid (flexible)
    hybrid_traits = SpeciesTraits(energy_source="hybrid")
    hybrid_with_prey = hybrid_traits.get_energy_source_multiplier(has_prey_nearby=True)
    hybrid_no_prey = hybrid_traits.get_energy_source_multiplier(has_prey_nearby=False)
    print(f"Hybrid (with prey): {hybrid_with_prey}x multiplier")
    print(f"Hybrid (no prey): {hybrid_no_prey}x multiplier")
    assert hybrid_with_prey == 1.5, "Hybrids should get 1.5x with prey"
    assert hybrid_no_prey == 0.7, "Hybrids should get 0.7x without prey"
    
    print("✓ Energy source system working")


def test_optimal_zones():
    """Test optimal zone detection and bonuses"""
    print("\n=== Testing Optimal Zones ===")
    
    # Desert specialist
    desert_species = SpeciesTraits(
        heat_tolerance=0.9,
        cold_tolerance=0.2,
        optimal_zone_bonus=2.5
    )
    
    assert desert_species.is_optimal_zone("desert") == True, "Should be optimal in desert"
    assert desert_species.is_optimal_zone("toxic") == False, "Should not be optimal in toxic"
    
    # Generalist
    generalist = SpeciesTraits(
        heat_tolerance=0.5,
        cold_tolerance=0.5,
        toxin_resistance=0.5
    )
    
    assert generalist.is_optimal_zone("fertile") == True, "Generalists optimal in fertile"
    assert generalist.is_optimal_zone("desert") == False, "Generalists not optimal in desert"
    
    # Toxic specialist
    toxic_species = SpeciesTraits(
        toxin_resistance=0.8
    )
    
    assert toxic_species.is_optimal_zone("toxic") == True, "Should be optimal in toxic"
    
    print("✓ Optimal zone detection working")


def test_environmental_pressure():
    """Test starvation outside optimal zones"""
    print("\n=== Testing Environmental Pressure ===")
    
    # Desert specialist in wrong zone
    desert_adapted = Species("DesertDweller", SpeciesTraits(
        base_energy=50,
        energy_decay=2,
        photosynthesis_rate=1,
        heat_tolerance=0.9,
        starvation_threshold=20,
        max_lifespan=0  # Immortal to test starvation only
    ))
    
    cell = Cell(0, 0, desert_adapted, energy=25)
    
    # Age in toxic zone (not optimal)
    for gen in range(5):
        is_alive = cell.age_one_generation(desert_adapted, 1.0, "toxic", False)
        print(f"Gen {gen+1}: Energy={cell.energy}, Alive={is_alive}")
        if not is_alive:
            print(f"Cell starved at energy {cell.energy} (threshold={desert_adapted.traits.starvation_threshold})")
            break
    
    assert not cell.is_alive, "Cell should starve in non-optimal zone"
    print("✓ Environmental pressure working")


def test_prey_detection():
    """Test predator prey detection"""
    print("\n=== Testing Prey Detection ===")
    
    grid = Grid(50, 50, wrap=True)
    
    # Create predator and prey species
    predator_species = Species("Predator", SpeciesTraits(
        is_predator=True,
        energy_source="predation"
    ))
    
    prey_species = Species("Prey", SpeciesTraits(
        can_be_consumed=True,
        energy_source="photosynthesis"
    ))
    
    grid.species_registry.register(predator_species)
    grid.species_registry.register(prey_species)
    
    # Place predator
    grid.cells[25][25] = Cell(25, 25, predator_species)
    
    # No prey nearby
    has_prey = grid._has_prey_nearby(25, 25, predator_species)
    print(f"Predator alone: has_prey={has_prey}")
    assert has_prey == False, "Should not detect prey when alone"
    
    # Add prey neighbor
    grid.cells[25][26] = Cell(26, 25, prey_species)
    
    # Prey nearby
    has_prey = grid._has_prey_nearby(25, 25, predator_species)
    print(f"Predator with prey neighbor: has_prey={has_prey}")
    assert has_prey == True, "Should detect nearby prey"
    
    print("✓ Prey detection working")


def test_integrated_mortality():
    """Test full simulation with aging, energy sources, and pressure"""
    print("\n=== Testing Integrated Mortality System ===")
    
    grid = Grid(100, 100, wrap=True)
    grid.setup_zones("quadrant")
    
    # Create diverse species
    species_configs = [
        ("Photosynthesizer", SpeciesTraits(
            base_energy=100,
            energy_decay=2,
            photosynthesis_rate=5,
            energy_source="photosynthesis",
            max_lifespan=200,
            heat_tolerance=0.6
        ), 30),
        ("Predator", SpeciesTraits(
            base_energy=120,
            energy_decay=3,
            photosynthesis_rate=1,
            energy_source="predation",
            can_move=True,
            movement_strategy="hunt",
            is_predator=True,
            max_lifespan=100,
            starvation_threshold=20
        ), 20),
        ("Hybrid", SpeciesTraits(
            base_energy=110,
            energy_decay=2,
            photosynthesis_rate=3,
            energy_source="hybrid",
            can_move=True,
            max_lifespan=150,
            heat_tolerance=0.5,
            toxin_resistance=0.5
        ), 25)
    ]
    
    for name, traits, pop in species_configs:
        species = Species(name, traits)
        grid.seed_species(species, pop, "random")
    
    initial_pop = sum(1 for row in grid.cells for cell in row if cell and cell.is_alive)
    print(f"Initial population: {initial_pop}")
    
    # Run simulation
    old_age_deaths = 0
    for gen in range(150):
        grid.step()
        
        # Count old cells
        for row in grid.cells:
            for cell in row:
                if cell and cell.is_alive:
                    species = grid.species_registry.get(cell.species_id)
                    if species and species.traits.max_lifespan > 0:
                        if cell.age >= species.traits.max_lifespan * 0.9:
                            old_age_deaths += 1
        
        if gen % 25 == 0:
            stats = grid.get_stats()
            print(f"Gen {stats['generation']}: pop={stats['population']}, "
                  f"species={stats['species_count']}, deaths={stats['deaths']}")
    
    final_stats = grid.get_stats()
    print(f"\nFinal: {final_stats['population']} cells, {final_stats['species_count']} species")
    print(f"Old age deaths detected: {old_age_deaths}")
    print("✓ Integrated mortality system complete")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PRIMORDIAL GARDEN v0.5.0 - MORTALITY TESTS")
    print("=" * 60)
    
    try:
        test_aging_and_lifespan()
        test_energy_sources()
        test_optimal_zones()
        test_environmental_pressure()
        test_prey_detection()
        test_integrated_mortality()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
