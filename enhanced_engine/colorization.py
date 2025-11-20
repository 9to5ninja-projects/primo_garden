"""
Advanced colorization system for species visualization
Colors encode: complexity, energy source, zone adaptation, and health
"""
from typing import Tuple
import colorsys


class SpeciesColorizer:
    """Generate meaningful colors based on species traits"""
    
    @staticmethod
    def generate_species_color(traits) -> Tuple[int, int, int]:
        """
        Generate a color that encodes species characteristics:
        
        HUE (0-360°):
        - 120° (green): Photosynthesizers (complexity 1)
        - 180° (cyan): Advanced photosynthesizers (complexity 2)
        - 60° (yellow): Opportunists (complexity 2)
        - 30° (orange): Predators (complexity 3)
        - 0° (red): Apex predators (complexity 4+)
        
        SATURATION (0-100%):
        - High: Specialists (strong zone adaptation)
        - Low: Generalists (weak zone adaptation)
        
        VALUE/BRIGHTNESS (0-100%):
        - Encodes metabolic efficiency and energy source mix
        """
        complexity = traits.complexity
        
        # Base hue from complexity and behavior
        if complexity == 1:
            # Simple photosynthesizers: Green
            base_hue = 120
        elif complexity == 2:
            if traits.photosynthesis_rate > 5:
                # Advanced photosynthesizers: Cyan
                base_hue = 180
            else:
                # Opportunists/scavengers: Yellow
                base_hue = 60
        elif complexity == 3:
            # Predators: Orange
            base_hue = 30
        else:  # complexity >= 4
            # Apex predators: Red
            base_hue = 0
        
        # Add variation based on native zone for distinction
        zone_hue_shift = {
            'fertile': 0,
            'ocean': 15,
            'desert': -15,
            'arctic': 30,
            'toxic': -30,
            'volcanic': -45
        }.get(traits.native_zone_type, 0)
        
        hue = (base_hue + zone_hue_shift) % 360
        
        # Saturation from specialization (zone adaptation strength)
        specialization = max(
            traits.heat_tolerance,
            traits.cold_tolerance,
            traits.toxin_resistance
        )
        # High specialization = high saturation (vivid colors)
        # Low specialization = low saturation (muted colors)
        saturation = 0.4 + (specialization * 0.6)  # 40-100%
        
        # Value/brightness from metabolic efficiency
        # Efficient organisms = brighter
        # Inefficient = darker
        value = 0.5 + (traits.metabolic_efficiency * 0.3)  # 50-80%
        value = min(0.9, max(0.5, value))
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @staticmethod
    def apply_energy_dimming(color: Tuple[int, int, int], energy_pct: float) -> Tuple[int, int, int]:
        """
        Dim color based on energy level
        - Full energy: 100% brightness
        - Low energy: 40% brightness
        """
        brightness = 0.4 + (0.6 * energy_pct)
        return tuple(int(c * brightness) for c in color)
    
    @staticmethod
    def get_zone_color(zone_type: str) -> Tuple[int, int, int]:
        """Get background color for zone types"""
        zone_colors = {
            'fertile': (34, 139, 34),    # Forest green
            'ocean': (25, 25, 112),       # Midnight blue
            'desert': (210, 180, 140),    # Tan
            'arctic': (176, 224, 230),    # Powder blue
            'toxic': (85, 107, 47),       # Dark olive green
            'volcanic': (139, 69, 19)     # Saddle brown
        }
        return zone_colors.get(zone_type, (50, 50, 50))
    
    @staticmethod
    def get_complexity_indicator_color(complexity: int) -> Tuple[int, int, int]:
        """Get a simple indicator color for UI overlays"""
        complexity_colors = {
            1: (0, 255, 0),      # Green - simple
            2: (255, 255, 0),    # Yellow - moderate
            3: (255, 165, 0),    # Orange - complex
            4: (255, 69, 0),     # Red-orange - very complex
            5: (255, 0, 0)       # Red - extreme
        }
        return complexity_colors.get(complexity, (255, 255, 255))
