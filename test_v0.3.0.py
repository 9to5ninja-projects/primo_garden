"""
Test script for Primordial Garden v0.3.0 - The Predator Update
Tests intelligent movement, predator/prey dynamics, and ecosystem balance
"""
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.grid import Grid
from enhanced_engine.zones import ZoneType


def create_prey_species(name: str, can_flee: bool = False) -> Species:
    """Create a prey species"""
    strategy = "flee" if can_flee else "random"
    traits = SpeciesTraits(
        base_energy=100,
        energy_decay=2,
        photosynthesis_rate=4,
        energy_from_birth=30,
        reproduction_threshold=50,
        can_move=True if can_flee else False,
        movement_strategy=strategy,
        is_predator=False,
        can_be_consumed=True,
        color=(50, 255, 50) if not can_flee else (255, 255, 0),
        mutation_rate=0.01
    )
    return Species(name, traits)


def create_predator_species(name: str) -> Species:
    """Create a predator species"""
    traits = SpeciesTraits(
        base_energy=120,
        energy_decay=4,  # Hungry!
        photosynthesis_rate=1,  # Carnivore
        energy_from_birth=40,
        reproduction_threshold=60,
        can_move=True,
        movement_strategy="hunt",
        is_predator=True,
        hunting_efficiency=0.75,
        can_be_consumed=False,  # Top predator
        color=(255, 50, 50),
        mutation_rate=0.01
    )
    return Species(name, traits)


def create_seeker_species(name: str) -> Species:
    """Create an energy-seeking species"""
    traits = SpeciesTraits(
        base_energy=100,
        energy_decay=2,
        photosynthesis_rate=3,
        can_move=True,
        movement_strategy="energy_seeking",
        color=(100, 200, 255),
        mutation_rate=0.01
    )
    return Species(name, traits)


def run_predator_prey_test(generations: int = 200):
    """Test predator/prey dynamics"""
    print("=== PREDATOR/PREY DYNAMICS TEST ===\n")
    
    grid = Grid(100, 100, wrap=True)
    grid.setup_zones("quadrant")
    
    # Create species
    prey_stationary = create_prey_species("Stationary_Prey", can_flee=False)
    prey_fleeing = create_prey_species("Fleeing_Prey", can_flee=True)
    predator = create_predator_species("Apex_Predator")
    
    # Seed
    grid.seed_species(prey_stationary, 80, "random")
    grid.seed_species(prey_fleeing, 60, "random")
    grid.seed_species(predator, 20, "random")
    
    print("Initial Setup:")
    print(f"  Stationary Prey: 80 (can't move)")
    print(f"  Fleeing Prey: 60 (flee strategy)")
    print(f"  Predators: 20 (hunt strategy)")
    print()
    
    print(f"{'Gen':>6} | {'Prey1':>6} | {'Prey2':>6} | {'Pred':>5} | {'Total':>6} | {'Hunts':>6}")
    print("=" * 70)
    
    for _ in range(generations):
        grid.step()
        
        if grid.generation % 10 == 0:
            stats = grid.get_stats()
            
            # Count each species
            prey1_pop = prey_stationary.population
            prey2_pop = prey_fleeing.population
            pred_pop = predator.population
            
            print(f"{grid.generation:>6} | {prey1_pop:>6} | {prey2_pop:>6} | {pred_pop:>5} | "
                  f"{stats['population']:>6} | {stats['deaths']:>6}")
    
    print("=" * 70)
    print("\nFINAL RESULTS:")
    stats = grid.get_stats()
    
    if prey_stationary.population > 0:
        print(f"  ✓ Stationary Prey survived: {prey_stationary.population} cells")
    else:
        print(f"  ✗ Stationary Prey extinct")
    
    if prey_fleeing.population > 0:
        print(f"  ✓ Fleeing Prey survived: {prey_fleeing.population} cells")
    else:
        print(f"  ✗ Fleeing Prey extinct")
    
    if predator.population > 0:
        print(f"  ✓ Predators survived: {predator.population} cells")
    else:
        print(f"  ✗ Predators starved (prey extinct or too fast)")
    
    print(f"\n  Total living species: {stats['species_count']}")
    print(f"  Extinct species: {len(grid.species_registry.extinct_species)}")
    print(f"  Avg species age: {stats['avg_species_age']:.1f} generations")


def run_movement_intelligence_test(generations: int = 100):
    """Test movement strategy effectiveness"""
    print("\n\n=== MOVEMENT INTELLIGENCE TEST ===\n")
    
    grid = Grid(100, 100, wrap=True)
    grid.setup_zones("ring")  # Central paradise
    
    # Seekers vs Random movers
    seekers = create_seeker_species("Energy_Seekers")
    random_movers = Species("Random_Movers", SpeciesTraits(
        base_energy=100,
        energy_decay=2,
        photosynthesis_rate=3,
        can_move=True,
        movement_strategy="random",
        color=(255, 100, 255),
        mutation_rate=0.01
    ))
    
    grid.seed_species(seekers, 50, "edge")
    grid.seed_species(random_movers, 50, "edge")
    
    print("Testing: Can intelligent seekers dominate random movers?")
    print("  Zone: Ring world (paradise in center)")
    print("  Seekers: energy_seeking strategy")
    print("  Random: random walk")
    print()
    
    print(f"{'Gen':>6} | {'Seekers':>8} | {'Random':>7} | {'Winner':>10}")
    print("=" * 50)
    
    for _ in range(generations):
        grid.step()
        
        if grid.generation % 10 == 0:
            seeker_pop = seekers.population
            random_pop = random_movers.population
            
            if seeker_pop > random_pop:
                winner = "Seekers"
            elif random_pop > seeker_pop:
                winner = "Random"
            else:
                winner = "Tie"
            
            print(f"{grid.generation:>6} | {seeker_pop:>8} | {random_pop:>7} | {winner:>10}")
    
    print("=" * 50)
    print("\nRESULT:")
    if seekers.population > random_movers.population:
        print(f"  ✓ SEEKERS WON! ({seekers.population} vs {random_movers.population})")
        print("  Intelligence beats randomness!")
    elif random_movers.population > seekers.population:
        print(f"  ? Random won ({random_movers.population} vs {seekers.population})")
        print("  Luck or seekers got stuck?")
    else:
        print("  = Tie - both strategies viable")


if __name__ == "__main__":
    import sys
    
    test_type = "both"
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    
    if test_type in ["both", "predator", "prey"]:
        run_predator_prey_test(200)
    
    if test_type in ["both", "movement", "intelligence"]:
        run_movement_intelligence_test(100)
    
    print("\n\nRun options:")
    print("  python test_v0.3.0.py           # Run both tests")
    print("  python test_v0.3.0.py predator  # Predator/prey only")
    print("  python test_v0.3.0.py movement  # Movement intelligence only")
    print("\nFor full UI with graphs: python main_enhanced.py")
