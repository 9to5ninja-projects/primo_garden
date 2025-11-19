"""
Environmental zones for Primordial Garden 2.0
Different regions with different rules
"""
from dataclasses import dataclass
from typing import Tuple
from enum import Enum
import random


class ZoneType(Enum):
    """Predefined zone types"""
    FERTILE = "fertile"
    DESERT = "desert"
    TOXIC = "toxic"
    NEUTRAL = "neutral"
    PARADISE = "paradise"
    VOID = "void"


@dataclass
class ZoneProperties:
    """Properties that define a zone's characteristics"""
    name: str
    
    # Energy modifiers
    energy_generation_mult: float = 1.0  # Multiply photosynthesis
    energy_decay_mult: float = 1.0  # Multiply energy decay
    
    # Reproduction modifiers
    reproduction_cost_mult: float = 1.0
    mutation_rate_mult: float = 1.0
    
    # Movement modifiers
    movement_cost_mult: float = 1.0
    can_enter: bool = True  # Some zones might be barriers
    
    # Visual
    background_color: Tuple[int, int, int] = (20, 20, 20)
    
    @staticmethod
    def from_type(zone_type: ZoneType) -> 'ZoneProperties':
        """Create zone properties from preset type"""
        presets = {
            ZoneType.FERTILE: ZoneProperties(
                name="Fertile Plains",
                energy_generation_mult=1.5,
                energy_decay_mult=0.8,
                background_color=(30, 40, 25)
            ),
            ZoneType.DESERT: ZoneProperties(
                name="Desert Wastes",
                energy_generation_mult=0.5,
                energy_decay_mult=1.5,
                movement_cost_mult=1.3,
                background_color=(45, 40, 25)
            ),
            ZoneType.TOXIC: ZoneProperties(
                name="Toxic Zone",
                energy_decay_mult=2.0,
                mutation_rate_mult=3.0,
                reproduction_cost_mult=1.5,
                background_color=(25, 45, 25)
            ),
            ZoneType.NEUTRAL: ZoneProperties(
                name="Neutral Ground",
                background_color=(20, 20, 20)
            ),
            ZoneType.PARADISE: ZoneProperties(
                name="Paradise",
                energy_generation_mult=2.0,
                energy_decay_mult=0.5,
                reproduction_cost_mult=0.7,
                mutation_rate_mult=0.5,
                background_color=(25, 30, 40)
            ),
            ZoneType.VOID: ZoneProperties(
                name="The Void",
                can_enter=False,
                background_color=(0, 0, 0)
            )
        }
        return presets.get(zone_type, presets[ZoneType.NEUTRAL])


class Zone:
    """A region of the grid with specific properties"""
    
    def __init__(self, x: int, y: int, width: int, height: int, properties: ZoneProperties):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.properties = properties
    
    def contains(self, x: int, y: int) -> bool:
        """Check if coordinates are within this zone"""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def get_center(self) -> Tuple[int, int]:
        """Get center coordinates of zone"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def __repr__(self):
        return f"Zone({self.properties.name} at ({self.x},{self.y}) size {self.width}x{self.height})"


class ZoneManager:
    """Manages environmental zones in the simulation"""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.zones = []
        
        # Default: entire grid is neutral
        self.default_zone = Zone(0, 0, grid_width, grid_height, 
                                ZoneProperties.from_type(ZoneType.NEUTRAL))
    
    def add_zone(self, zone: Zone):
        """Add a zone (later zones override earlier ones)"""
        self.zones.append(zone)
    
    def get_zone_at(self, x: int, y: int) -> Zone:
        """Get the zone at specific coordinates"""
        # Check zones in reverse order (later zones have priority)
        for zone in reversed(self.zones):
            if zone.contains(x, y):
                return zone
        return self.default_zone
    
    def create_random_zones(self, num_zones: int = 5, min_size: int = 20, max_size: int = 60):
        """Generate random zones for variety"""
        zone_types = list(ZoneType)
        zone_types.remove(ZoneType.NEUTRAL)  # Don't create random neutral zones
        
        for _ in range(num_zones):
            width = random.randint(min_size, max_size)
            height = random.randint(min_size, max_size)
            x = random.randint(0, max(0, self.grid_width - width))
            y = random.randint(0, max(0, self.grid_height - height))
            
            zone_type = random.choice(zone_types)
            properties = ZoneProperties.from_type(zone_type)
            
            self.add_zone(Zone(x, y, width, height, properties))
    
    def create_quadrant_zones(self):
        """Create 4 different zones in quadrants"""
        hw = self.grid_width // 2
        hh = self.grid_height // 2
        
        # Top-left: Fertile
        self.add_zone(Zone(0, 0, hw, hh, ZoneProperties.from_type(ZoneType.FERTILE)))
        
        # Top-right: Desert
        self.add_zone(Zone(hw, 0, hw, hh, ZoneProperties.from_type(ZoneType.DESERT)))
        
        # Bottom-left: Toxic
        self.add_zone(Zone(0, hh, hw, hh, ZoneProperties.from_type(ZoneType.TOXIC)))
        
        # Bottom-right: Paradise
        self.add_zone(Zone(hw, hh, hw, hh, ZoneProperties.from_type(ZoneType.PARADISE)))
    
    def create_ring_world(self, center_radius: int = 50):
        """Create a central paradise surrounded by harsh zones"""
        cx = self.grid_width // 2
        cy = self.grid_height // 2
        
        # Central paradise
        self.add_zone(Zone(
            cx - center_radius, cy - center_radius,
            center_radius * 2, center_radius * 2,
            ZoneProperties.from_type(ZoneType.PARADISE)
        ))
        
        # Surrounding toxic ring (approximate with 4 zones)
        ring_width = 40
        
        # Top
        self.add_zone(Zone(
            cx - center_radius - ring_width, cy - center_radius - ring_width,
            (center_radius * 2) + (ring_width * 2), ring_width,
            ZoneProperties.from_type(ZoneType.TOXIC)
        ))
        
        # Bottom
        self.add_zone(Zone(
            cx - center_radius - ring_width, cy + center_radius,
            (center_radius * 2) + (ring_width * 2), ring_width,
            ZoneProperties.from_type(ZoneType.TOXIC)
        ))
        
        # Left
        self.add_zone(Zone(
            cx - center_radius - ring_width, cy - center_radius,
            ring_width, center_radius * 2,
            ZoneProperties.from_type(ZoneType.TOXIC)
        ))
        
        # Right
        self.add_zone(Zone(
            cx + center_radius, cy - center_radius,
            ring_width, center_radius * 2,
            ZoneProperties.from_type(ZoneType.TOXIC)
        ))
    
    def get_all_zones(self):
        """Get list of all zones"""
        return self.zones
