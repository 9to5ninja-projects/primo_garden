"""
Simulation Tracker
Records and analyzes simulation data over time
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class SimulationTracker:
    def __init__(self):
        self.history = {
            'generation': [],
            'total_population': [],
            'species_count': [],
            'diversity_index': [],
            'dominant_species': [],
            'dominant_population': [],
            'births': [],
            'deaths': [],
            'mutations': [],
            'avg_species_age': []
        }
    
    def snapshot(self, world):
        """Record current simulation state"""
        self.history['generation'].append(world.generation)
        self.history['total_population'].append(world.total_population)
        self.history['species_count'].append(len(world.species_registry))
        self.history['births'].append(world.births_this_gen)
        self.history['deaths'].append(world.deaths_this_gen)
        self.history['mutations'].append(world.mutations_this_gen)
        self.history['avg_species_age'].append(world.get_average_species_age())
        
        # Calculate diversity (Shannon index)
        diversity = self._calculate_diversity(world)
        self.history['diversity_index'].append(diversity)
        
        # Track dominant species
        if world.species_registry:
            dominant = max(world.species_registry.values(), key=lambda s: s.population)
            self.history['dominant_species'].append(dominant.id)
            self.history['dominant_population'].append(dominant.population)
        else:
            self.history['dominant_species'].append(0)
            self.history['dominant_population'].append(0)
    
    def _calculate_diversity(self, world):
        """Calculate Shannon diversity index"""
        if world.total_population == 0:
            return 0.0
        
        diversity = 0.0
        for species in world.species_registry.values():
            if species.population > 0:
                proportion = species.population / world.total_population
                diversity -= proportion * np.log(proportion)
        
        return diversity
    
    def export(self, filename=None):
        """Export data to CSV in exports folder"""
        # Create exports directory if it doesn't exist
        exports_dir = Path(__file__).parent.parent / "exports"
        exports_dir.mkdir(exist_ok=True)
        
        # Use provided filename or generate timestamped one
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{timestamp}.csv"
        
        filepath = exports_dir / filename
        df = pd.DataFrame(self.history)
        df.to_csv(filepath, index=False)
        print(f"Exported {len(df)} data points to {filepath}")
    
    def get_dataframe(self):
        """Return data as pandas DataFrame"""
        return pd.DataFrame(self.history)
