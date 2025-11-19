"""
Enhanced Grid system for Primordial Garden 2.0
Integrates energy, zones, mobility, and complex species interactions
"""
from typing import List, Tuple, Optional
from .cell import Cell
from .species_enhanced import Species, SpeciesRegistry
from .zones import Zone, ZoneManager, ZoneType, ZoneProperties
import random


class Grid:
    """Main simulation grid with energy and zone support"""
    
    def __init__(self, width: int, height: int, wrap: bool = True):
        self.width = width
        self.height = height
        self.wrap = wrap
        
        # Grid structure
        self.cells = [[None for _ in range(width)] for _ in range(height)]
        
        # Species management
        self.species_registry = SpeciesRegistry()
        
        # Zone management
        self.zone_manager = ZoneManager(width, height)
        
        # Statistics
        self.generation = 0
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
    
    def setup_zones(self, zone_layout: str = "random"):
        """Initialize environmental zones"""
        if zone_layout == "random":
            self.zone_manager.create_random_zones(num_zones=random.randint(3, 7))
        elif zone_layout == "quadrant":
            self.zone_manager.create_quadrant_zones()
        elif zone_layout == "ring":
            self.zone_manager.create_ring_world()
        # "neutral" = do nothing, entire grid stays neutral
    
    def seed_species(self, species: Species, population: int, pattern: str = "random"):
        """Add initial population of a species to the grid"""
        self.species_registry.register(species)
        
        cells_placed = 0
        attempts = 0
        max_attempts = population * 10
        
        if pattern == "random":
            while cells_placed < population and attempts < max_attempts:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                
                if self.cells[y][x] is None:
                    zone = self.zone_manager.get_zone_at(x, y)
                    if zone.properties.can_enter:
                        self.cells[y][x] = Cell(x, y, species)
                        cells_placed += 1
                
                attempts += 1
        
        elif pattern == "center":
            cx, cy = self.width // 2, self.height // 2
            radius = int((population / 3.14159) ** 0.5)
            
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if cells_placed >= population:
                        break
                    if dx*dx + dy*dy <= radius*radius:
                        x, y = cx + dx, cy + dy
                        if 0 <= x < self.width and 0 <= y < self.height:
                            if self.cells[y][x] is None:
                                zone = self.zone_manager.get_zone_at(x, y)
                                if zone.properties.can_enter:
                                    self.cells[y][x] = Cell(x, y, species)
                                    cells_placed += 1
        
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
        
        print(f"Seeded {cells_placed} cells of {species.name}")
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighbor coordinates (8-way)"""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
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
    
    def count_living_neighbors(self, x: int, y: int) -> int:
        """Count how many living neighbors a position has"""
        count = 0
        for nx, ny in self.get_neighbors(x, y):
            if self.cells[ny][nx] and self.cells[ny][nx].is_alive:
                count += 1
        return count
    
    def step(self):
        """Execute one generation of the simulation"""
        self.generation += 1
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
        
        # Phase 1: Age all cells and handle energy decay
        self.process_aging()
        
        # Phase 2: Process movement (optional)
        self.process_movement()
        
        # Phase 3: Process births and deaths (Conway-style with energy constraints)
        self.process_reproduction()
        
        # Phase 4: Update species populations
        self.species_registry.update_populations(self)
        
        return self.generation
    
    def process_aging(self):
        """Age all cells and handle energy decay"""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    species = self.species_registry.get(cell.species_id)
                    zone = self.zone_manager.get_zone_at(x, y)
                    
                    # Apply zone modifiers
                    energy_mult = zone.properties.energy_decay_mult
                    
                    if not cell.age_one_generation(species, energy_mult):
                        # Cell died of starvation
                        self.deaths_this_gen += 1
                        species.total_deaths += 1
                        cell.is_alive = False
    
    def process_movement(self):
        """Allow mobile cells to move (simple random walk for now)"""
        # Collect all mobile cells first to avoid double-processing
        mobile_cells = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    species = self.species_registry.get(cell.species_id)
                    if cell.can_move(species):
                        mobile_cells.append((x, y, cell))
        
        # Process movements
        for old_x, old_y, cell in mobile_cells:
            species = self.species_registry.get(cell.species_id)
            neighbors = self.get_neighbors(old_x, old_y)
            
            # Filter for valid empty spots
            valid_spots = []
            for nx, ny in neighbors:
                zone = self.zone_manager.get_zone_at(nx, ny)
                if zone.properties.can_enter and self.cells[ny][nx] is None:
                    valid_spots.append((nx, ny))
            
            if valid_spots:
                # Simple random movement for now (can be made smarter later)
                new_x, new_y = random.choice(valid_spots)
                
                if cell.move_to(new_x, new_y, species):
                    # Update grid
                    self.cells[old_y][old_x] = None
                    self.cells[new_y][new_x] = cell
        
        # Reset movement flags
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    cell.reset_movement()
    
    def process_reproduction(self):
        """Handle births and deaths based on Conway rules + energy"""
        # We need to process births/deaths simultaneously
        birth_queue = []  # (x, y, species_id, energy)
        death_queue = []  # (x, y)
        
        # Check all positions
        for y in range(self.height):
            for x in range(self.width):
                neighbors_count = self.count_living_neighbors(x, y)
                current_cell = self.cells[y][x]
                
                if current_cell and current_cell.is_alive:
                    # Living cell: check survival (Conway rules)
                    if neighbors_count < 2 or neighbors_count > 3:
                        death_queue.append((x, y))
                    # else: survives
                
                else:
                    # Empty or dead cell: check for birth (Conway rule: exactly 3 neighbors)
                    if neighbors_count == 3:
                        # Determine parent species (from neighbors)
                        neighbor_cells = []
                        for nx, ny in self.get_neighbors(x, y):
                            ncell = self.cells[ny][nx]
                            if ncell and ncell.is_alive:
                                neighbor_cells.append(ncell)
                        
                        if len(neighbor_cells) >= 3:
                            # Pick dominant parent
                            parent_cell = random.choice(neighbor_cells[:3])
                            parent_species = self.species_registry.get(parent_cell.species_id)
                            
                            zone = self.zone_manager.get_zone_at(x, y)
                            if zone.properties.can_enter:
                                # Birth happens if zone allows (Conway rule)
                                # Energy from parent if they can afford it, otherwise minimal
                                if parent_cell.can_reproduce(parent_species):
                                    offspring_energy = parent_cell.consume_reproduction_energy(parent_species)
                                else:
                                    # Birth still happens but with minimal energy
                                    offspring_energy = parent_species.traits.base_energy // 3
                                
                                # Mutation check
                                effective_mutation_rate = (parent_species.traits.mutation_rate * 
                                                         zone.properties.mutation_rate_mult)
                                
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
