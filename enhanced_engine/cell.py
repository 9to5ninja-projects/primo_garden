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
        
    def age_one_generation(self, species, zone_modifier: float = 1.0):
        """Process one generation tick - decay energy and age"""
        self.age += 1
        
        # Energy decay
        decay = int(species.traits.energy_decay * zone_modifier)
        self.energy = max(0, self.energy - decay)
        
        # Photosynthesis/energy generation
        gain = int(species.traits.photosynthesis_rate * zone_modifier)
        self.energy = min(self.max_energy, self.energy + gain)
        
        # Death by starvation
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
        """Check if cell can afford to move"""
        return (self.is_alive and 
                species.traits.can_move and 
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
    
    def get_color(self, species) -> Tuple[int, int, int]:
        """Get color with energy-based brightness"""
        base_color = species.traits.color
        
        # Dim color based on energy level
        energy_pct = self.energy / self.max_energy
        brightness = 0.4 + (0.6 * energy_pct)  # Range from 40% to 100% brightness
        
        return tuple(int(c * brightness) for c in base_color)
    
    def __repr__(self):
        return f"Cell(pos=({self.x},{self.y}), species={self.species_id}, energy={self.energy}, alive={self.is_alive})"
