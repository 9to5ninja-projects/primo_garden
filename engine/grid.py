"""
Cellular Automata Grid Engine
Handles the core simulation grid and life/death rules
"""

import numpy as np
from .species import Species


class World:
    def __init__(self, width, height, rules, initial_density=0.15):
        self.width = width
        self.height = height
        self.rules = rules
        self.generation = 0
        
        # Main grids
        self.grid = np.zeros((height, width), dtype=np.int32)  # Species IDs
        self.energy_grid = np.ones((height, width), dtype=np.float32)  # Energy per cell
        
        # Species tracking
        self.species_registry = {}  # id -> Species object
        self.next_species_id = 1
        
        # Stats
        self.total_population = 0
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
        
        # Initialize with random life
        self.reset(initial_density)
    
    def reset(self, density):
        """Reset world with new random initial conditions"""
        self.generation = 0
        self.grid = np.zeros((self.height, self.width), dtype=np.int32)
        self.energy_grid = np.ones((self.height, self.width), dtype=np.float32)
        self.species_registry = {}
        self.next_species_id = 1
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
        
        # Seed initial life
        random_cells = np.random.random((self.height, self.width)) < density
        
        # Create initial species
        initial_species = self._create_species(parent_id=None)
        self.grid[random_cells] = initial_species.id
        
        self._update_stats()
    
    def step(self):
        """Execute one generation of the simulation"""
        # Reset per-generation stats
        old_population = self.total_population
        self.births_this_gen = 0
        self.deaths_this_gen = 0
        self.mutations_this_gen = 0
        
        new_grid = np.zeros_like(self.grid)
        
        # Count neighbors for each cell
        neighbors = self._count_neighbors()
        
        # Apply rules
        for y in range(self.height):
            for x in range(self.width):
                alive = self.grid[y, x] > 0
                neighbor_count = neighbors[y, x]
                
                # Survival rules
                if alive:
                    species_id = self.grid[y, x]
                    if self._survives(species_id, neighbor_count):
                        # Survive - keep same species ID (no mutation on survival)
                        new_grid[y, x] = species_id
                    else:
                        # Dies
                        self.deaths_this_gen += 1
                
                # Birth rules
                elif self._births(neighbor_count):
                    # New cell born - inherit from random neighbor
                    parent_id = self._get_random_neighbor_species(x, y)
                    if parent_id is not None:
                        self.births_this_gen += 1
                        
                        # Chance to mutate during reproduction
                        if np.random.random() < self.rules.mutation_rate:
                            new_species = self._create_species(parent_id=parent_id)
                            new_grid[y, x] = new_species.id
                            self.mutations_this_gen += 1
                        else:
                            # Inherit parent species directly
                            new_grid[y, x] = parent_id
        
        self.grid = new_grid
        self.generation += 1
        
        # Clean up extinct species
        self._cleanup_extinct()
        self._update_stats()
    
    def _count_neighbors(self):
        """Count living neighbors for each cell (Moore neighborhood)"""
        neighbors = np.zeros((self.height, self.width), dtype=np.int32)
        
        # All 8 directions
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                # Roll grid to check neighbors (wraps at edges)
                shifted = np.roll(np.roll(self.grid, dy, axis=0), dx, axis=1)
                neighbors += (shifted > 0).astype(np.int32)
        
        return neighbors
    
    def _survives(self, species_id, neighbor_count):
        """Check if cell survives based on rules"""
        min_neighbors, max_neighbors = self.rules.survival_range
        return min_neighbors <= neighbor_count <= max_neighbors
    
    def _births(self, neighbor_count):
        """Check if new cell is born based on rules"""
        min_neighbors, max_neighbors = self.rules.birth_range
        return min_neighbors <= neighbor_count <= max_neighbors
    
    def _get_random_neighbor_species(self, x, y):
        """Get species ID from a random living neighbor"""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                
                if self.grid[ny, nx] > 0:
                    neighbors.append(self.grid[ny, nx])
        
        if neighbors:
            return np.random.choice(neighbors)
        return None
    
    def _create_species(self, parent_id=None):
        """Create new species, optionally mutated from parent"""
        species_id = self.next_species_id
        self.next_species_id += 1
        
        species = Species(species_id, parent_id, self.generation)
        
        # If has parent, inherit and mutate traits
        if parent_id is not None and parent_id in self.species_registry:
            parent = self.species_registry[parent_id]
            species.inherit_from(parent, mutation_strength=0.1)
        
        self.species_registry[species_id] = species
        return species
    
    def _cleanup_extinct(self):
        """Remove species with no living members"""
        alive_species = set(self.grid[self.grid > 0])
        extinct = [sid for sid in self.species_registry.keys() if sid not in alive_species]
        
        for sid in extinct:
            del self.species_registry[sid]
    
    def _update_stats(self):
        """Update population statistics"""
        self.total_population = np.sum(self.grid > 0)
        
        # Update per-species populations
        for species_id in self.species_registry:
            self.species_registry[species_id].population = np.sum(self.grid == species_id)
    
    def get_average_species_age(self):
        """Calculate average age of currently living species"""
        if not self.species_registry:
            return 0
        total_age = sum(self.generation - s.birth_generation for s in self.species_registry.values())
        return total_age / len(self.species_registry)
