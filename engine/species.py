"""
Species Tracking System
Manages individual species traits and lineage
"""

import numpy as np
import colorsys


class Species:
    def __init__(self, species_id, parent_id=None, birth_generation=0):
        self.id = species_id
        self.parent_id = parent_id
        self.birth_generation = birth_generation
        self.population = 0
        
        # Traits (for future expansion)
        self.traits = {
            'metabolism': 1.0,      # Energy consumption rate
            'reproduction': 0.5,    # Reproduction threshold
            'resilience': 1.0,      # Survival flexibility
        }
        
        # Visual
        self.color = self._generate_color()
    
    def _generate_color(self):
        """Generate a unique color for this species"""
        # Use species ID to seed color generation
        np.random.seed(self.id)
        
        # HSV color space for better variety
        hue = np.random.random()
        saturation = 0.5 + np.random.random() * 0.5  # 50-100%
        value = 0.6 + np.random.random() * 0.4       # 60-100%
        
        # Convert to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return tuple(int(c * 255) for c in rgb)
    
    def inherit_from(self, parent, mutation_strength=0.1):
        """Inherit traits from parent with mutations"""
        for trait_name in self.traits:
            parent_value = parent.traits[trait_name]
            mutation = np.random.normal(0, mutation_strength)
            self.traits[trait_name] = max(0.1, parent_value + mutation)
        
        # Color mutation (slight hue shift from parent)
        parent_hsv = colorsys.rgb_to_hsv(
            parent.color[0] / 255,
            parent.color[1] / 255,
            parent.color[2] / 255
        )
        
        hue = (parent_hsv[0] + np.random.normal(0, 0.05)) % 1.0
        saturation = np.clip(parent_hsv[1] + np.random.normal(0, 0.05), 0.3, 1.0)
        value = np.clip(parent_hsv[2] + np.random.normal(0, 0.05), 0.4, 1.0)
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        self.color = tuple(int(c * 255) for c in rgb)
