"""
Test complexity-linked intelligence system (Phase 1 of emergence)
"""
import sys
sys.path.insert(0, '.')

from enhanced_engine.species_enhanced import Species, SpeciesTraits

def test_complexity_strategies():
    """Test that complexity levels restrict available strategies"""
    print("Testing Complexity → Strategy Restrictions...")
    
    # Complexity 1: Only random
    traits1 = SpeciesTraits(complexity=1)
    available1 = traits1.get_available_strategies()
    print(f"  Complexity 1: {available1}")
    assert available1 == ["random"], f"Expected ['random'], got {available1}"
    
    # Complexity 2: Random, energy_seeking, flee
    traits2 = SpeciesTraits(complexity=2)
    available2 = traits2.get_available_strategies()
    print(f"  Complexity 2: {available2}")
    assert "energy_seeking" in available2, "Complexity 2 should have energy_seeking"
    assert "flee" in available2, "Complexity 2 should have flee"
    assert "hunt" not in available2, "Complexity 2 shouldn't have hunt yet"
    
    # Complexity 3: All strategies including hunt
    traits3 = SpeciesTraits(complexity=3)
    available3 = traits3.get_available_strategies()
    print(f"  Complexity 3: {available3}")
    assert "hunt" in available3, "Complexity 3 should have hunt"
    
    # Complexity 4+: All strategies
    traits4 = SpeciesTraits(complexity=4)
    available4 = traits4.get_available_strategies()
    print(f"  Complexity 4+: {available4}")
    
    print("✓ All complexity levels have correct strategy restrictions\n")

def test_strategy_validation():
    """Test that invalid strategies are auto-corrected"""
    print("Testing Strategy Validation...")
    
    # Try to create a complexity 1 organism with "hunt" strategy (should auto-correct)
    traits = SpeciesTraits(complexity=1, movement_strategy="hunt")
    print(f"  Created complexity 1 with 'hunt' → strategy corrected to '{traits.movement_strategy}'")
    assert traits.movement_strategy == "random", "Should auto-correct to random"
    
    # Try complexity 2 with "hunt" (should auto-correct)
    traits2 = SpeciesTraits(complexity=2, movement_strategy="hunt")
    print(f"  Created complexity 2 with 'hunt' → strategy corrected to '{traits2.movement_strategy}'")
    assert traits2.movement_strategy in ["random", "energy_seeking", "flee"], "Should auto-correct"
    
    # Complexity 3 with "hunt" (should be valid)
    traits3 = SpeciesTraits(complexity=3, movement_strategy="hunt")
    print(f"  Created complexity 3 with 'hunt' → strategy is '{traits3.movement_strategy}'")
    assert traits3.movement_strategy == "hunt", "Should keep hunt for complexity 3"
    
    print("✓ Invalid strategies are auto-corrected\n")

def test_strategy_mutation():
    """Test that strategies can mutate and respect complexity"""
    print("Testing Strategy Mutation...")
    
    # Create a simple organism (complexity 1)
    species1 = Species(
        name="Simple",
        traits=SpeciesTraits(complexity=1, movement_strategy="random")
    )
    
    # Mutate many times and check strategies stay valid
    mutations_checked = 0
    strategy_changes = 0
    for i in range(100):
        mutant = species1.mutate(generation=i)
        mutations_checked += 1
        
        # Check strategy is valid for complexity
        if not mutant.traits.is_strategy_valid():
            print(f"  ✗ Invalid strategy '{mutant.traits.movement_strategy}' for complexity {mutant.traits.complexity}")
            assert False, "Mutant has invalid strategy!"
        
        if mutant.traits.movement_strategy != species1.traits.movement_strategy:
            strategy_changes += 1
    
    print(f"  Checked {mutations_checked} mutations, all strategies valid")
    print(f"  Strategy changed {strategy_changes} times (~{strategy_changes}% rate)")
    
    # Create a complex organism (complexity 3)
    species3 = Species(
        name="Complex",
        traits=SpeciesTraits(complexity=3, movement_strategy="hunt", can_move=True)
    )
    
    # Mutate and see if strategies evolve
    strategies_seen = set()
    for i in range(200):
        mutant = species3.mutate(generation=i)
        if mutant.traits.complexity >= 3:  # Only track if stays complex
            strategies_seen.add(mutant.traits.movement_strategy)
    
    print(f"  Complex species showed {len(strategies_seen)} different strategies: {strategies_seen}")
    assert len(strategies_seen) >= 2, "Complex species should explore multiple strategies"
    
    print("✓ Strategy mutations work correctly\n")

def test_complexity_evolution_pressure():
    """Test that complexity can increase/decrease through mutation"""
    print("Testing Complexity Evolution...")
    
    # Start with complexity 2 (middle value for better range)
    species = Species(
        name="Evolving",
        traits=SpeciesTraits(complexity=2, movement_strategy="random")
    )
    
    complexity_levels = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    # Generate many mutations
    for i in range(1000):  # More mutations to see full range
        mutant = species.mutate(generation=i)
        complexity_levels[mutant.traits.complexity] += 1
        
        # Check that if complexity increased, strategy might have upgraded
        if mutant.traits.complexity > species.traits.complexity:
            available = mutant.traits.get_available_strategies()
            assert mutant.traits.movement_strategy in available, "Strategy should be valid after complexity increase"
    
    print(f"  Complexity distribution over 1000 mutations:")
    for level, count in sorted(complexity_levels.items()):
        pct = (count/10) if count > 0 else 0
        print(f"    Level {level}: {count} ({pct:.1f}%)")
    
    # Should see at least complexity 1, 2, 3 (±1 from starting point of 2)
    non_zero = sum(1 for c in complexity_levels.values() if c > 0)
    print(f"  Saw {non_zero} different complexity levels")
    assert non_zero >= 3, f"Should see at least 3 different complexity levels, got {non_zero}"
    
    print("✓ Complexity can evolve up and down\n")

def test_preset_species():
    """Test that preset species have valid complexity/strategy combos"""
    print("Testing Preset Species...")
    
    presets = {
        "Balanced": SpeciesTraits(
            complexity=1, movement_strategy="random",
            energy_source="photosynthesis"
        ),
        "Mobile": SpeciesTraits(
            complexity=2, movement_strategy="random", can_move=True,
            energy_source="photosynthesis"
        ),
        "Predator": SpeciesTraits(
            complexity=3, movement_strategy="hunt", can_move=True,
            is_predator=True, energy_source="predation"
        ),
        "Seeker": SpeciesTraits(
            complexity=2, movement_strategy="energy_seeking", can_move=True,
            energy_source="hybrid"
        ),
    }
    
    for name, traits in presets.items():
        assert traits.is_strategy_valid(), f"{name} has invalid strategy for complexity"
        print(f"  ✓ {name}: complexity {traits.complexity}, strategy '{traits.movement_strategy}'")
    
    print("✓ All presets are valid\n")

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 TEST: Complexity-Linked Intelligence")
    print("=" * 60)
    print()
    
    test_complexity_strategies()
    test_strategy_validation()
    test_strategy_mutation()
    test_complexity_evolution_pressure()
    test_preset_species()
    
    print("=" * 60)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("=" * 60)
    print()
    print("WHAT THIS MEANS:")
    print("- Simple organisms (complexity 1) can only move randomly")
    print("- Aware organisms (complexity 2) can seek energy and flee")
    print("- Strategic organisms (complexity 3+) can hunt prey")
    print("- Species can evolve higher complexity to unlock smarter behaviors")
    print("- In harsh environments, smarter organisms will have survival advantage")
    print("- Natural selection will favor complexity despite the energy cost!")
    print()
    print("NEXT: Run a simulation and watch species evolve intelligence!")
