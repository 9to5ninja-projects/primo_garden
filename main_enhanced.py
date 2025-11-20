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
import json

# Import enhanced engine
from enhanced_engine.grid import Grid
from enhanced_engine.species_enhanced import Species, SpeciesTraits
from enhanced_engine.zones import ZoneType
from enhanced_engine.population_manager import PopulationManager

# Import existing visualization (reuse optimized renderer concept)
from visualization.renderer import Renderer as BaseRenderer
from visualization.live_graphs import LiveGraphs


def save_species_config(species_configs, filename="last_species_config.json"):
    """Save species configuration to file (v0.9.0: Updated for behavioral redesign)"""
    config_data = []
    for species, pop in species_configs:
        config_data.append({
            "name": species.name,
            "population": pop,
            "traits": {
                "base_energy": species.traits.base_energy,
                "energy_decay": species.traits.energy_decay,
                "photosynthesis_rate": species.traits.photosynthesis_rate,
                "complexity": species.traits.complexity,
                "metabolic_efficiency": species.traits.metabolic_efficiency,
                "heat_tolerance": species.traits.heat_tolerance,
                "cold_tolerance": species.traits.cold_tolerance,
                "toxin_resistance": species.traits.toxin_resistance,
                "max_lifespan": species.traits.max_lifespan,
                "energy_source": species.traits.energy_source,
                "starvation_threshold": species.traits.starvation_threshold,
                "optimal_zone_bonus": species.traits.optimal_zone_bonus,
                "colonial_affinity": species.traits.colonial_affinity,
                "cluster_reproduction_bonus": species.traits.cluster_reproduction_bonus,
                "hunting_efficiency": species.traits.hunting_efficiency,
                "color": species.traits.color
            }
        })
    
    with open(filename, 'w') as f:
        json.dump(config_data, f, indent=2)


def load_species_config(filename="last_species_config.json"):
    """Load species configuration from file (v0.9.0: Handles old and new formats)"""
    try:
        with open(filename, 'r') as f:
            config_data = json.load(f)
        
        species_list = []
        for config in config_data:
            trait_data = config["traits"].copy()
            
            # Remove old v0.8.0 parameters if present
            trait_data.pop('can_move', None)
            trait_data.pop('movement_strategy', None)
            trait_data.pop('is_predator', None)
            trait_data.pop('movement_cost', None)  # Now auto-calculated
            
            # Add new v0.9.0 parameters with defaults if missing
            trait_data.setdefault('colonial_affinity', 1.2)
            trait_data.setdefault('cluster_reproduction_bonus', 1.3)
            trait_data.setdefault('hunting_efficiency', 0.5)
            
            traits = SpeciesTraits(**trait_data)
            species = Species(name=config["name"], traits=traits)
            species_list.append((species, config["population"]))
        
        print("✓ Loaded previous configuration (upgraded to v0.9.0)")
        return species_list
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"⚠ Could not load config: {e}")
        return None


def simple_species_creator():
    """Terminal-based species creation (simpler than full GUI)"""
    print("\n=== Species Designer ===")
    
    # Check for saved configuration
    if Path("last_species_config.json").exists():
        replay = input("Replay last species configuration? (y/n, default n): ").strip().lower()
        if replay == 'y':
            species_list = load_species_config()
            if species_list:
                print(f"✓ Loaded {len(species_list)} species from last run:")
                for species, pop in species_list:
                    print(f"  - {species.name}: {pop} cells")
                return species_list
    
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
                                     complexity=1, metabolic_efficiency=1.0,
                                     max_lifespan=300, energy_source="photosynthesis",
                                     colonial_affinity=1.2, cluster_reproduction_bonus=1.3,
                                     color=(0, 255, 0))
                name = "Balanced"
            elif choice == '2':
                traits = SpeciesTraits(base_energy=80, energy_decay=1, photosynthesis_rate=4,
                                     complexity=1, metabolic_efficiency=0.8,
                                     heat_tolerance=0.7, toxin_resistance=0.6,
                                     max_lifespan=400, energy_source="photosynthesis",
                                     optimal_zone_bonus=2.5,
                                     colonial_affinity=1.3, cluster_reproduction_bonus=1.4,
                                     color=(100, 255, 100))
                name = "Efficient"
            elif choice == '3':
                traits = SpeciesTraits(base_energy=120, energy_decay=3, photosynthesis_rate=3,
                                     complexity=2, metabolic_efficiency=1.2,
                                     max_lifespan=250, energy_source="photosynthesis",
                                     colonial_affinity=1.1, cluster_reproduction_bonus=1.2,
                                     color=(0, 200, 255))
                name = "Mobile"
            elif choice == '4':
                traits = SpeciesTraits(base_energy=150, energy_decay=2, photosynthesis_rate=2,
                                     complexity=1, metabolic_efficiency=0.9,
                                     heat_tolerance=0.8, cold_tolerance=0.8, toxin_resistance=0.7,
                                     max_lifespan=500, energy_source="photosynthesis",
                                     optimal_zone_bonus=2.0,
                                     colonial_affinity=1.4, cluster_reproduction_bonus=1.5,
                                     color=(255, 200, 0))
                name = "Resilient"
            elif choice == '5':
                traits = SpeciesTraits(base_energy=120, energy_decay=4, photosynthesis_rate=1,
                                     complexity=3, metabolic_efficiency=1.3,
                                     max_lifespan=150, energy_source="predation",
                                     starvation_threshold=20,
                                     hunting_efficiency=0.6,
                                     colonial_affinity=1.0, cluster_reproduction_bonus=1.1,
                                     color=(255, 0, 0))
                name = "Predator"
            else:  # 6
                traits = SpeciesTraits(base_energy=100, energy_decay=2, photosynthesis_rate=2,
                                     complexity=2, metabolic_efficiency=1.1,
                                     heat_tolerance=0.6, toxin_resistance=0.6,
                                     max_lifespan=350, energy_source="hybrid",
                                     colonial_affinity=1.2, cluster_reproduction_bonus=1.3,
                                     color=(255, 255, 0))
                name = "Seeker"
        else:
            # Custom configuration (v0.9.0: All organisms mobile, behavior from complexity)
            print(f"\nConfiguring {name}:")
            print("Note: All organisms can move. Behavior emerges from complexity:")
            print("  Complexity 1: Seeks energy (phototropism)")
            print("  Complexity 2: Flees from danger")
            print("  Complexity 3+: Hunts prey (50-80% efficiency)")
            try:
                energy = int(input(f"  Base energy (50-200, default 100): ") or "100")
                decay = int(input(f"  Energy decay (1-10, default 2): ") or "2")
                photo = int(input(f"  Photosynthesis rate (0-20, default 3): ") or "3")
                complexity = int(input(f"  Complexity level (1-5, default 1): ") or "1")
                complexity = max(1, min(5, complexity))
                
                colonial_affinity = float(input(f"  Colonial affinity (1.0-1.5, default 1.2): ") or "1.2")
                cluster_bonus = float(input(f"  Cluster reproduction bonus (1.0-2.0, default 1.3): ") or "1.3")
                
                r = int(input(f"  Color R (0-255, default 0): ") or "0")
                g = int(input(f"  Color G (0-255, default 255): ") or "255")
                b = int(input(f"  Color B (0-255, default 0): ") or "0")
                
                traits = SpeciesTraits(
                    base_energy=energy,
                    energy_decay=decay,
                    photosynthesis_rate=photo,
                    complexity=complexity,
                    colonial_affinity=colonial_affinity,
                    cluster_reproduction_bonus=cluster_bonus,
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
        
        # Removed 5 species limit - can add as many as desired
        if len(species_list) >= 10:
            more = input(f"You have {len(species_list)} species. Add more? (y/n, default n): ").strip().lower()
            if more != 'y':
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
    
    # Environmental shifting
    shift_env = input("\nEnable environmental changes? (y/n, default y): ").strip().lower()
    if shift_env != 'n':
        interval = input("Zone shift interval in generations (default 100): ").strip()
        interval = int(interval) if interval.isdigit() else 100
        grid.zone_manager.enable_shifting(interval)
        print(f"✓ Zones will shift every {interval} generations")
    
    # Create species
    print("\nSpecies Creation:")
    print("You can create custom species or use presets")
    species_configs = simple_species_creator()
    
    if not species_configs:
        print("No species created. Creating default species...")
        default_species = Species("Default", SpeciesTraits())
        species_configs = [(default_species, 100)]
    
    # Save configuration for replay
    save_species_config(species_configs)
    print(f"✓ Configuration saved (can replay with 'y' next time)\n")
    
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
    # Draw zones with semi-transparent overlays and borders
    for zone in grid.zone_manager.get_all_zones():
        zone_rect = pygame.Rect(
            zone.x * cell_size,
            zone.y * cell_size,
            zone.width * cell_size,
            zone.height * cell_size
        )
        # Draw zone background (semi-transparent)
        zone_surface = pygame.Surface((zone_rect.width, zone_rect.height))
        zone_surface.set_alpha(60)  # More visible
        zone_surface.fill(zone.properties.background_color)
        screen.blit(zone_surface, zone_rect.topleft)
        
        # Draw zone border for clarity
        border_color = tuple(min(255, c + 40) for c in zone.properties.background_color)
        pygame.draw.rect(screen, border_color, zone_rect, 2)  # 2px border
    
    # Draw cells with energy-based brightness
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.cells[y][x]
            if cell and cell.is_alive:
                species = grid.species_registry.get(cell.species_id)
                if species:
                    try:
                        color = cell.get_color(species)
                        # Validate color is RGB tuple
                        if isinstance(color, (tuple, list)) and len(color) == 3:
                            color = tuple(int(max(0, min(255, c))) for c in color)
                        else:
                            color = (100, 200, 100)  # Default green
                    except:
                        color = (100, 200, 100)  # Default green on error
                    
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, color, rect)


def draw_enhanced_stats(screen, grid, panel_x, speed, paused, font, small_font, pop_manager=None):
    """Draw stats panel"""
    stats = grid.get_stats()
    
    # Background
    pygame.draw.rect(screen, (30, 30, 40), (panel_x, 0, 400, screen.get_height()))
    
    y_offset = 20
    line_height = 30
    
    # Check for population pressure
    pressure_warning = ""
    if pop_manager:
        pop_stats = pop_manager.get_population_stats(grid.cells)
        pressure = pop_stats['total'] / pop_manager.total_cell_limit
        if pressure > 0.9:
            pressure_warning = "🔥 HIGH LOAD"
        elif pressure > 0.7:
            pressure_warning = "⚠️  BUSY"
    
    stat_lines = [
        f"Generation: {stats['generation']}",
        f"Population: {stats['population']} {pressure_warning}",
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
        f"Q: Quit",
        f"",
        f"--- Zones Guide ---",
        f"Forest Green: Fertile",
        f"  (1.2x energy, easy)",
        f"Tan: Desert",
        f"  (0.6x energy, harsh)",
        f"Dark Olive: Toxic",
        f"  (0.4x, high mutation)",
        f"Bright: Paradise",
        f"  (2x energy, ideal)",
        f"Gray: Neutral",
        f"  (1x energy, default)",
        f"",
        f"Zones shift every",
        f"50 generations!"
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
        # Show species with its actual color
        name_text = species.name[:20] if len(species.name) <= 20 else species.name[:17] + "..."
        complexity_indicator = f"[C{species.traits.complexity}]"
        
        text = small_font.render(f"{name_text}: {species.population}", 
                                True, species.traits.color)
        screen.blit(text, (panel_x + 10, top_y + 30 + i * 25))
        
        # Show complexity indicator
        comp_text = small_font.render(complexity_indicator, True, (150, 150, 150))
        screen.blit(comp_text, (panel_x + 280, top_y + 30 + i * 25))
    
    # Add organism color legend
    legend_y = top_y + 180
    legend_title = small_font.render("--- Organism Colors ---", True, (150, 200, 255))
    screen.blit(legend_title, (panel_x + 10, legend_y))
    
    legend_items = [
        ("Green: Photosynthesizers", (0, 200, 0)),
        ("Cyan: Advanced Plants", (0, 200, 200)),
        ("Yellow: Opportunists", (200, 200, 0)),
        ("Orange: Predators", (200, 100, 0)),
        ("Red: Apex Predators", (200, 0, 0)),
        ("", None),
        ("Vivid = Specialist", None),
        ("Muted = Generalist", None),
        ("Bright = High Energy", None),
        ("Dim = Low Energy", None),
    ]
    
    for i, (text_str, color) in enumerate(legend_items):
        if color:
            # Draw color swatch
            swatch_rect = pygame.Rect(panel_x + 10, legend_y + 25 + i * 20, 15, 15)
            pygame.draw.rect(screen, color, swatch_rect)
            text = small_font.render(text_str.split(":")[1] if ":" in text_str else text_str, 
                                    True, (180, 180, 180))
            screen.blit(text, (panel_x + 30, legend_y + 25 + i * 20))
        else:
            text = small_font.render(text_str, True, (150, 150, 150))
            screen.blit(text, (panel_x + 10, legend_y + 25 + i * 20))


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
