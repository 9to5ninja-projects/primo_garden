"""
Primordial Garden v0.3.0 - Enhanced Mode
Run with: python main_enhanced.py

New features in v0.3.0:
- Intelligent movement (energy-seeking, fleeing, hunting)
- Predator/prey system with consumption mechanics
- Real-time graphs (press G to toggle)

Features from v0.2.0:
- Energy system with decay and photosynthesis
- Environmental zones (Fertile, Desert, Toxic, Paradise)
- Species designer for custom traits
- Cell mobility
- Zone-based mutations
"""

import pygame
import sys
from pathlib import Path
from datetime import datetime
import csv

# Import enhanced engine
from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.zones import ZoneType

# Import existing visualization (reuse optimized renderer concept)
from visualization.renderer import Renderer as BaseRenderer
from visualization.live_graphs import LiveGraphs


def simple_species_creator():
    """Terminal-based species creation (simpler than full GUI)"""
    print("\n=== Species Designer ===")
    print("Create your custom species!\n")
    
    species_list = []
    
    while True:
        name = input(f"Species name (or 'done' to finish, 'quick' for preset): ").strip()
        
        if name.lower() == 'done':
            break
        elif name.lower() == 'quick':
            # Quick presets
            print("\nQuick Presets:")
            print("1. Balanced - Standard traits")
            print("2. Efficient - Low energy needs")
            print("3. Mobile - Can move around")
            print("4. Resilient - High energy storage")
            print("5. Predator - Hunts other species")
            print("6. Seeker - Seeks energy-rich zones")
            choice = input("Choose (1-6): ").strip()
            
            if choice == '1':
                traits = SpeciesTraits(base_energy=100, energy_decay=2, photosynthesis_rate=3,
                                     color=(0, 255, 0))
                name = "Balanced"
            elif choice == '2':
                traits = SpeciesTraits(base_energy=80, energy_decay=1, photosynthesis_rate=4,
                                     color=(100, 255, 100))
                name = "Efficient"
            elif choice == '3':
                traits = SpeciesTraits(base_energy=120, energy_decay=3, photosynthesis_rate=3,
                                     can_move=True, movement_cost=5, movement_strategy="random",
                                     color=(0, 200, 255))
                name = "Mobile"
            elif choice == '4':
                traits = SpeciesTraits(base_energy=150, energy_decay=2, photosynthesis_rate=2,
                                     color=(255, 200, 0))
                name = "Resilient"
            elif choice == '5':
                traits = SpeciesTraits(base_energy=120, energy_decay=4, photosynthesis_rate=1,
                                     can_move=True, movement_cost=6, movement_strategy="hunt",
                                     is_predator=True, hunting_efficiency=0.75,
                                     color=(255, 0, 0))
                name = "Predator"
            else:  # 6
                traits = SpeciesTraits(base_energy=100, energy_decay=2, photosynthesis_rate=2,
                                     can_move=True, movement_cost=4, movement_strategy="energy_seeking",
                                     color=(255, 255, 0))
                name = "Seeker"
        else:
            # Custom configuration
            print(f"\nConfiguring {name}:")
            try:
                energy = int(input(f"  Base energy (50-200, default 100): ") or "100")
                decay = int(input(f"  Energy decay (1-10, default 2): ") or "2")
                photo = int(input(f"  Photosynthesis rate (0-20, default 3): ") or "3")
                can_move = input(f"  Can move? (y/n, default n): ").lower() == 'y'
                
                movement_strategy = "random"
                is_predator = False
                if can_move:
                    print(f"  Movement strategies: random, energy_seeking, flee, hunt")
                    movement_strategy = input(f"  Strategy (default random): ").strip() or "random"
                    is_predator = input(f"  Is predator? (y/n, default n): ").lower() == 'y'
                
                r = int(input(f"  Color R (0-255, default 0): ") or "0")
                g = int(input(f"  Color G (0-255, default 255): ") or "255")
                b = int(input(f"  Color B (0-255, default 0): ") or "0")
                
                traits = SpeciesTraits(
                    base_energy=energy,
                    energy_decay=decay,
                    photosynthesis_rate=photo,
                    can_move=can_move,
                    movement_strategy=movement_strategy,
                    is_predator=is_predator,
                    color=(r, g, b)
                )
            except ValueError:
                print("Invalid input, using defaults")
                traits = SpeciesTraits()
        
        pop = int(input(f"Initial population for {name} (10-500, default 100): ") or "100")
        pop = max(10, min(500, pop))
        
        species = Species(name=name, traits=traits)
        species_list.append((species, pop))
        print(f"✓ Added {name} with {pop} cells\n")
        
        if len(species_list) >= 5:
            print("Maximum 5 species reached.")
            break
    
    return species_list


def main():
    """Enhanced simulation entry point"""
    print("=" * 60)
    print("PRIMORDIAL GARDEN v0.3.0 - ENHANCED MODE")
    print("=" * 60)
    print("\nNew in v0.3.0:")
    print("  • Intelligent movement (energy-seeking, fleeing, hunting)")
    print("  • Predator/prey dynamics")
    print("  • Real-time graphs (press G to view)")
    print("\nCore Features:")
    print("  • Energy system with zones")
    print("  • Cell mobility")
    print("  • Custom species designer")
    print()
    
    # Configuration
    try:
        width = int(input("Grid width (default 200): ") or "200")
        height = int(input("Grid height (default 150): ") or "150")
    except ValueError:
        width, height = 200, 150
    
    # Create grid
    grid = Grid(width, height, wrap=True)
    
    # Setup zones
    print("\nZone layouts:")
    print("1. Neutral (no zones)")
    print("2. Random zones")
    print("3. Quadrants (4 different zones)")
    print("4. Ring world (central paradise)")
    zone_choice = input("Choose (1-4, default 2): ").strip() or "2"
    
    zone_map = {"1": "neutral", "2": "random", "3": "quadrant", "4": "ring"}
    grid.setup_zones(zone_map.get(zone_choice, "random"))
    
    # Create species
    print("\nSpecies Creation:")
    print("You can create custom species or use presets")
    species_configs = simple_species_creator()
    
    if not species_configs:
        print("No species created. Creating default species...")
        default_species = Species("Default", SpeciesTraits())
        species_configs = [(default_species, 100)]
    
    # Seed species
    for species, pop in species_configs:
        pattern = input(f"Placement for {species.name} (random/center/edge, default random): ").strip() or "random"
        grid.seed_species(species, pop, pattern)
    
    # Run simulation
    print("\n" + "=" * 60)
    print("Starting simulation...")
    print("Controls: SPACE=pause, 1-5=speed, G=graphs, S=export, Q=quit")
    print("=" * 60 + "\n")
    
    run_enhanced_simulation(grid, width, height)


def run_enhanced_simulation(grid, width, height):
    """Run the enhanced simulation with pygame"""
    # Initialize pygame
    pygame.init()
    cell_size = 4
    screen_width = width * cell_size + 400  # Extra space for stats
    screen_height = height * cell_size
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Primordial Garden v0.2.0 - Enhanced")
    clock = pygame.time.Clock()
    
    # Simulation state
    running = True
    paused = False
    speed = 1
    export_data = []
    show_graphs = False
    
    # Initialize graphs
    graphs = LiveGraphs(max_history=500)
    graph_window = None
    
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    while running:
        # Events
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
                    # Export
                    save_data(export_data)
                elif event.key == pygame.K_g:
                    # Toggle graphs
                    show_graphs = not show_graphs
                    if show_graphs and graph_window is None:
                        # Create separate window for graphs
                        graph_window = pygame.display.set_mode((1200, 800))
                        pygame.display.set_caption("Primordial Garden - Live Graphs")
                    elif not show_graphs and graph_window:
                        # Return to main window
                        graph_window = None
                        pygame.display.set_mode((screen_width, screen_height))
                        pygame.display.set_caption("Primordial Garden v0.2.0 - Enhanced")
                elif event.key == pygame.K_q:
                    running = False
        
        # Update
        if not paused:
            for _ in range(speed):
                grid.step()
                if grid.generation % 10 == 0:
                    stats = grid.get_stats()
                    export_data.append(stats)
        
        # Update graphs with current stats
        current_stats = grid.get_stats()
        graphs.update(current_stats)
        
        # Render
        if show_graphs and graph_window:
            # Display graphs
            graph_image = graphs.render()
            if graph_image is not None:
                # Convert numpy array to pygame surface
                graph_surface = pygame.surfarray.make_surface(
                    graph_image.swapaxes(0, 1)
                )
                graph_window.fill((0, 0, 0))
                graph_window.blit(graph_surface, (0, 0))
        else:
            # Display normal simulation
            screen.fill((0, 0, 0))
            draw_enhanced_grid(screen, grid, cell_size)
            draw_enhanced_stats(screen, grid, width * cell_size, speed, paused, font, small_font)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Save on exit
    save_data(export_data)
    
    # Clean up graphs
    graphs.close()
    
    pygame.quit()


def draw_enhanced_grid(screen, grid, cell_size):
    """Draw grid with zones and energy-based brightness"""
    # Draw zones first
    for zone in grid.zone_manager.get_all_zones():
        zone_rect = pygame.Rect(
            zone.x * cell_size,
            zone.y * cell_size,
            zone.width * cell_size,
            zone.height * cell_size
        )
        pygame.draw.rect(screen, zone.properties.background_color, zone_rect)
    
    # Draw cells with energy-based brightness
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.cells[y][x]
            if cell and cell.is_alive:
                species = grid.species_registry.get(cell.species_id)
                if species:
                    color = cell.get_color(species)
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, color, rect)


def draw_enhanced_stats(screen, grid, panel_x, speed, paused, font, small_font):
    """Draw stats panel"""
    stats = grid.get_stats()
    
    # Background
    pygame.draw.rect(screen, (30, 30, 40), (panel_x, 0, 400, screen.get_height()))
    
    y_offset = 20
    line_height = 30
    
    stat_lines = [
        f"Generation: {stats['generation']}",
        f"Population: {stats['population']}",
        f"Species: {stats['species_count']}",
        f"",
        f"This Generation:",
        f"  Births: {stats['births']}",
        f"  Deaths: {stats['deaths']}",
        f"  Mutations: {stats['mutations']}",
        f"",
        f"Avg Species Age:",
        f"  {stats['avg_species_age']:.1f} gens",
        f"",
        f"Speed: {speed}x {'(PAUSED)' if paused else ''}",
        f"",
        f"Controls:",
        f"SPACE: Pause",
        f"1-5: Speed",
        f"G: Toggle Graphs",
        f"S: Export Data",
        f"Q: Quit"
    ]
    
    for i, line in enumerate(stat_lines):
        color = (200, 200, 200)
        if ":" in line and not line.startswith(" "):
            color = (150, 200, 255)
        
        text = small_font.render(line, True, color)
        screen.blit(text, (panel_x + 10, y_offset + i * line_height))
    
    # Top species
    top_y = 650
    title = font.render("Top Species:", True, (150, 200, 255))
    screen.blit(title, (panel_x + 10, top_y))
    
    species_list = sorted(grid.species_registry.get_living_species(),
                         key=lambda s: s.population, reverse=True)[:5]
    
    for i, species in enumerate(species_list):
        text = small_font.render(f"{species.name[:15]}: {species.population}", 
                                True, species.traits.color)
        screen.blit(text, (panel_x + 10, top_y + 30 + i * 25))


def save_data(export_data):
    """Save simulation data to CSV"""
    if not export_data:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = Path("exports") / f"enhanced_{timestamp}.csv"
    
    with open(filepath, 'w', newline='') as f:
        if export_data:
            writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
    
    print(f"\n✓ Saved data to {filepath}")


if __name__ == "__main__":
    main()
