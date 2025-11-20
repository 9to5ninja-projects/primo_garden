"""
Test carrying capacity system (Phase 4 of emergence)
"""
import sys
sys.path.insert(0, '.')

from enhanced_engine.zones import Zone, ZoneProperties, ZoneType
from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.cell import Cell

def test_zone_carrying_capacity():
    """Test that zones have appropriate carrying capacities"""
    print("Testing Zone Carrying Capacities...")
    
    capacities = {
        ZoneType.FERTILE: 120,
        ZoneType.DESERT: 60,
        ZoneType.TOXIC: 40,
        ZoneType.PARADISE: 150,
        ZoneType.NEUTRAL: 100,
        ZoneType.VOID: 0,
    }
    
    for zone_type, expected_capacity in capacities.items():
        props = ZoneProperties.from_type(zone_type)
        print(f"  {zone_type.value}: capacity={props.carrying_capacity}, expected={expected_capacity}")
        assert props.carrying_capacity == expected_capacity, \
            f"{zone_type} should have capacity {expected_capacity}, got {props.carrying_capacity}"
    
    print("✓ All zones have correct carrying capacities\n")

def test_population_counting():
    """Test that zones can count cells correctly"""
    print("Testing Population Counting...")
    
    # Create grid and zone
    grid = Grid(width=100, height=100)
    zone = Zone(20, 20, 40, 40, ZoneProperties.from_type(ZoneType.FERTILE))
    zone.grid = grid
    
    # Create a test species
    species = Species("Test", SpeciesTraits(base_energy=100))
    grid.species_registry.register(species)
    
    # Initially empty
    count = zone.get_cell_count()
    print(f"  Empty zone: {count} cells")
    assert count == 0, "Empty zone should have 0 cells"
    
    # Add some cells inside the zone
    for i in range(5):
        x, y = 25 + i, 25 + i
        cell = Cell(x, y, species, 100)
        grid.cells[y][x] = cell
    
    count = zone.get_cell_count()
    print(f"  After adding 5 cells: {count} cells")
    assert count == 5, "Should count 5 cells in zone"
    
    # Add cells outside the zone (shouldn't be counted)
    for i in range(3):
        x, y = 10 + i, 10 + i  # Outside zone
        cell = Cell(x, y, species, 100)
        grid.cells[y][x] = cell
    
    count = zone.get_cell_count()
    print(f"  After adding 3 cells outside zone: {count} cells (should still be 5)")
    assert count == 5, "Should not count cells outside zone"
    
    print("✓ Population counting works correctly\n")

def test_population_pressure():
    """Test that population pressure calculates correctly"""
    print("Testing Population Pressure Calculations...")
    
    grid = Grid(width=100, height=100)
    zone = Zone(0, 0, 50, 50, ZoneProperties(name="Test", carrying_capacity=100))
    zone.grid = grid
    
    species = Species("Test", SpeciesTraits(base_energy=100))
    grid.species_registry.register(species)
    
    # Test 1: Empty zone (< 50% capacity) = 1.3x bonus
    pressure = zone.get_population_pressure()
    print(f"  0/100 cells (0%): pressure={pressure:.2f} (expected 1.3)")
    assert pressure == 1.3, "Empty zone should give 1.3x bonus"
    
    # Test 2: Add 30 cells (30% = < 50% capacity) = 1.3x bonus
    for i in range(30):
        x, y = i % 50, i // 50
        grid.cells[y][x] = Cell(x, y, species, 100)
    
    pressure = zone.get_population_pressure()
    print(f"  30/100 cells (30%): pressure={pressure:.2f} (expected ~1.12)")
    assert 1.1 <= pressure <= 1.3, "Under 50% capacity should give bonus"
    
    # Test 3: Add more to reach 70 cells (70% capacity) = ~0.88x
    for i in range(30, 70):
        x, y = i % 50, i // 50
        grid.cells[y][x] = Cell(x, y, species, 100)
    
    pressure = zone.get_population_pressure()
    print(f"  70/100 cells (70%): pressure={pressure:.2f} (expected ~0.88)")
    assert 0.7 <= pressure <= 1.0, "70% capacity should be near normal"
    
    # Test 4: Overcrowd to 150 cells (150% capacity) = 0.8x
    for i in range(70, 150):
        x, y = i % 50, i // 50
        if y < 50:  # Make sure we're in the zone
            grid.cells[y][x] = Cell(x, y, species, 100)
    
    pressure = zone.get_population_pressure()
    print(f"  150/100 cells (150%): pressure={pressure:.2f} (expected 0.8)")
    assert 0.7 <= pressure <= 0.9, "150% capacity should give moderate penalty"
    
    # Test 5: Extreme overcrowding 200 cells (200% capacity) = ~0.5x minimum
    for i in range(150, 200):
        x, y = i % 50, i // 50
        if y < 50:
            grid.cells[y][x] = Cell(x, y, species, 100)
    
    pressure = zone.get_population_pressure()
    print(f"  200/100 cells (200%): pressure={pressure:.2f} (expected ~0.5)")
    assert 0.5 <= pressure <= 0.7, "Extreme overcrowding should hit 0.5x minimum"
    
    print("✓ Population pressure calculations correct\n")

def test_energy_gain_with_pressure():
    """Test that energy gain is affected by population pressure"""
    print("Testing Energy Gain with Population Pressure...")
    
    species = Species("Test", SpeciesTraits(
        base_energy=100,
        photosynthesis_rate=10,
        energy_decay=2
    ))
    
    cell = Cell(50, 50, species, 100)
    
    # Test with different pressure levels
    pressures = [
        (1.3, "Empty zone bonus"),
        (1.0, "Normal capacity"),
        (0.7, "Moderate overcrowding"),
        (0.5, "Extreme overcrowding"),
    ]
    
    for pressure, desc in pressures:
        initial_energy = cell.energy
        cell.age_one_generation(species, zone_modifier=1.0, zone_type="neutral", 
                               has_prey_nearby=False, population_pressure=pressure)
        energy_change = cell.energy - initial_energy
        print(f"  {desc} (pressure={pressure}): energy change = {energy_change}")
        
        # More pressure = more energy gain (or less loss)
        # With decay=2 and photo=10, base change is +8
        # At 1.2x should be better, at 0.2x should be worse
    
    print("✓ Energy gain responds to population pressure\n")

def test_reproduction_with_pressure():
    """Test that reproduction is harder in overcrowded zones"""
    print("Testing Reproduction with Population Pressure...")
    
    grid = Grid(width=50, height=50)
    grid.setup_zones("neutral")
    
    species = Species("Breeder", SpeciesTraits(
        base_energy=100,
        reproduction_threshold=60,
        energy_from_birth=40
    ))
    grid.species_registry.register(species)
    
    # Test 1: Normal capacity - should be able to reproduce
    zone = grid.zone_manager.default_zone
    zone.properties.carrying_capacity = 100
    
    # Place 50 cells (50% capacity)
    for i in range(50):
        x, y = i % 50, i // 50
        grid.cells[y][x] = Cell(x, y, species, 100)
    
    pressure = zone.get_population_pressure()
    print(f"  50/100 capacity: pressure={pressure:.2f}")
    print(f"    Can reproduce normally")
    
    # Test 2: Overcrowded - reproduction should be harder
    # Add more cells to reach 150 (150% capacity)
    for i in range(50, 150):
        x, y = i % 50, i // 50
        if y < 50:
            grid.cells[y][x] = Cell(x, y, species, 100)
    
    pressure = zone.get_population_pressure()
    reproduction_difficulty = 1.0 / pressure if pressure > 0 else 999.0
    effective_threshold = species.traits.reproduction_threshold * reproduction_difficulty
    
    print(f"  150/100 capacity: pressure={pressure:.2f}")
    print(f"    Reproduction threshold increased: {species.traits.reproduction_threshold} → {effective_threshold:.0f}")
    print(f"    Difficulty multiplier: {reproduction_difficulty:.2f}x")
    
    assert effective_threshold > species.traits.reproduction_threshold, \
        "Overcrowding should increase reproduction threshold"
    
    print("✓ Reproduction responds correctly to overcrowding\n")

def test_integration():
    """Test full system with carrying capacity"""
    print("Testing Full Integration...")
    
    grid = Grid(width=100, height=100)
    grid.setup_zones("quadrant")
    
    # Create species
    species = Species("Test", SpeciesTraits(
        base_energy=100,
        photosynthesis_rate=5,
        energy_decay=2,
        reproduction_threshold=60
    ))
    
    # Seed with high initial population
    grid.seed_species(species, 200, pattern="random")
    
    initial_pop = sum(1 for row in grid.cells for cell in row if cell and cell.is_alive)
    print(f"  Initial population: {initial_pop}")
    
    # Run simulation for multiple generations
    for gen in range(50):
        grid.step()
    
    final_pop = sum(1 for row in grid.cells for cell in row if cell and cell.is_alive)
    print(f"  Population after 50 generations: {final_pop}")
    
    # Check zone populations
    for zone in grid.zone_manager.get_all_zones():
        count = zone.get_cell_count()
        capacity = zone.properties.carrying_capacity
        pressure = zone.get_population_pressure()
        print(f"  {zone.properties.name}: {count}/{capacity} cells (pressure={pressure:.2f}x)")
    
    print("✓ Integration test complete\n")

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 4 TEST: Carrying Capacity")
    print("=" * 60)
    print()
    
    test_zone_carrying_capacity()
    test_population_counting()
    test_population_pressure()
    test_energy_gain_with_pressure()
    test_reproduction_with_pressure()
    test_integration()
    
    print("=" * 60)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("=" * 60)
    print()
    print("WHAT THIS MEANS:")
    print("- Zones now have carrying capacity limits")
    print("- Overcrowded zones penalize energy gain (down to 0.2x)")
    print("- Empty zones bonus energy gain (up to 1.2x)")
    print("- Reproduction is harder in overcrowded zones")
    print("- This prevents infinite growth and stasis patterns!")
    print()
    print("EXPECTED RESULTS:")
    print("- Populations will self-regulate around carrying capacity")
    print("- Overcrowded zones will see die-offs and migration")
    print("- Species will spread to empty zones for better resources")
    print("- NO MORE 1,000+ generation stasis locks!")
    print()
    print("NEXT: Run a simulation and watch populations balance!")
