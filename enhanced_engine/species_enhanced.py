"""
Species system for Primordial Garden 2.0
Each species has genetic traits that affect survival, energy, and behavior
"""
from dataclasses import dataclass
from typing import Tuple
import random
from .colorization import SpeciesColorizer


@dataclass
class SpeciesTraits:
    """Genetic traits that define a species' behavior and efficiency"""
    
    # Energy traits
    base_energy: int = 100  # Starting energy for new cells
    energy_decay: int = 2   # Energy lost per generation
    energy_from_birth: int = 50  # Energy cost to reproduce
    photosynthesis_rate: int = 3  # Energy gained per generation (base)
    
    # Mobility traits (ALL organisms can move - even bacteria drift/swim)
    movement_range: int = 1  # Base movement range (can be increased for migrants)
    movement_cost: int = 1   # Energy cost per move (scales with complexity: 1 + complexity/2)
    # movement_strategy determined by complexity: 1=seek energy, 2=flee, 3+=hunt
    
    # Predation traits (unlocked at complexity 3+, efficiency scales with complexity)
    hunting_efficiency: float = 0.5  # Energy transfer rate when consuming (increases with complexity)
    can_be_consumed: bool = True  # Can be eaten by predators
    
    # Colony clustering traits (same-species cells benefit from adjacency)
    colonial_affinity: float = 1.2  # Energy bonus when adjacent to same species (1.0-1.5x)
    cluster_reproduction_bonus: float = 1.3  # Reproduction boost in colonies (1.0-2.0x)
    
    # Survival traits
    overcrowding_tolerance: int = 3  # Max neighbors before stress
    isolation_tolerance: int = 1  # Min neighbors needed
    
    # Reproduction traits
    reproduction_threshold: int = 60  # Min energy to reproduce
    mutation_rate: float = 0.01  # Chance to mutate on birth
    sexual_reproduction: bool = False  # Requires two parents
    
    # Organism complexity (affects energy needs)
    complexity: int = 1  # 1=simple, 2=moderate, 3=complex
    metabolic_efficiency: float = 1.0  # Energy usage multiplier
    
    # Environmental adaptation
    heat_tolerance: float = 0.5  # 0.0-1.0 (desert adaptation)
    cold_tolerance: float = 0.5  # 0.0-1.0 (arctic adaptation)
    toxin_resistance: float = 0.5  # 0.0-1.0 (toxic zone adaptation)
    
    # Lifespan and aging
    max_lifespan: int = 200  # Maximum generations before old age death (0 = immortal)
    age_decline_start: float = 0.7  # When aging effects start (70% of lifespan)
    
    # Food/Energy source type
    energy_source: str = "photosynthesis"  # "photosynthesis", "predation", "hybrid"
    starvation_threshold: int = 10  # Die if energy below this outside optimal zone
    optimal_zone_bonus: float = 2.0  # Energy multiplier in ideal environment
    
    # Habitat specialization (Phase 3)
    native_zone_type: str = "fertile"  # Zone where this lineage evolved
    native_zone_affinity: float = 1.5  # Reproduction bonus in native zone (1.0-2.0x)
    
    # Visual
    color: Tuple[int, int, int] = (0, 255, 0)  # RGB color
    
    def __post_init__(self):
        """Validate traits are within reasonable bounds"""
        self.base_energy = max(1, min(200, self.base_energy))
        self.energy_decay = max(1, min(10, self.energy_decay))
        self.photosynthesis_rate = max(0, min(20, self.photosynthesis_rate))
        self.mutation_rate = max(0.0, min(1.0, self.mutation_rate))
        self.complexity = max(1, min(5, self.complexity))
        self.metabolic_efficiency = max(0.5, min(2.0, self.metabolic_efficiency))
        self.heat_tolerance = max(0.0, min(1.0, self.heat_tolerance))
        self.cold_tolerance = max(0.0, min(1.0, self.cold_tolerance))
        self.toxin_resistance = max(0.0, min(1.0, self.toxin_resistance))
        self.max_lifespan = max(0, min(1000, self.max_lifespan))
        self.colonial_affinity = max(1.0, min(1.5, self.colonial_affinity))
        self.cluster_reproduction_bonus = max(1.0, min(2.0, self.cluster_reproduction_bonus))
        
        # Movement cost scales with complexity but stays low
        # Complexity 1: 1 energy (drift/float)
        # Complexity 2: 2 energy (active swimming)
        # Complexity 3: 2 energy (hunting movement)
        # Complexity 4+: 3 energy (complex movement)
        self.movement_cost = max(1, 1 + (self.complexity // 2))
    
    def get_complexity_cost(self) -> float:
        """Higher complexity organisms need more energy"""
        return 1.0 + (self.complexity - 1) * 0.3
    
    def get_adaptation_bonus(self, zone_type: str) -> float:
        """Get energy bonus/penalty based on adaptation to zone"""
        if zone_type == "desert":
            return 0.5 + (self.heat_tolerance * 1.0)  # 0.5x to 1.5x
        elif zone_type == "fertile":
            return 1.0 + (1.0 - abs(self.heat_tolerance - 0.5)) * 0.5
        elif zone_type == "toxic":
            return 0.3 + (self.toxin_resistance * 1.2)  # 0.3x to 1.5x
        elif zone_type == "paradise":
            return 1.5  # Everyone thrives
        return 1.0
    
    def is_optimal_zone(self, zone_type: str) -> bool:
        """Check if this is an optimal zone for this species"""
        if zone_type == "desert" and self.heat_tolerance > 0.7:
            return True
        elif zone_type == "fertile" and 0.4 <= self.heat_tolerance <= 0.6:
            return True
        elif zone_type == "toxic" and self.toxin_resistance > 0.7:
            return True
        elif zone_type == "paradise":
            return True
        return False
    
    def get_energy_source_multiplier(self, has_prey_nearby: bool) -> float:
        """Calculate energy gain based on food source availability"""
        if self.energy_source == "photosynthesis":
            return 1.0  # Always gets photosynthesis
        elif self.energy_source == "predation":
            return 2.0 if has_prey_nearby else 0.1  # Needs prey or starves
        else:  # hybrid
            return 1.5 if has_prey_nearby else 0.7  # Flexible
    
    def get_movement_strategy(self) -> str:
        """Get movement strategy based on complexity level (AUTOMATIC)"""
        if self.complexity == 1:
            # Simple organisms: phototropism/chemotaxis (seek energy)
            return "energy_seeking"
        elif self.complexity == 2:
            # Moderate organisms: can sense danger and flee
            return "flee"
        else:
            # Complex organisms (3+): can hunt
            return "hunt"
    
    def can_hunt(self) -> bool:
        """Check if organism is complex enough to hunt (complexity 3+)"""
        return self.complexity >= 3
    
    def get_hunting_efficiency(self) -> float:
        """Get hunting efficiency based on complexity"""
        if not self.can_hunt():
            return 0.0
        # Complexity 3: 50%, 4: 65%, 5: 80%
        return min(0.8, 0.35 + (self.complexity * 0.15))


class Species:
    """Represents a distinct species with unique traits and genome"""
    
    _next_id = 1
    
    def __init__(self, name: str = None, traits: SpeciesTraits = None, parent_id: int = None):
        self.id = Species._next_id
        Species._next_id += 1
        
        self.name = name or f"Species_{self.id}"
        self.traits = traits or SpeciesTraits()
        self.parent_id = parent_id  # For tracking lineage
        
        # Use advanced colorization if no color set
        if self.traits.color == (0, 255, 0):  # Default green
            self.traits.color = SpeciesColorizer.generate_species_color(self.traits)
        
        # Statistics
        self.population = 0
        self.total_births = 0
        self.total_deaths = 0
        self.generation_born = 0
        
    def mutate(self, generation: int) -> 'Species':
        """Create a mutated offspring species"""
        # First, calculate the mutated complexity (needed for strategy selection)
        new_complexity = self._mutate_value(self.traits.complexity, 1)
        
        # Create traits object with mutated complexity to check available strategies
        temp_traits = SpeciesTraits(complexity=new_complexity)
        
        new_traits = SpeciesTraits(
            base_energy=self._mutate_value(self.traits.base_energy, 5),
            energy_decay=self._mutate_value(self.traits.energy_decay, 1),
            energy_from_birth=self._mutate_value(self.traits.energy_from_birth, 5),
            photosynthesis_rate=self._mutate_value(self.traits.photosynthesis_rate, 1),
            movement_range=self._mutate_value(self.traits.movement_range, 1),
            # movement_cost auto-calculated from complexity in __post_init__
            hunting_efficiency=self._mutate_value(self.traits.hunting_efficiency, 0.1, is_float=True),
            can_be_consumed=self.traits.can_be_consumed,
            colonial_affinity=self._mutate_value(self.traits.colonial_affinity, 0.05, is_float=True),
            cluster_reproduction_bonus=self._mutate_value(self.traits.cluster_reproduction_bonus, 0.1, is_float=True),
            overcrowding_tolerance=self._mutate_value(self.traits.overcrowding_tolerance, 1),
            isolation_tolerance=self._mutate_value(self.traits.isolation_tolerance, 1),
            reproduction_threshold=self._mutate_value(self.traits.reproduction_threshold, 5),
            mutation_rate=self._mutate_value(self.traits.mutation_rate, 0.005, is_float=True),
            sexual_reproduction=self.traits.sexual_reproduction if random.random() > 0.02 else not self.traits.sexual_reproduction,
            complexity=new_complexity,  # Use pre-calculated complexity
            metabolic_efficiency=self._mutate_value(self.traits.metabolic_efficiency, 0.1, is_float=True),
            heat_tolerance=self._mutate_value(self.traits.heat_tolerance, 0.1, is_float=True),
            cold_tolerance=self._mutate_value(self.traits.cold_tolerance, 0.1, is_float=True),
            toxin_resistance=self._mutate_value(self.traits.toxin_resistance, 0.1, is_float=True),
            max_lifespan=self._mutate_value(self.traits.max_lifespan, 20),
            age_decline_start=self._mutate_value(self.traits.age_decline_start, 0.05, is_float=True),
            energy_source=self._mutate_energy_source(self.traits.energy_source),
            starvation_threshold=self._mutate_value(self.traits.starvation_threshold, 3),
            optimal_zone_bonus=self._mutate_value(self.traits.optimal_zone_bonus, 0.2, is_float=True),
            native_zone_type=self._mutate_native_zone(self.traits.native_zone_type),
            native_zone_affinity=self._mutate_value(self.traits.native_zone_affinity, 0.1, is_float=True),
            color=self._mutate_color(self.traits.color)
        )
        
        mutant = Species(
            name=f"{self.name}_m{generation}",
            traits=new_traits,
            parent_id=self.id
        )
        mutant.generation_born = generation
        
        # Regenerate color based on new traits
        mutant.traits.color = SpeciesColorizer.generate_species_color(mutant.traits)
        
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
    
    @staticmethod
    def _mutate_energy_source(current: str) -> str:
        """Mutate energy source type (rare)"""
        if random.random() < 0.05:  # 5% chance to change
            options = ["photosynthesis", "predation", "hybrid"]
            options.remove(current)
            return random.choice(options)
        return current
    
    @staticmethod
    def _mutate_native_zone(current: str) -> str:
        """Mutate native zone type (very rare - long-term adaptation)"""
        if random.random() < 0.02:  # 2% chance to adapt to new zone
            zones = ["fertile", "desert", "toxic", "paradise", "neutral"]
            # More likely to move to adjacent zone than random
            if random.random() < 0.7:  # 70% chance for adjacent zone
                adjacent = {
                    "fertile": ["paradise", "neutral"],
                    "desert": ["neutral", "toxic"],
                    "toxic": ["desert", "neutral"],
                    "paradise": ["fertile", "neutral"],
                    "neutral": ["fertile", "desert", "toxic", "paradise"]
                }
                return random.choice(adjacent.get(current, zones))
            else:
                return random.choice(zones)
        return current
    
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
