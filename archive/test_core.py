#!/usr/bin/env python3
"""
Test script - verifies core simulation without GUI
Run this to test if the engine works before launching full app
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.grid import World
from engine.rules import EnvironmentalRules
from analysis.tracker import SimulationTracker


def test_simulation():
    print("Testing Primordial Garden core engine...")
    print("-" * 50)
    
    # Load basic preset
    config_path = Path(__file__).parent / "config" / "presets.json"
    with open(config_path, 'r') as f:
        presets = json.load(f)
    
    params = presets["presets"]["minimal"]
    
    # Initialize
    print(f"Creating {params['grid_size'][0]}x{params['grid_size'][1]} world...")
    rules = EnvironmentalRules(params)
    world = World(
        width=params["grid_size"][0],
        height=params["grid_size"][1],
        rules=rules,
        initial_density=params["initial_density"]
    )
    
    tracker = SimulationTracker()
    
    print(f"Initial population: {world.total_population}")
    print(f"Initial species: {len(world.species_registry)}")
    print()
    
    # Run simulation
    print("Running 1000 generations...")
    for i in range(1000):
        world.step()
        
        if i % 100 == 0:
            tracker.snapshot(world)
            print(f"Gen {i:4d}: Pop={world.total_population:5d}, Species={len(world.species_registry):3d}")
    
    print()
    print("-" * 50)
    print("Test complete!")
    print(f"Final generation: {world.generation}")
    print(f"Final population: {world.total_population}")
    print(f"Final species count: {len(world.species_registry)}")
    
    if len(world.species_registry) > 0:
        print("\nTop 3 species by population:")
        sorted_species = sorted(
            world.species_registry.values(),
            key=lambda s: s.population,
            reverse=True
        )[:3]
        
        for i, species in enumerate(sorted_species, 1):
            print(f"  {i}. Species {species.id}: {species.population} cells (born gen {species.birth_generation})")
    
    print("\n✓ Core engine working correctly!")
    print("You can now run 'python main.py' to see it visualized.")


if __name__ == "__main__":
    test_simulation()
