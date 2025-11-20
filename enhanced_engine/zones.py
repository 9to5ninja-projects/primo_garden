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
    
    # Population limits (Phase 4: Carrying Capacity)
    carrying_capacity: int = 50  # Max cells per zone before overcrowding
    
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
                carrying_capacity=120,  # Rich zone supports more life
                background_color=(30, 40, 25)
            ),
            ZoneType.DESERT: ZoneProperties(
                name="Desert Wastes",
                energy_generation_mult=0.5,
                energy_decay_mult=1.5,
                movement_cost_mult=1.3,
                carrying_capacity=60,  # Harsh zone supports less life
                background_color=(45, 40, 25)
            ),
            ZoneType.TOXIC: ZoneProperties(
                name="Toxic Zone",
                energy_decay_mult=2.0,
                mutation_rate_mult=3.0,
                reproduction_cost_mult=1.5,
                carrying_capacity=40,  # Very harsh, minimal capacity
                background_color=(25, 45, 25)
            ),
            ZoneType.NEUTRAL: ZoneProperties(
                name="Neutral Ground",
                carrying_capacity=100,  # Standard capacity
                background_color=(20, 20, 20)
            ),
            ZoneType.PARADISE: ZoneProperties(
                name="Paradise",
                energy_generation_mult=2.0,
                energy_decay_mult=0.5,
                reproduction_cost_mult=0.7,
                mutation_rate_mult=0.5,
                carrying_capacity=150,  # Paradise supports abundant life
                background_color=(25, 30, 40)
            ),
            ZoneType.VOID: ZoneProperties(
                name="The Void",
                can_enter=False,
                carrying_capacity=0,  # Nothing can live here
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
        self.grid = None  # Reference to grid for cell counting (set by ZoneManager)
    
    def contains(self, x: int, y: int) -> bool:
        """Check if coordinates are within this zone"""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def get_center(self) -> Tuple[int, int]:
        """Get center coordinates of zone"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def get_cell_count(self) -> int:
        """Count living cells in this zone (Phase 4: Carrying Capacity)"""
        if not self.grid:
            return 0
        
        count = 0
        for y in range(self.y, min(self.y + self.height, len(self.grid.cells))):
            for x in range(self.x, min(self.x + self.width, len(self.grid.cells[0]))):
                cell = self.grid.cells[y][x]
                if cell and cell.is_alive:
                    count += 1
        return count
    
    def get_population_pressure(self) -> float:
        """Calculate population pressure multiplier (Phase 4: Carrying Capacity)
        
        Returns:
            0.5-1.3x multiplier based on crowding
            < 50% capacity: 1.3x (plenty of resources)
            50-100% capacity: 1.0x (normal)
            100-150% capacity: 0.8-1.0x (moderate pressure)
            > 150% capacity: 0.5-0.8x (severe overcrowding)
        """
        if self.properties.carrying_capacity == 0:
            return 0.0  # Void zones
        
        current_pop = self.get_cell_count()
        capacity = self.properties.carrying_capacity
        
        if current_pop < capacity * 0.5:
            # Plenty of room - bonus resources
            return 1.3
        elif current_pop < capacity:
            # Normal density - smooth transition from 1.3 to 1.0
            ratio = current_pop / capacity
            return 1.3 - (ratio * 0.3)  # 1.3 at 0% to 1.0 at 100%
        elif current_pop < capacity * 1.3:
            # Moderate overcrowding - manageable penalty
            overcrowding_ratio = (current_pop - capacity) / (capacity * 0.3)
            return 1.0 - (overcrowding_ratio * 0.3)  # 1.0 at 100% to 0.7 at 130%
        else:
            # Severe overcrowding - harsh but survivable
            return 0.6  # Minimum 60% energy (was 30%)
    
    def __repr__(self):
        return f"Zone({self.properties.name} at ({self.x},{self.y}) size {self.width}x{self.height})"


class ZoneManager:
    """Manages environmental zones in the simulation"""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.zones = []
        self.generation = 0
        self.shift_interval = 100  # Zones shift every N generations
        self.shift_enabled = False
        
        # Default: entire grid is neutral
        self.default_zone = Zone(0, 0, grid_width, grid_height, 
                                ZoneProperties.from_type(ZoneType.NEUTRAL))
    
    def enable_shifting(self, interval: int = 100):
        """Enable environmental zone shifting"""
        self.shift_enabled = True
        self.shift_interval = interval
    
    def step(self):
        """Advance generation and potentially shift zones"""
        self.generation += 1
        if self.shift_enabled and self.generation % self.shift_interval == 0:
            self.shift_zones()
    
    def shift_zones(self):
        """Gradually shift zone boundaries and types"""
        if not self.zones:
            return
        
        changes = []
        for i, zone in enumerate(self.zones):
            # Moderate chance to change zone type (30%)
            if random.random() < 0.3:
                zone_types = [ZoneType.FERTILE, ZoneType.DESERT, 
                             ZoneType.TOXIC, ZoneType.PARADISE]
                old_type = zone.properties.name
                new_type = random.choice(zone_types)
                zone.properties = ZoneProperties.from_type(new_type)
                changes.append(f"Zone {i+1}: {old_type} -> {zone.properties.name}")
            
            # Higher chance to shift boundaries (70%)
            if random.random() < 0.7:
                dx = random.randint(-8, 8)
                dy = random.randint(-8, 8)
                zone.x = max(0, min(self.grid_width - zone.width, zone.x + dx))
                zone.y = max(0, min(self.grid_height - zone.height, zone.y + dy))
            
            # Change size more frequently (60%)
            if random.random() < 0.6:
                dw = random.randint(-8, 8)
                dh = random.randint(-8, 8)
                zone.width = max(15, min(80, zone.width + dw))
                zone.height = max(15, min(80, zone.height + dh))
        
        if changes:
            print("  Zone transformations:", ", ".join(changes))
        return len(changes)
    
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
