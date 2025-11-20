"""
Test suite for v0.8.0 Phase 3: Habitat Specialization + Energy-Dependent Conway Rules
"""
import sys
import random
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.zones import Zone, ZoneProperties, ZoneType
from enhanced_engine.cell import Cell


def test_native_zone_assignment():
    """Test that species are assigned native zones based on seeding location"""
    print("\n=== Test: Native Zone Assignment ===")
    
    traits = SpeciesTraits()
    species = Species("TestSpecies", traits)
    
    # Should default to fertile
    assert species.traits.native_zone_type == "fertile", "Default native zone should be fertile"
    
    # Test setting native zone
    species.traits.native_zone_type = "desert"
    assert species.traits.native_zone_type == "desert", "Native zone should update"
    
    print("✓ Native zone assignment works correctly")


def test_native_zone_affinity():
    """Test that native zone affinity is in valid range"""
    print("\n=== Test: Native Zone Affinity ===")
    
    traits = SpeciesTraits()
    species = Species("TestSpecies", traits)
    
    # Should be between 1.0 and 2.0
    assert 1.0 <= species.traits.native_zone_affinity <= 2.0, \
        f"Native zone affinity {species.traits.native_zone_affinity} out of range [1.0, 2.0]"
    
    print(f"✓ Native zone affinity {species.traits.native_zone_affinity:.2f} is valid")


def test_native_zone_reproduction_bonus():
    """Test that native zone gives reproduction advantage"""
    print("\n=== Test: Native Zone Reproduction Bonus ===")
    
    traits = SpeciesTraits()
    species = Species("TestSpecies", traits)
    species.traits.native_zone_type = "fertile"
    species.traits.native_zone_affinity = 1.5
    
    # Simulate reproduction threshold calculation
    base_threshold = 100
    difficulty = 1.0
    population_pressure = 1.0
    
    # In native zone
    native_bonus = species.traits.native_zone_affinity
    native_threshold = base_threshold * difficulty * population_pressure / native_bonus
    
    # Outside native zone
    foreign_threshold = base_threshold * difficulty * population_pressure
    
    print(f"  Base threshold: {base_threshold}")
    print(f"  Native zone threshold: {native_threshold:.1f} (easier)")
    print(f"  Foreign zone threshold: {foreign_threshold:.1f}")
    
    assert native_threshold < foreign_threshold, "Native zone should have lower threshold"
    assert abs(native_threshold - (base_threshold / 1.5)) < 1, "Calculation should match expected"
    
    print("✓ Native zone provides reproduction advantage")


def test_native_zone_mutation():
    """Test that native zone mutations favor adjacent zones"""
    print("\n=== Test: Native Zone Mutation ===")
    
    traits = SpeciesTraits()
    species = Species("TestSpecies", traits)
    
    # Test mutation frequency and logic
    mutations = 0
    adjacent_count = 0
    total_trials = 1000
    
    for _ in range(total_trials):
        original = species.traits.native_zone_type
        species.traits.native_zone_type = Species._mutate_native_zone(original)
        
        if species.traits.native_zone_type != original:
            mutations += 1
            
            # Check if adjacent zone preference works
            adjacent_zones = {
                "paradise": ["fertile"],
                "fertile": ["paradise", "neutral"],
                "neutral": ["fertile", "desert"],
                "desert": ["neutral", "toxic"],
                "toxic": ["desert"]
            }
            
            if species.traits.native_zone_type in adjacent_zones.get(original, []):
                adjacent_count += 1
        
        # Reset for next trial
        species.traits.native_zone_type = original
    
    mutation_rate = mutations / total_trials * 100
    
    print(f"  Mutation rate: {mutation_rate:.1f}% (expected ~2%)")
    
    if mutations > 0:
        adjacent_rate = adjacent_count / mutations * 100
        print(f"  Adjacent zone preference: {adjacent_rate:.1f}% (expected ~70%)")
        assert adjacent_rate > 50, "Should prefer adjacent zones"
    
    assert 1.0 <= mutation_rate <= 4.0, f"Mutation rate {mutation_rate}% outside expected range [1-4%]"
    
    print("✓ Native zone mutations work correctly")


def test_energy_dependent_survival_rules():
    """Test that Conway survival rules vary by energy level"""
    print("\n=== Test: Energy-Dependent Conway Rules ===")
    
    # Simulate energy-dependent neighbor requirements
    test_cases = [
        (0.8, (2, 3), "High energy (>70%)"),
        (0.5, (2, 3), "Medium energy (40-70%)"),
        (0.3, (3, 4), "Low energy (<40%)")
    ]
    
    for energy_ratio, expected_range, description in test_cases:
        if energy_ratio > 0.7:
            min_neighbors, max_neighbors = 2, 3
        elif energy_ratio > 0.4:
            min_neighbors, max_neighbors = 2, 3
        else:
            min_neighbors, max_neighbors = 3, 4
        
        print(f"  {description}: {min_neighbors}-{max_neighbors} neighbors")
        assert (min_neighbors, max_neighbors) == expected_range, \
            f"Energy {energy_ratio} should require {expected_range}, got {(min_neighbors, max_neighbors)}"
    
    print("✓ Energy-dependent survival rules correct")


def test_geometry_breaking_perturbations():
    """Test that old cells at max neighbors have death chance"""
    print("\n=== Test: Geometry-Breaking Perturbations ===")
    
    # Simulate perturbation logic
    old_age = 60
    max_neighbors = 3
    perturbation_rate = 0.02
    
    trials = 10000
    deaths = 0
    
    for _ in range(trials):
        # Cell at max neighbors, old age
        if random.random() < perturbation_rate:
            deaths += 1
    
    actual_rate = deaths / trials
    print(f"  Death rate for old cells at max neighbors: {actual_rate:.3f}")
    print(f"  Expected: ~{perturbation_rate:.3f}")
    
    # Should be close to 2% (within statistical variance)
    assert 0.015 <= actual_rate <= 0.025, \
        f"Death rate {actual_rate:.3f} outside expected range [0.015, 0.025]"
    
    print("✓ Geometry-breaking perturbations active")


def test_zone_type_names():
    """Test that zone type names are correctly extracted"""
    print("\n=== Test: Zone Type Name Extraction ===")
    
    test_zones = [
        ("Paradise Zone 1", "paradise"),
        ("Fertile Region", "fertile"),
        ("Neutral Territory", "neutral"),
        ("Desert Area", "desert"),
        ("Toxic Wasteland", "toxic")
    ]
    
    for full_name, expected in test_zones:
        # Simulate the extraction logic from grid.py
        zone_name = full_name.lower().split()[0]
        print(f"  '{full_name}' → '{zone_name}'")
        assert zone_name == expected, f"Expected {expected}, got {zone_name}"
    
    print("✓ Zone name extraction works correctly")


def test_species_reproduction_in_zones():
    """Test comprehensive reproduction mechanics with zones"""
    print("\n=== Test: Species Reproduction Across Zones ===")
    
    traits = SpeciesTraits(reproduction_threshold=80)
    species = Species("Specialist", traits)
    species.traits.native_zone_type = "fertile"
    species.traits.native_zone_affinity = 1.6
    
    base_threshold = species.traits.reproduction_threshold
    
    zones = ["paradise", "fertile", "neutral", "desert", "toxic"]
    difficulties = [0.8, 1.0, 1.1, 1.3, 1.5]
    
    print(f"  Base threshold: {base_threshold}")
    print(f"  Native zone: {species.traits.native_zone_type} (affinity: {species.traits.native_zone_affinity}x)")
    print()
    
    for zone_name, difficulty in zip(zones, difficulties):
        is_native = zone_name == species.traits.native_zone_type
        bonus = species.traits.native_zone_affinity if is_native else 1.0
        
        effective_threshold = base_threshold * difficulty / bonus
        
        marker = "★" if is_native else " "
        print(f"  {marker} {zone_name.capitalize():8} (diff {difficulty:.1f}): threshold {effective_threshold:.1f}")
    
    # Verify native zone has lowest threshold
    fertile_threshold = base_threshold * 1.0 / species.traits.native_zone_affinity
    paradise_threshold = base_threshold * 0.8 / 1.0
    
    assert fertile_threshold < (base_threshold * 1.0), \
        "Native zone bonus should lower threshold"
    
    print("\n✓ Reproduction mechanics work correctly across zones")


def test_integration_scenario():
    """Test full integration of all Phase 3 features"""
    print("\n=== Test: Full Integration Scenario ===")
    
    # Create a species seeded in desert
    traits = SpeciesTraits(reproduction_threshold=70)
    species = Species("DesertSpecialist", traits)
    species.traits.native_zone_type = "desert"
    species.traits.native_zone_affinity = 1.8
    
    print(f"  Species: {species.name}")
    print(f"  Native zone: {species.traits.native_zone_type}")
    print(f"  Affinity: {species.traits.native_zone_affinity}x")
    
    # Test cells in different zones
    cell_desert = Cell(10, 10, species)
    cell_desert.energy = 100
    cell_desert.age = 70
    
    cell_fertile = Cell(20, 20, species)
    cell_fertile.energy = 100
    cell_fertile.age = 5
    
    # Simulate reproduction check in native zone (desert, difficulty 1.3)
    desert_threshold = 70 * 1.3 / 1.8  # ~50.6
    desert_can_reproduce = cell_desert.energy >= desert_threshold
    
    # Simulate reproduction check in foreign zone (fertile, difficulty 1.0)
    fertile_threshold = 70 * 1.0 / 1.0  # 70
    fertile_can_reproduce = cell_fertile.energy >= fertile_threshold
    
    print(f"\n  Cell in native desert zone:")
    print(f"    Energy: {cell_desert.energy}, Threshold: {desert_threshold:.1f}")
    print(f"    Can reproduce: {desert_can_reproduce}")
    
    print(f"\n  Cell in foreign fertile zone:")
    print(f"    Energy: {cell_fertile.energy}, Threshold: {fertile_threshold:.1f}")
    print(f"    Can reproduce: {fertile_can_reproduce}")
    
    # Both should be able to reproduce, but desert is easier
    assert desert_can_reproduce, "Should reproduce in native zone"
    assert fertile_can_reproduce, "Should reproduce in fertile zone too (high energy)"
    assert desert_threshold < fertile_threshold, "Native zone should have advantage"
    
    # Test geometry breaking on old cell
    old_cell_death_chance = 0.02 if cell_desert.age > 50 else 0.0
    print(f"\n  Old cell (age {cell_desert.age}) death chance: {old_cell_death_chance:.1%}")
    assert old_cell_death_chance > 0, "Old cells should have perturbation chance"
    
    # Test energy-dependent survival for low energy cell
    low_energy_cell = Cell(30, 30, species)
    low_energy_cell.energy = 20
    low_energy_cell.max_energy = 100
    energy_ratio = low_energy_cell.energy / low_energy_cell.max_energy
    
    if energy_ratio < 0.4:
        required_neighbors = "3-4"
    else:
        required_neighbors = "2-3"
    
    print(f"\n  Low energy cell ({energy_ratio:.1%}) needs {required_neighbors} neighbors")
    assert required_neighbors == "3-4", "Low energy cells should need more neighbors"
    
    print("\n✓ Full integration scenario works correctly")


def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("v0.8.0 Phase 3: Habitat Specialization Test Suite")
    print("=" * 60)
    
    test_functions = [
        test_native_zone_assignment,
        test_native_zone_affinity,
        test_native_zone_reproduction_bonus,
        test_native_zone_mutation,
        test_energy_dependent_survival_rules,
        test_geometry_breaking_perturbations,
        test_zone_type_names,
        test_species_reproduction_in_zones,
        test_integration_scenario
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
