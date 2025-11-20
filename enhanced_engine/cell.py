"""
Cell implementation with energy mechanics for Primordial Garden 2.0
"""
from typing import Optional, Tuple


class Cell:
    """Individual cell with energy, position, and species traits"""
    
    def __init__(self, x: int, y: int, species, energy: int = None):
        self.x = x
        self.y = y
        self.species_id = species.id
        self.is_alive = True
        self.age = 0
        
        # Energy system
        self.energy = energy if energy is not None else species.traits.base_energy
        self.max_energy = species.traits.base_energy * 2  # Can store up to 2x base
        
        # Movement tracking
        self.has_moved_this_gen = False
        self.move_history = []  # Track last N positions
        
    def age_one_generation(self, species, zone_modifier: float = 1.0, zone_type: str = "neutral", 
                          has_prey_nearby: bool = False, population_pressure: float = 1.0):
        """Process one generation tick - decay energy and age
        
        Args:
            species: Species traits
            zone_modifier: Zone energy multiplier
            zone_type: Type of zone for adaptation
            has_prey_nearby: Whether prey is available (for predators)
            population_pressure: Carrying capacity multiplier (0.2-1.2x)
        """
        self.age += 1
        
        # Check for old age death
        if species.traits.max_lifespan > 0 and self.age >= species.traits.max_lifespan:
            self.is_alive = False
            return False
        
        # Get adaptation bonus based on environment
        adaptation_mult = species.traits.get_adaptation_bonus(zone_type)
        
        # Apply complexity cost (more complex = more energy needed)
        complexity_cost = species.traits.get_complexity_cost()
        
        # Calculate aging penalty
        aging_penalty = 1.0
        if species.traits.max_lifespan > 0:
            age_ratio = self.age / species.traits.max_lifespan
            if age_ratio > species.traits.age_decline_start:
                # Linear decline after age threshold
                decline = (age_ratio - species.traits.age_decline_start) / (1.0 - species.traits.age_decline_start)
                aging_penalty = 1.0 + decline * 0.5  # Up to 50% more energy cost
        
        # Energy decay (increased by complexity, aging, modified by zone and adaptation)
        decay = int(species.traits.energy_decay * zone_modifier * complexity_cost * aging_penalty / adaptation_mult)
        self.energy = max(0, self.energy - decay)
        
        # Energy gain based on food source availability
        food_mult = species.traits.get_energy_source_multiplier(has_prey_nearby)
        
        # Check if in optimal zone for bonus
        zone_bonus = species.traits.optimal_zone_bonus if species.traits.is_optimal_zone(zone_type) else 1.0
        
        # Photosynthesis/energy generation (boosted by adaptation, food, optimal zone, POPULATION PRESSURE)
        gain = int(species.traits.photosynthesis_rate * zone_modifier * adaptation_mult * 
                  food_mult * zone_bonus * population_pressure / species.traits.metabolic_efficiency)
        self.energy = min(self.max_energy, self.energy + gain)
        
        # Death by starvation (harsh penalty outside optimal zone)
        if not species.traits.is_optimal_zone(zone_type):
            if self.energy < species.traits.starvation_threshold:
                self.is_alive = False
                return False
        
        # Standard starvation
        if self.energy <= 0:
            self.is_alive = False
            return False
        
        return True
    
    def can_reproduce(self, species) -> bool:
        """Check if cell has enough energy to reproduce"""
        return (self.is_alive and 
                self.energy >= species.traits.reproduction_threshold)
    
    def consume_reproduction_energy(self, species) -> int:
        """Deduct reproduction cost and return energy for offspring"""
        cost = species.traits.energy_from_birth
        self.energy -= cost
        return cost // 2  # Offspring gets half the energy spent
    
    def can_move(self, species) -> bool:
        """Check if cell can afford to move (ALL organisms can move)"""
        return (self.is_alive and 
                not self.has_moved_this_gen and
                self.energy >= species.traits.movement_cost)
    
    def move_to(self, new_x: int, new_y: int, species):
        """Move cell to new position"""
        if not self.can_move(species):
            return False
        
        # Track history
        self.move_history.append((self.x, self.y))
        if len(self.move_history) > 10:
            self.move_history.pop(0)
        
        # Update position
        self.x = new_x
        self.y = new_y
        
        # Consume energy
        self.energy -= species.traits.movement_cost
        self.has_moved_this_gen = True
        
        return True
    
    def reset_movement(self):
        """Reset movement flag for new generation"""
        self.has_moved_this_gen = False
    
    def consume_prey(self, prey_cell, species, prey_species) -> int:
        """Consume another cell and gain energy"""
        if not self.is_alive or not prey_cell.is_alive:
            return 0
        
        # Transfer energy from prey to predator
        energy_gained = int(prey_cell.energy * species.traits.hunting_efficiency)
        self.energy = min(self.max_energy, self.energy + energy_gained)
        
        # Kill the prey
        prey_cell.is_alive = False
        
        return energy_gained
    
    def get_color(self, species) -> Tuple[int, int, int]:
        """Get color with energy-based brightness"""
        from .colorization import SpeciesColorizer
        
        base_color = species.traits.color
        
        # Apply energy-based dimming
        energy_pct = self.energy / self.max_energy
        return SpeciesColorizer.apply_energy_dimming(base_color, energy_pct)
    
    def __repr__(self):
        return f"Cell(pos=({self.x},{self.y}), species={self.species_id}, energy={self.energy}, alive={self.is_alive})"
