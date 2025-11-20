"""
Enhanced Grid system for Primordial Garden 2.0
Integrates energy, zones, mobility, and complex species interactions
"""
from typing import List, Tuple, Optional
from .cell import Cell
from .species_enhanced import Species, SpeciesRegistry
from .zones import Zone, ZoneManager, ZoneType, ZoneProperties
import random
import time
import numpy as np
from .grid_numba import count_all_neighbors


class Grid:
    """Main simulation grid with energy and zone support"""
    
    def __init__(self, width: int, height: int, wrap: bool = True):
        self.width = width
        self.height = height
        self.wrap = wrap
        
        # Grid structure
        self.cells = [[None for _ in range(width)] for _ in range(height)]
        
        # Numba-accelerated neighbor cache
        self._neighbor_cache = None
        self._neighbor_cache_generation = -1
        
        # Zone caches for performance
        self._zone_cache = {}  # (x, y) -> Zone
        self._zone_pressure_cache = {}  # Zone -> pressure
        self._zone_cache_generation = -1
        
        # Species management
        self.species_registry = SpeciesRegistry()
        
        # Zone management
        self.zone_manager = ZoneManager(width, height)
        
        # Statistics
        self.generation = 0
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
        
        # Performance profiling
        self.timing_stats = {
            'aging': 0.0,
            'movement': 0.0,
            'predation': 0.0,
            'reproduction': 0.0,
            'neighbor_counting': 0.0,
            'total_step': 0.0
        }
    
    def setup_zones(self, zone_layout: str = "random"):
        """Initialize environmental zones"""
        if zone_layout == "random":
            self.zone_manager.create_random_zones(num_zones=random.randint(3, 7))
        elif zone_layout == "quadrant":
            self.zone_manager.create_quadrant_zones()
        elif zone_layout == "ring":
            self.zone_manager.create_ring_world()
        # "neutral" = do nothing, entire grid stays neutral
        
        # Set grid reference for all zones (enables population counting)
        for zone in self.zone_manager.get_all_zones():
            zone.grid = self
        self.zone_manager.default_zone.grid = self
    
    def seed_species(self, species: Species, population: int, pattern: str = "random"):
        """Add initial population of a species to the grid"""
        self.species_registry.register(species)
        
        # Track zone where most cells are placed to set as native zone (Phase 3)
        zone_counts = {}
        
        cells_placed = 0
        attempts = 0
        max_attempts = population * 100  # Increased for better placement
        
        if pattern == "random":
            while cells_placed < population and attempts < max_attempts:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                
                if self.cells[y][x] is None:
                    zone = self.zone_manager.get_zone_at(x, y)
                    if zone.properties.can_enter:
                        self.cells[y][x] = Cell(x, y, species)
                        cells_placed += 1
                        
                        # Track zone placement
                        zone_name = zone.properties.name.lower().split()[0]
                        zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1
                
                attempts += 1
        
        elif pattern == "center":
            cx, cy = self.width // 2, self.height // 2
            
            # Add random offset for different species (so they don't all stack at exact center)
            num_existing_species = len(self.species_registry.get_living_species()) - 1  # -1 for current
            offset_angle = num_existing_species * 60  # Spread species around center
            import math
            offset_dist = num_existing_species * 15  # Distance from center
            cx += int(offset_dist * math.cos(math.radians(offset_angle)))
            cy += int(offset_dist * math.sin(math.radians(offset_angle)))
            
            # Seed stable blocks (2x2 squares) - Conway stable pattern
            # Spiral outward from offset center placing 2x2 blocks
            spiral_radius = 0
            while cells_placed < population and spiral_radius < 50:
                # Try to place blocks in a ring at this radius
                for angle in range(0, 360, 30):  # 12 positions per ring
                    if cells_placed >= population:
                        break
                    
                    # Calculate position
                    dx = int(spiral_radius * math.cos(math.radians(angle)))
                    dy = int(spiral_radius * math.sin(math.radians(angle)))
                    bx, by = cx + dx, cy + dy
                    
                    # Try to place a 2x2 block here
                    can_place = True
                    for bdy in range(2):
                        for bdx in range(2):
                            x, y = bx + bdx, by + bdy
                            if not (0 <= x < self.width and 0 <= y < self.height):
                                can_place = False
                                break
                            if self.cells[y][x] is not None:
                                can_place = False
                                break
                            zone = self.zone_manager.get_zone_at(x, y)
                            if not zone.properties.can_enter:
                                can_place = False
                                break
                        if not can_place:
                            break
                    
                    # Place the block
                    if can_place:
                        for bdy in range(2):
                            for bdx in range(2):
                                x, y = bx + bdx, by + bdy
                                self.cells[y][x] = Cell(x, y, species)
                                cells_placed += 1
                                
                                # Track zone placement
                                zone = self.zone_manager.get_zone_at(x, y)
                                zone_name = zone.properties.name.lower().split()[0]
                                zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1
                                
                                if cells_placed >= population:
                                    break
                            if cells_placed >= population:
                                break
                
                spiral_radius += 4  # Move to next ring
            
            # Fallback: If we couldn't place enough blocks, scatter remaining randomly near center
            if cells_placed < population:
                fallback_attempts = 0
                while cells_placed < population and fallback_attempts < population * 50:
                    # Scatter within a larger radius
                    radius = 50
                    angle = random.random() * 2 * math.pi
                    dist = random.random() * radius
                    x = int(cx + dist * math.cos(angle))
                    y = int(cy + dist * math.sin(angle))
                    
                    if 0 <= x < self.width and 0 <= y < self.height:
                        if self.cells[y][x] is None:
                            zone = self.zone_manager.get_zone_at(x, y)
                            if zone.properties.can_enter:
                                self.cells[y][x] = Cell(x, y, species)
                                cells_placed += 1
                                
                                # Track zone placement
                                zone_name = zone.properties.name.lower().split()[0]
                                zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1
                    
                    fallback_attempts += 1
        
        elif pattern == "edge":
            # Place around perimeter
            positions = []
            for x in range(self.width):
                positions.append((x, 0))
                positions.append((x, self.height - 1))
            for y in range(1, self.height - 1):
                positions.append((0, y))
                positions.append((self.width - 1, y))
            
            random.shuffle(positions)
            for x, y in positions[:population]:
                if self.cells[y][x] is None:
                    zone = self.zone_manager.get_zone_at(x, y)
                    if zone.properties.can_enter:
                        self.cells[y][x] = Cell(x, y, species)
                        cells_placed += 1
                        
                        # Track zone placement
                        zone_name = zone.properties.name.lower().split()[0]
                        zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1
        
        # Phase 3: Set native zone based on where species was seeded most
        if zone_counts:
            most_common_zone = max(zone_counts, key=zone_counts.get)
            species.traits.native_zone_type = most_common_zone
            print(f"  {species.name} established in {most_common_zone} zone ({zone_counts[most_common_zone]}/{cells_placed} cells)")
        
        print(f"Seeded {cells_placed} cells of {species.name}")
    
    def get_neighbors(self, x: int, y: int, radius: int = 1) -> List[Tuple[int, int]]:
        """Get valid neighbor coordinates within specified radius"""
        neighbors = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                
                if self.wrap:
                    nx = nx % self.width
                    ny = ny % self.height
                else:
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue
                
                neighbors.append((nx, ny))
        
        return neighbors
    
    def _build_neighbor_cache(self):
        """Build cached neighbor counts using Numba (called once per generation)"""
        # Create numpy boolean array of alive cells
        alive_grid = np.zeros((self.height, self.width), dtype=np.bool_)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                alive_grid[y, x] = (cell is not None and cell.is_alive)
        
        # Use Numba to count all neighbors at once
        self._neighbor_cache = count_all_neighbors(alive_grid, self.wrap)
        self._neighbor_cache_generation = self.generation
    
    def _build_zone_caches(self):
        """Build zone and pressure caches (called once per generation)"""
        if self._zone_cache_generation == self.generation:
            return  # Already cached
        
        self._zone_cache.clear()
        self._zone_pressure_cache.clear()
        
        # Cache zone lookup for every position
        for y in range(self.height):
            for x in range(self.width):
                zone = self.zone_manager.get_zone_at(x, y)
                self._zone_cache[(x, y)] = zone
        
        # Cache population pressure for each unique zone
        for zone in self.zone_manager.get_all_zones():
            self._zone_pressure_cache[zone] = zone.get_population_pressure()
        self._zone_pressure_cache[self.zone_manager.default_zone] = self.zone_manager.default_zone.get_population_pressure()
        
        self._zone_cache_generation = self.generation
    
    def _get_cached_zone(self, x: int, y: int) -> Zone:
        """Get zone from cache (must call _build_zone_caches first)"""
        return self._zone_cache.get((x, y), self.zone_manager.default_zone)
    
    def _get_cached_pressure(self, zone: Zone) -> float:
        """Get population pressure from cache"""
        return self._zone_pressure_cache.get(zone, 1.0)
    
    def count_living_neighbors(self, x: int, y: int) -> int:
        """Count how many living neighbors a position has"""
        # Use cached neighbor counts if available
        if self._neighbor_cache is not None and self._neighbor_cache_generation == self.generation:
            return int(self._neighbor_cache[y, x])
        
        # Fallback to manual counting (shouldn't happen after optimization)
        t0 = time.perf_counter()
        count = 0
        for nx, ny in self.get_neighbors(x, y):
            if self.cells[ny][nx] and self.cells[ny][nx].is_alive:
                count += 1
        self.timing_stats['neighbor_counting'] += time.perf_counter() - t0
        return count
    
    def step(self):
        """Execute one generation of the simulation"""
        step_start = time.perf_counter()
        self.generation += 1
        
        # Dynamic zone shifts every 50 generations
        if self.generation % 50 == 0:
            self.zone_manager.shift_zones()
            print(f"Gen {self.generation}: Zones shifted!")
        
        # Migration pressure event every 150 generations (less frequent)
        migration_pressure = 0.0
        if self.generation % 150 == 0:
            migration_pressure = 0.3  # 30% of organisms feel urge (was 50%)
            print(f"Gen {self.generation}: Migration pressure event!")
        
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
        
        # Phase 0: Environmental changes
        self.zone_manager.step()
        
        # Phase 1: Age all cells and handle energy decay
        t0 = time.perf_counter()
        self.process_aging()
        self.timing_stats['aging'] = time.perf_counter() - t0
        
        # Phase 2: Process movement (optional)
        t0 = time.perf_counter()
        self.process_movement(migration_pressure=migration_pressure)
        self.timing_stats['movement'] = time.perf_counter() - t0
        
        # Phase 3: Predator hunting (if predators exist)
        t0 = time.perf_counter()
        self.process_predation()
        self.timing_stats['predation'] = time.perf_counter() - t0
        
        # Phase 4: Process births and deaths (Conway-style with energy constraints)
        t0 = time.perf_counter()
        self.process_reproduction()
        self.timing_stats['reproduction'] = time.perf_counter() - t0
        
        # Phase 5: Update species populations
        self.species_registry.update_populations(self)
        
        self.timing_stats['total_step'] = time.perf_counter() - step_start
        
        # Print performance stats every 10 generations
        if self.generation % 10 == 0:
            self._print_timing_stats()
        
        return self.generation
    
    def process_aging(self):
        """Age all cells and handle energy decay"""
        # Build zone caches once (OPTIMIZATION)
        self._build_zone_caches()
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    species = self.species_registry.get(cell.species_id)
                    zone = self._get_cached_zone(x, y)  # CACHED
                    
                    # Apply zone modifiers
                    energy_mult = zone.properties.energy_decay_mult
                    zone_name = zone.properties.name.lower().split()[0]  # Extract type from name
                    
                    # Check for nearby prey (for predators/hybrid feeders)
                    has_prey = self._has_prey_nearby(x, y, species)
                    
                    # Get population pressure from carrying capacity (Phase 4) - CACHED
                    population_pressure = self._get_cached_pressure(zone)
                    
                    # Apply colonial clustering bonus (same-species neighbors)
                    colony_bonus = self._get_colony_bonus(x, y, cell.species_id, species)
                    energy_mult *= colony_bonus
                    
                    if not cell.age_one_generation(species, energy_mult, zone_name, has_prey, population_pressure):
                        # Cell died (starvation or old age)
                        self.deaths_this_gen += 1
                        species.total_deaths += 1
                        cell.is_alive = False
    
    def _has_prey_nearby(self, x: int, y: int, species) -> bool:
        """Check if there are consumable cells nearby"""
        if species.traits.energy_source == "photosynthesis":
            return False  # Doesn't need prey
        
        for nx, ny in self.get_neighbors(x, y):
            neighbor = self.cells[ny][nx]
            if neighbor and neighbor.is_alive:
                neighbor_species = self.species_registry.get(neighbor.species_id)
                if (neighbor_species and 
                    neighbor_species.traits.can_be_consumed and
                    neighbor.species_id != species.id):
                    return True
        return False
    
    def _has_predators_nearby(self, x: int, y: int, species) -> bool:
        """Check if there are predators nearby (complexity 3+ organisms)"""
        for nx, ny in self.get_neighbors(x, y):
            neighbor = self.cells[ny][nx]
            if neighbor and neighbor.is_alive:
                neighbor_species = self.species_registry.get(neighbor.species_id)
                if neighbor_species and neighbor_species.traits.can_hunt():
                    return True
        return False
    
    def _get_colony_bonus(self, x: int, y: int, species_id: int, species) -> float:
        """Calculate colonial clustering bonus (same-species neighbors)"""
        same_species_count = 0
        total_neighbors = 0
        
        for nx, ny in self.get_neighbors(x, y):
            neighbor = self.cells[ny][nx]
            if neighbor and neighbor.is_alive:
                total_neighbors += 1
                if neighbor.species_id == species_id:
                    same_species_count += 1
        
        if total_neighbors == 0:
            return 1.0  # No colony effect when isolated
        
        # Colony bonus scales with percentage of same-species neighbors
        colony_ratio = same_species_count / total_neighbors
        # Bonus = 1.0 (no neighbors) to colonial_affinity (all same species)
        return 1.0 + (colony_ratio * (species.traits.colonial_affinity - 1.0))
    
    def _get_cluster_reproduction_bonus(self, x: int, y: int, species_id: int, species) -> float:
        """Calculate reproduction bonus when surrounded by same-species colony"""
        same_species_count = 0
        
        for nx, ny in self.get_neighbors(x, y):
            neighbor = self.cells[ny][nx]
            if neighbor and neighbor.is_alive and neighbor.species_id == species_id:
                same_species_count += 1
        
        # Bonus scales with cluster size (3 same-species neighbors = full bonus)
        cluster_ratio = min(1.0, same_species_count / 3.0)
        # Bonus = 1.0 (no cluster) to cluster_reproduction_bonus (full cluster)
        return 1.0 + (cluster_ratio * (species.traits.cluster_reproduction_bonus - 1.0))
    
    def process_movement(self, migration_pressure: float = 0.0):
        """Cells only move when necessary - to find food or escape danger
        migration_pressure: 0.0-1.0, external pressure to migrate"""
        # Build zone caches for movement checks (OPTIMIZATION)
        self._build_zone_caches()
        
        # Collect all cells that CAN move (have energy)
        mobile_cells = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    species = self.species_registry.get(cell.species_id)
                    if cell.can_move(species):
                        mobile_cells.append((x, y, cell))
        
        # Process movements - only when strategically necessary
        for old_x, old_y, cell in mobile_cells:
            species = self.species_registry.get(cell.species_id)
            strategy = species.traits.get_movement_strategy()
            should_move = False
            
            # Migration pressure event overrides some logic
            if migration_pressure > 0 and random.random() < migration_pressure:
                should_move = True
            
            # FOOD-DRIVEN MOVEMENT LOGIC (if not already decided to move)
            if not should_move:
                if strategy == "hunt":
                    # Predators ALWAYS move to find prey (aggressive hunting)
                    # They must hunt to survive (can't photosynthesize)
                    has_prey = self._has_prey_nearby(old_x, old_y, species)
                    if not has_prey or cell.energy < species.traits.reproduction_threshold * 1.2:
                        should_move = True
                    # Even with prey nearby, 30% chance to hunt more aggressively
                    elif random.random() < 0.3:
                        should_move = True
                        
                elif strategy == "flee":
                    # Flee from predators (survival instinct)
                    if self._has_predators_nearby(old_x, old_y, species):
                        should_move = True
                    # Also move if zone quality is poor and energy is low
                    elif cell.energy < species.traits.reproduction_threshold * 0.7:
                        current_zone = self._get_cached_zone(old_x, old_y)  # CACHED
                        if current_zone.properties.energy_generation_mult < 1.0:
                            should_move = True
                            
                else:  # "energy_seeking" (photosynthesizers)
                    # Photosynthesizers explore to find better zones
                    current_zone = self._get_cached_zone(old_x, old_y)  # CACHED
                    current_quality = current_zone.properties.energy_generation_mult
                    population_pressure = self._get_cached_pressure(current_zone)  # CACHED
                    
                    # Move if population pressure is getting bad
                    if population_pressure < 0.8:  # Start moving at 80% pressure (was 60%)
                        should_move = True
                    # Move if zone is poor
                    elif current_quality < 1.0:  # Any non-ideal zone triggers exploration
                        should_move = True
                    elif cell.energy > species.traits.reproduction_threshold * 1.2:  # High energy = explore
                        # Well-fed organisms explore for new territories
                        if random.random() < 0.35:  # 35% chance to explore when healthy
                            should_move = True
                    elif cell.energy < species.traits.reproduction_threshold * 0.85:
                        # Low energy - seek better zones
                        should_move = True
            
            if not should_move:
                continue  # Stay put - conserve energy
            
            # Extended range for migration when desperate or exploring
            movement_range = 1  # Default adjacent
            if cell.energy < species.traits.reproduction_threshold * 0.5:
                # Desperate - try long-distance migration (range 2)
                movement_range = 2
            elif cell.energy > species.traits.reproduction_threshold * 1.5:
                # Abundant energy - explore farther (range 2)
                movement_range = 2
            
            neighbors = self.get_neighbors(old_x, old_y, radius=movement_range)
            
            # Filter for valid spots (can be empty OR occupied by weaker organisms)
            valid_spots = []
            for nx, ny in neighbors:
                zone = self._get_cached_zone(nx, ny)  # CACHED
                if not zone.properties.can_enter:
                    continue
                    
                target_cell = self.cells[ny][nx]
                if target_cell is None:
                    # Empty space - always valid
                    valid_spots.append((nx, ny))
                elif target_cell.is_alive:
                    # Occupied - can displace if we have more energy (competition)
                    if cell.energy > target_cell.energy * 1.1:  # Only need 10% more energy (was 20%)
                        valid_spots.append((nx, ny))
            
            if not valid_spots:
                continue
            
            # Choose destination based on complexity-driven strategy
            strategy = species.traits.get_movement_strategy()
            target_x, target_y = None, None
            
            if strategy == "energy_seeking":
                target_x, target_y = self._move_energy_seeking(old_x, old_y, valid_spots)
            elif strategy == "flee":
                target_x, target_y = self._move_flee(old_x, old_y, valid_spots, species)
            elif strategy == "hunt":
                target_x, target_y = self._move_hunt(old_x, old_y, valid_spots, species)
            else:
                target_x, target_y = random.choice(valid_spots)
            
            # Execute movement
            if target_x is not None and cell.move_to(target_x, target_y, species):
                # Check if target is occupied - displacement
                target_cell = self.cells[target_y][target_x]
                if target_cell and target_cell.is_alive:
                    # Displace the weaker organism (it dies or moves)
                    target_cell.is_alive = False
                    self.deaths_this_gen += 1
                
                # Update grid
                self.cells[old_y][old_x] = None
                self.cells[target_y][target_x] = cell
        
        # Reset movement flags
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    cell.reset_movement()
    
    def _move_energy_seeking(self, x: int, y: int, valid_spots: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Move toward zones with better energy generation"""
        current_zone = self._get_cached_zone(x, y)  # CACHED
        current_energy_mult = current_zone.properties.energy_generation_mult
        
        # Score each spot by energy potential
        best_spot = None
        best_score = current_energy_mult
        
        for nx, ny in valid_spots:
            zone = self._get_cached_zone(nx, ny)  # CACHED
            score = zone.properties.energy_generation_mult - zone.properties.energy_decay_mult
            
            if score > best_score:
                best_score = score
                best_spot = (nx, ny)
        
        # If no better spot, move randomly
        return best_spot if best_spot else random.choice(valid_spots)
    
    def _move_flee(self, x: int, y: int, valid_spots: List[Tuple[int, int]], species: Species) -> Tuple[int, int]:
        """Move away from predators (complexity 3+ organisms)"""
        # Find predators in neighborhood
        predators_nearby = []
        for nx, ny in self.get_neighbors(x, y):
            neighbor = self.cells[ny][nx]
            if neighbor and neighbor.is_alive:
                neighbor_species = self.species_registry.get(neighbor.species_id)
                # Flee from organisms that can hunt (complexity 3+)
                if neighbor_species.traits.can_hunt():
                    predators_nearby.append((nx, ny))
        
        if not predators_nearby:
            # No threat, move toward energy
            return self._move_energy_seeking(x, y, valid_spots)
        
        # Move to spot farthest from predators
        best_spot = None
        best_distance = -1
        
        for nx, ny in valid_spots:
            min_dist = min(abs(nx - px) + abs(ny - py) for px, py in predators_nearby)
            if min_dist > best_distance:
                best_distance = min_dist
                best_spot = (nx, ny)
        
        return best_spot if best_spot else random.choice(valid_spots)
    
    def _move_hunt(self, x: int, y: int, valid_spots: List[Tuple[int, int]], species: Species) -> Tuple[int, int]:
        """Move toward prey"""
        # Find prey in extended neighborhood
        prey_nearby = []
        for nx, ny in self.get_neighbors(x, y):
            neighbor = self.cells[ny][nx]
            if neighbor and neighbor.is_alive:
                neighbor_species = self.species_registry.get(neighbor.species_id)
                # Hunt organisms that can be consumed and aren't hunters themselves
                if neighbor_species.traits.can_be_consumed and not neighbor_species.traits.can_hunt():
                    prey_nearby.append((nx, ny))
        
        if not prey_nearby:
            # No prey, move toward energy
            return self._move_energy_seeking(x, y, valid_spots)
        
        # Move to spot closest to prey
        best_spot = None
        best_distance = float('inf')
        
        for nx, ny in valid_spots:
            min_dist = min(abs(nx - px) + abs(ny - py) for px, py in prey_nearby)
            if min_dist < best_distance:
                best_distance = min_dist
                best_spot = (nx, ny)
        
        return best_spot if best_spot else random.choice(valid_spots)
    
    def process_predation(self):
        """Handle predation (only for complexity 3+ organisms)"""
        predation_events = []  # (predator_cell, prey_x, prey_y)
        
        # Find all complex organisms that can hunt
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    species = self.species_registry.get(cell.species_id)
                    
                    # Only complex organisms (complexity 3+) can hunt
                    if species.traits.can_hunt():
                        # Look for prey in adjacent cells
                        prey_neighbors = []
                        for nx, ny in self.get_neighbors(x, y):
                            neighbor = self.cells[ny][nx]
                            if neighbor and neighbor.is_alive:
                                neighbor_species = self.species_registry.get(neighbor.species_id)
                                # Can't eat same species or other hunters
                                if (neighbor_species.traits.can_be_consumed and 
                                    neighbor.species_id != cell.species_id):
                                    prey_neighbors.append((neighbor, nx, ny))
                        
                        # Attack one prey if available
                        if prey_neighbors:
                            prey_cell, px, py = random.choice(prey_neighbors)
                            predation_events.append((cell, species, prey_cell, px, py))
        
        # Process predation events
        for predator_cell, predator_species, prey_cell, px, py in predation_events:
            if prey_cell.is_alive:  # Check if prey still alive
                prey_species = self.species_registry.get(prey_cell.species_id)
                
                # Use complexity-based hunting efficiency
                actual_efficiency = predator_species.traits.get_hunting_efficiency()
                energy_gained = int(prey_cell.energy * actual_efficiency)
                predator_cell.energy = min(predator_cell.max_energy, predator_cell.energy + energy_gained)
                
                # Kill prey
                prey_cell.is_alive = False
                
                # Remove from grid
                self.cells[py][px] = None
                self.deaths_this_gen += 1
                prey_species.total_deaths += 1
    
    def process_reproduction(self):
        """Handle births and deaths based on Conway rules + energy"""
        # Build neighbor cache once for this generation (NUMBA OPTIMIZATION)
        self._build_neighbor_cache()
        # Build zone caches (OPTIMIZATION)
        self._build_zone_caches()
        
        # We need to process births/deaths simultaneously
        birth_queue = []  # (x, y, species_id, energy)
        death_queue = []  # (x, y)
        
        # Check all positions
        for y in range(self.height):
            for x in range(self.width):
                neighbors_count = self.count_living_neighbors(x, y)
                current_cell = self.cells[y][x]
                
                if current_cell and current_cell.is_alive:
                    # Living cell: ENERGY-DEPENDENT CONWAY RULES (Phase 3+4)
                    # High energy cells: Standard Conway (2-3 neighbors survive)
                    # Low energy cells: Need MORE neighbors (3-4) to survive
                    # This makes stable patterns collapse when energy depletes
                    species = self.species_registry.get(current_cell.species_id)
                    energy_ratio = current_cell.energy / current_cell.max_energy
                    
                    # Calculate neighbor requirements based on energy
                    if energy_ratio > 0.7:
                        # High energy: Standard Conway (2-3 neighbors)
                        min_neighbors, max_neighbors = 2, 3
                    elif energy_ratio > 0.4:
                        # Medium energy: Slightly harder (2-3 neighbors, but 4 is risky)
                        min_neighbors, max_neighbors = 2, 3
                        # Add small chance of death at 4 neighbors when weakened
                        if neighbors_count == 4 and random.random() < 0.3:
                            death_queue.append((x, y))
                            continue
                    else:
                        # Low energy: Need 3-4 neighbors (2 is too lonely, 5+ too crowded)
                        min_neighbors, max_neighbors = 3, 4
                    
                    # Apply rules with geometry-breaking perturbation
                    if neighbors_count < min_neighbors or neighbors_count > max_neighbors:
                        death_queue.append((x, y))
                    elif neighbors_count == max_neighbors and current_cell.age > 50:
                        # Older cells at max neighbors: small random death chance
                        # Breaks perfect geometric stability over time
                        if random.random() < 0.02:  # 2% chance
                            death_queue.append((x, y))
                    # else: survives
                
                else:
                    # Empty or dead cell: check for birth
                    # RELAXED CONWAY: 2-4 neighbors can trigger birth (not just 3)
                    # This allows reproduction in more configurations
                    if 2 <= neighbors_count <= 4:
                        # Determine parent species (from neighbors)
                        neighbor_cells = []
                        for nx, ny in self.get_neighbors(x, y):
                            ncell = self.cells[ny][nx]
                            if ncell and ncell.is_alive:
                                neighbor_cells.append(ncell)
                        
                        if len(neighbor_cells) >= 2:  # At least 2 neighbors needed
                            # Check if sexual reproduction is required
                            parent_cell = random.choice(neighbor_cells)
                            parent_species = self.species_registry.get(parent_cell.species_id)
                            
                            # Sexual reproduction: need two parents of same species
                            second_parent = None
                            if parent_species.traits.sexual_reproduction and len(neighbor_cells) >= 2:
                                # Find another parent of same species
                                same_species_neighbors = [nc for nc in neighbor_cells 
                                                         if nc.species_id == parent_species.id and nc != parent_cell]
                                if same_species_neighbors:
                                    second_parent = random.choice(same_species_neighbors)
                                else:
                                    # Can't reproduce without second parent
                                    continue
                            
                            zone = self._get_cached_zone(x, y)  # CACHED
                            if zone.properties.can_enter:
                                # Check population pressure (Phase 4: Carrying Capacity) - CACHED
                                population_pressure = self._get_cached_pressure(zone)
                                
                                # Reproduction is moderately harder in overcrowded zones
                                # Only significantly blocked in extreme overcrowding (> 150% capacity)
                                reproduction_difficulty = max(1.0, 1.0 / max(0.8, population_pressure))
                                
                                # PHASE 3: Native zone bonus
                                # Species reproduce better in their native habitat
                                zone_type_name = zone.properties.name.lower().split()[0]  # Extract "fertile", "desert", etc.
                                native_zone_bonus = 1.0
                                if zone_type_name == parent_species.traits.native_zone_type:
                                    # In native zone: lower threshold, easier reproduction
                                    native_zone_bonus = parent_species.traits.native_zone_affinity
                                
                                # Colonial clustering bonus: Cells in same-species clusters reproduce better
                                cluster_bonus = self._get_cluster_reproduction_bonus(x, y, parent_species.id, parent_species)
                                
                                # Birth probability depends on neighbor count
                                # 3 neighbors: 100% chance (classic Conway)
                                # 2 or 4 neighbors: 50% chance (relaxed rule)
                                birth_probability = 1.0 if neighbors_count == 3 else 0.5
                                if random.random() > birth_probability:
                                    continue  # Birth doesn't happen this time
                                
                                # Birth happens if parent has enough energy
                                # Energy from parent(s) if they can afford it
                                effective_threshold = parent_species.traits.reproduction_threshold * reproduction_difficulty / (native_zone_bonus * cluster_bonus)
                                
                                if parent_cell.can_reproduce(parent_species) and parent_cell.energy >= effective_threshold:
                                    offspring_energy = parent_cell.consume_reproduction_energy(parent_species)
                                    
                                    # Second parent contributes if sexual
                                    if second_parent and second_parent.can_reproduce(parent_species):
                                        offspring_energy += second_parent.consume_reproduction_energy(parent_species) // 2
                                else:
                                    # In severely overcrowded zones (< 0.6x pressure), block weak reproduction
                                    if population_pressure < 0.6:
                                        continue  # Skip birth if zone is extremely crowded and parents are weak
                                    # Otherwise birth can still happen with minimal energy
                                    offspring_energy = parent_species.traits.base_energy // 3
                                
                                # Mutation check (sexual reproduction reduces mutation chance)
                                mutation_mult = 0.5 if second_parent else 1.0
                                effective_mutation_rate = (parent_species.traits.mutation_rate * 
                                                         zone.properties.mutation_rate_mult * mutation_mult)
                                
                                if random.random() < effective_mutation_rate:
                                    # Mutate
                                    mutant_species = parent_species.mutate(self.generation)
                                    self.species_registry.register(mutant_species)
                                    birth_queue.append((x, y, mutant_species.id, offspring_energy))
                                    self.mutations_this_gen += 1
                                else:
                                    # Normal birth
                                    birth_queue.append((x, y, parent_species.id, offspring_energy))
        
        # Apply deaths
        for x, y in death_queue:
            cell = self.cells[y][x]
            if cell:
                species = self.species_registry.get(cell.species_id)
                if species:
                    species.total_deaths += 1
                cell.is_alive = False
                self.cells[y][x] = None
                self.deaths_this_gen += 1
        
        # Apply births
        for x, y, species_id, energy in birth_queue:
            species = self.species_registry.get(species_id)
            if species:
                self.cells[y][x] = Cell(x, y, species, energy)
                species.total_births += 1
                self.births_this_gen += 1
    
    def _print_timing_stats(self):
        """Print performance timing breakdown"""
        stats = self.timing_stats
        total = stats['total_step'] * 1000  # Convert to ms
        
        if total < 1:
            return  # Skip if too fast
        
        print(f"\nPerformance (Gen {self.generation}):")
        print(f"  Total:        {total:.1f}ms")
        print(f"  Aging:        {stats['aging']*1000:.1f}ms ({stats['aging']/stats['total_step']*100:.0f}%)")
        print(f"  Movement:     {stats['movement']*1000:.1f}ms ({stats['movement']/stats['total_step']*100:.0f}%)")
        print(f"  Predation:    {stats['predation']*1000:.1f}ms ({stats['predation']/stats['total_step']*100:.0f}%)")
        print(f"  Reproduction: {stats['reproduction']*1000:.1f}ms ({stats['reproduction']/stats['total_step']*100:.0f}%)")
        print(f"  Neighbor Cnt: {stats['neighbor_counting']*1000:.1f}ms ({stats['neighbor_counting']/stats['total_step']*100:.0f}%)")
        
        # Reset neighbor counting for next cycle
        stats['neighbor_counting'] = 0.0
    
    def get_stats(self):
        """Get current simulation statistics"""
        living_cells = sum(1 for row in self.cells for cell in row if cell and cell.is_alive)
        species_stats = self.species_registry.get_stats()
        
        avg_species_age = 0
        if species_stats['total_species'] > 0:
            ages = [self.generation - s.generation_born 
                   for s in self.species_registry.get_living_species()]
            avg_species_age = sum(ages) / len(ages) if ages else 0
        
        return {
            'generation': self.generation,
            'population': living_cells,
            'species_count': species_stats['total_species'],
            'births': self.births_this_gen,
            'deaths': self.deaths_this_gen,
            'mutations': self.mutations_this_gen,
            'avg_species_age': avg_species_age,
            'dominant_species': species_stats['most_populous']
        }
