#!/usr/bin/env python3
"""
Primordial Garden - Emergent Life Simulator
Main entry point
"""

import pygame
import sys
import json
from pathlib import Path

from engine.grid import World
from engine.rules import EnvironmentalRules
from visualization.renderer import Renderer
from analysis.tracker import SimulationTracker


def load_preset(preset_name="primordial_soup"):
    """Load simulation parameters from config"""
    config_path = Path(__file__).parent / "config" / "presets.json"
    with open(config_path, 'r') as f:
        presets = json.load(f)
    return presets["presets"][preset_name]


def main():
    # Load parameters
    params = load_preset("primordial_soup")
    
    # Initialize components
    rules = EnvironmentalRules(params)
    world = World(
        width=params["grid_size"][0],
        height=params["grid_size"][1],
        rules=rules,
        initial_density=params["initial_density"]
    )
    
    renderer = Renderer(world, screen_size=(1600, 900))
    tracker = SimulationTracker()
    
    # Simulation state
    running = True
    paused = False
    speed = 1  # Simulation speed multiplier
    show_stats = True
    
    clock = pygame.time.Clock()
    frame_count = 0
    
    print("Primordial Garden - Controls:")
    print("  SPACE: Pause/Resume")
    print("  1-5: Set speed (1x to 100x)")
    print("  S: Toggle stats overlay")
    print("  R: Reset simulation")
    print("  Q/ESC: Quit")
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_1:
                    speed = 1
                elif event.key == pygame.K_2:
                    speed = 5
                elif event.key == pygame.K_3:
                    speed = 10
                elif event.key == pygame.K_4:
                    speed = 50
                elif event.key == pygame.K_5:
                    speed = 100
                elif event.key == pygame.K_s:
                    show_stats = not show_stats
                elif event.key == pygame.K_r:
                    world.reset(params["initial_density"])
                    tracker = SimulationTracker()
                    frame_count = 0
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
        
        # Simulation step
        if not paused:
            for _ in range(speed):
                world.step()
                frame_count += 1
                
                # Track every 10 generations
                if frame_count % 10 == 0:
                    tracker.snapshot(world)
        
        # Render (skip frames at high speeds for better performance)
        if speed <= 10 or frame_count % (speed // 10) == 0:
            renderer.draw_frame(show_stats, speed, paused)
        
        # Cap framerate
        clock.tick(60)
    
    # Cleanup - close pygame window first to prevent lockup
    pygame.quit()
    
    print(f"\nSimulation ended at generation {world.generation}")
    print(f"Final species count: {len(world.species_registry)}")
    print(f"Final population: {world.total_population}")
    
    # Offer to export data
    export = input("\nExport simulation data? (y/n): ")
    if export.lower() == 'y':
        tracker.export()  # Auto-generates timestamped filename in exports/
    
    sys.exit()


if __name__ == "__main__":
    main()
