"""
Species system for Primordial Garden 2.0
Each species has genetic traits that affect survival, energy, and behavior
"""
from dataclasses import dataclass
from typing import Tuple
import random


@dataclass
class SpeciesTraits:
    """Genetic traits that define a species' behavior and efficiency"""
    
    # Energy traits
    base_energy: int = 100  # Starting energy for new cells
    energy_decay: int = 2   # Energy lost per generation
    energy_from_birth: int = 50  # Energy cost to reproduce
    photosynthesis_rate: int = 3  # Energy gained per generation (base)
    
    # Mobility traits
    can_move: bool = False
    movement_range: int = 1  # How many cells they can move
    movement_cost: int = 5   # Energy cost per move
    
    # Survival traits
    overcrowding_tolerance: int = 3  # Max neighbors before stress
    isolation_tolerance: int = 1  # Min neighbors needed
    
    # Reproduction traits
    reproduction_threshold: int = 60  # Min energy to reproduce
    mutation_rate: float = 0.01  # Chance to mutate on birth
    
    # Visual
    color: Tuple[int, int, int] = (0, 255, 0)  # RGB color
    
    def __post_init__(self):
        """Validate traits are within reasonable bounds"""
        self.base_energy = max(1, min(200, self.base_energy))
        self.energy_decay = max(1, min(10, self.energy_decay))
        self.photosynthesis_rate = max(0, min(20, self.photosynthesis_rate))
        self.mutation_rate = max(0.0, min(1.0, self.mutation_rate))


class Species:
    """Represents a distinct species with unique traits and genome"""
    
    _next_id = 1
    
    def __init__(self, name: str = None, traits: SpeciesTraits = None, parent_id: int = None):
        self.id = Species._next_id
        Species._next_id += 1
        
        self.name = name or f"Species_{self.id}"
        self.traits = traits or SpeciesTraits()
        self.parent_id = parent_id  # For tracking lineage
        
        # Statistics
        self.population = 0
        self.total_births = 0
        self.total_deaths = 0
        self.generation_born = 0
        
    def mutate(self, generation: int) -> 'Species':
        """Create a mutated offspring species"""
        new_traits = SpeciesTraits(
            base_energy=self._mutate_value(self.traits.base_energy, 5),
            energy_decay=self._mutate_value(self.traits.energy_decay, 1),
            energy_from_birth=self._mutate_value(self.traits.energy_from_birth, 5),
            photosynthesis_rate=self._mutate_value(self.traits.photosynthesis_rate, 1),
            can_move=self.traits.can_move if random.random() > 0.1 else not self.traits.can_move,
            movement_range=self._mutate_value(self.traits.movement_range, 1),
            movement_cost=self._mutate_value(self.traits.movement_cost, 2),
            overcrowding_tolerance=self._mutate_value(self.traits.overcrowding_tolerance, 1),
            isolation_tolerance=self._mutate_value(self.traits.isolation_tolerance, 1),
            reproduction_threshold=self._mutate_value(self.traits.reproduction_threshold, 5),
            mutation_rate=self._mutate_value(self.traits.mutation_rate, 0.005, is_float=True),
            color=self._mutate_color(self.traits.color)
        )
        
        mutant = Species(
            name=f"{self.name}_m{generation}",
            traits=new_traits,
            parent_id=self.id
        )
        mutant.generation_born = generation
        return mutant
    
    @staticmethod
    def _mutate_value(value, max_delta, is_float=False):
        """Apply random mutation to a value"""
        if is_float:
            delta = random.uniform(-max_delta, max_delta)
            return max(0.0, min(1.0, value + delta))
        else:
            delta = random.randint(-max_delta, max_delta)
            return max(1, value + delta)
    
    @staticmethod
    def _mutate_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Slightly mutate RGB color"""
        r, g, b = color
        return (
            max(0, min(255, r + random.randint(-30, 30))),
            max(0, min(255, g + random.randint(-30, 30))),
            max(0, min(255, b + random.randint(-30, 30)))
        )
    
    def __repr__(self):
        return f"Species({self.name}, pop={self.population}, id={self.id})"


class SpeciesRegistry:
    """Manages all species in the simulation"""
    
    def __init__(self):
        self.species_by_id = {}
        self.extinct_species = []
        
    def register(self, species: Species) -> Species:
        """Add a species to the registry"""
        self.species_by_id[species.id] = species
        return species
    
    def get(self, species_id: int) -> Species:
        """Get species by ID"""
        return self.species_by_id.get(species_id)
    
    def mark_extinct(self, species_id: int):
        """Move species to extinct list"""
        if species_id in self.species_by_id:
            species = self.species_by_id.pop(species_id)
            self.extinct_species.append(species)
    
    def get_living_species(self):
        """Get all non-extinct species"""
        return list(self.species_by_id.values())
    
    def update_populations(self, grid):
        """Update population counts from grid state"""
        # Reset all populations
        for species in self.species_by_id.values():
            species.population = 0
        
        # Count living cells
        for row in grid.cells:
            for cell in row:
                if cell and cell.is_alive:
                    species = self.get(cell.species_id)
                    if species:
                        species.population += 1
        
        # Mark extinct species
        extinct_ids = [sid for sid, species in self.species_by_id.items() 
                       if species.population == 0]
        for sid in extinct_ids:
            self.mark_extinct(sid)
    
    def get_stats(self):
        """Get current species statistics"""
        living = self.get_living_species()
        return {
            'total_species': len(living),
            'extinct_species': len(self.extinct_species),
            'total_population': sum(s.population for s in living),
            'most_populous': max(living, key=lambda s: s.population) if living else None,
            'oldest_species': min(living, key=lambda s: s.generation_born) if living else None
        }
