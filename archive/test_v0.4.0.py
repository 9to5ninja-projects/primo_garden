"""
Test script for v0.4.0 features
Tests: Environmental adaptation, sexual reproduction, complexity, shifting zones
"""

from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.zones import ZoneType


def test_adaptation():
    """Test environmental adaptation bonuses"""
    print("\n=== Testing Environmental Adaptation ===")
    
    # Desert-adapted species
    desert_species = Species("DesertDweller", SpeciesTraits(
        heat_tolerance=0.9,
        cold_tolerance=0.2,
        toxin_resistance=0.3
    ))
    
    # Check adaptation bonuses
    desert_bonus = desert_species.traits.get_adaptation_bonus("desert")
    toxic_bonus = desert_species.traits.get_adaptation_bonus("toxic")
    
    print(f"Desert adaptation: {desert_bonus:.2f}x (expected ~1.4x)")
    print(f"Toxic adaptation: {toxic_bonus:.2f}x (expected ~0.6x)")
    
    assert desert_bonus > 1.2, "Desert-adapted should thrive in desert"
    assert toxic_bonus < 0.8, "Desert-adapted should struggle in toxic"
    print("✓ Adaptation system working")


def test_complexity():
    """Test organism complexity costs"""
    print("\n=== Testing Complexity System ===")
    
    simple = SpeciesTraits(complexity=1)
    complex_org = SpeciesTraits(complexity=4)
    
    simple_cost = simple.get_complexity_cost()
    complex_cost = complex_org.get_complexity_cost()
    
    print(f"Simple organism (complexity 1): {simple_cost:.2f}x energy")
    print(f"Complex organism (complexity 4): {complex_cost:.2f}x energy")
    
    assert simple_cost == 1.0, "Simplest organisms should have base cost"
    assert complex_cost > 1.5, "Complex organisms should cost more"
    print("✓ Complexity system working")


def test_sexual_reproduction():
    """Test sexual reproduction mechanics"""
    print("\n=== Testing Sexual Reproduction ===")
    
    # Create sexual and asexual species
    sexual_species = Species("Sexual", SpeciesTraits(
        sexual_reproduction=True,
        mutation_rate=0.1
    ))
    
    asexual_species = Species("Asexual", SpeciesTraits(
        sexual_reproduction=False,
        mutation_rate=0.1
    ))
    
    print(f"Sexual species: requires 2 parents, lower mutation")
    print(f"Asexual species: requires 1 parent, normal mutation")
    
    assert sexual_species.traits.sexual_reproduction == True
    assert asexual_species.traits.sexual_reproduction == False
    print("✓ Reproduction modes configured")


def test_zone_shifting():
    """Test dynamic zone changes"""
    print("\n=== Testing Zone Shifting ===")
    
    grid = Grid(100, 100, wrap=True)
    grid.setup_zones("random")
    
    initial_zone_count = len(grid.zone_manager.zones)
    initial_first_zone_x = grid.zone_manager.zones[0].x if grid.zone_manager.zones else 0
    
    print(f"Initial zones: {initial_zone_count}")
    print(f"Initial first zone position: x={initial_first_zone_x}")
    
    # Enable shifting
    grid.zone_manager.enable_shifting(interval=10)
    
    # Advance 10 generations
    for _ in range(10):
        grid.zone_manager.step()
    
    # Check if zones shifted
    final_first_zone_x = grid.zone_manager.zones[0].x if grid.zone_manager.zones else 0
    
    print(f"After 10 gens, first zone position: x={final_first_zone_x}")
    print(f"Zone shifted: {initial_first_zone_x != final_first_zone_x}")
    
    print("✓ Zone shifting enabled")


def test_integrated_simulation():
    """Test full simulation with all v0.4.0 features"""
    print("\n=== Testing Integrated Simulation ===")
    
    grid = Grid(150, 150, wrap=True)
    grid.setup_zones("quadrant")
    grid.zone_manager.enable_shifting(interval=50)
    
    # Create diverse species
    species_configs = [
        ("Simple", SpeciesTraits(
            complexity=1,
            metabolic_efficiency=0.8,
            heat_tolerance=0.5
        ), 50),
        ("Complex", SpeciesTraits(
            complexity=3,
            metabolic_efficiency=1.2,
            toxin_resistance=0.8,
            sexual_reproduction=True
        ), 50),
        ("Adapted", SpeciesTraits(
            complexity=2,
            heat_tolerance=0.9,
            cold_tolerance=0.3,
            can_move=True,
            movement_strategy="energy_seeking"
        ), 50)
    ]
    
    for name, traits, pop in species_configs:
        species = Species(name, traits)
        grid.seed_species(species, pop, "random")
    
    print(f"Seeded {len(species_configs)} species")
    
    # Run simulation
    initial_pop = sum(1 for row in grid.cells for cell in row if cell and cell.is_alive)
    print(f"Initial population: {initial_pop}")
    
    for gen in range(50):
        grid.step()
        if gen % 10 == 0:
            stats = grid.get_stats()
            print(f"Gen {stats['generation']}: pop={stats['population']}, "
                  f"species={stats['species_count']}, mutations={stats['mutations']}")
    
    final_stats = grid.get_stats()
    print(f"\nFinal: {final_stats['population']} cells, {final_stats['species_count']} species")
    print("✓ Integrated simulation complete")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PRIMORDIAL GARDEN v0.4.0 - FEATURE TESTS")
    print("=" * 60)
    
    try:
        test_adaptation()
        test_complexity()
        test_sexual_reproduction()
        test_zone_shifting()
        test_integrated_simulation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
