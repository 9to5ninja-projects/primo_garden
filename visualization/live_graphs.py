"""
Real-time graphing system for Primordial Garden
Displays population, species, and energy metrics during simulation
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for pygame integration
import matplotlib.pyplot as plt
from collections import deque
from typing import Dict, List
import numpy as np


class LiveGraphs:
    """Manages real-time plotting of simulation metrics"""
    
    def __init__(self, max_history: int = 500):
        self.max_history = max_history
        
        # Data storage
        self.generation_history = deque(maxlen=max_history)
        self.population_history = deque(maxlen=max_history)
        self.species_history = deque(maxlen=max_history)
        self.births_history = deque(maxlen=max_history)
        self.deaths_history = deque(maxlen=max_history)
        self.mutations_history = deque(maxlen=max_history)
        
        # Figure setup
        self.fig = None
        self.axes = None
        self.setup_figure()
    
    def setup_figure(self):
        """Initialize matplotlib figure with subplots"""
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('Primordial Garden - Live Metrics', fontsize=14, fontweight='bold')
        
        # Configure each subplot
        titles = [
            'Population Over Time',
            'Species Count Over Time', 
            'Births/Deaths/Mutations',
            'Species Diversity'
        ]
        
        for idx, (ax, title) in enumerate(zip(self.axes.flat, titles)):
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Generation')
        
        self.axes[0, 0].set_ylabel('Population')
        self.axes[0, 1].set_ylabel('Species Count')
        self.axes[1, 0].set_ylabel('Events per Generation')
        self.axes[1, 1].set_ylabel('Diversity Index')
        
        plt.tight_layout()
    
    def update(self, stats: Dict):
        """Update graphs with new data point"""
        gen = stats.get('generation', 0)
        pop = stats.get('population', 0)
        species = stats.get('species_count', 0)
        births = stats.get('births', 0)
        deaths = stats.get('deaths', 0)
        mutations = stats.get('mutations', 0)
        
        # Append new data
        self.generation_history.append(gen)
        self.population_history.append(pop)
        self.species_history.append(species)
        self.births_history.append(births)
        self.deaths_history.append(deaths)
        self.mutations_history.append(mutations)
    
    def render(self) -> np.ndarray:
        """Generate graph image as numpy array for pygame display"""
        if len(self.generation_history) < 2:
            return None
        
        # Clear all axes
        for ax in self.axes.flat:
            ax.clear()
            ax.grid(True, alpha=0.3)
        
        gens = list(self.generation_history)
        
        # Plot 1: Population
        self.axes[0, 0].plot(gens, list(self.population_history), 
                            color='#00ff00', linewidth=2, label='Population')
        self.axes[0, 0].set_title('Population Over Time')
        self.axes[0, 0].set_ylabel('Population')
        self.axes[0, 0].legend()
        self.axes[0, 0].set_xlabel('Generation')
        
        # Plot 2: Species Count
        self.axes[0, 1].plot(gens, list(self.species_history), 
                            color='#ffaa00', linewidth=2, label='Species')
        self.axes[0, 1].set_title('Species Count Over Time')
        self.axes[0, 1].set_ylabel('Species Count')
        self.axes[0, 1].legend()
        self.axes[0, 1].set_xlabel('Generation')
        
        # Plot 3: Events (Births/Deaths/Mutations)
        self.axes[1, 0].plot(gens, list(self.births_history), 
                            color='#00ff00', linewidth=1, alpha=0.7, label='Births')
        self.axes[1, 0].plot(gens, list(self.deaths_history), 
                            color='#ff0000', linewidth=1, alpha=0.7, label='Deaths')
        self.axes[1, 0].plot(gens, list(self.mutations_history), 
                            color='#ff00ff', linewidth=1, alpha=0.7, label='Mutations')
        self.axes[1, 0].set_title('Births/Deaths/Mutations')
        self.axes[1, 0].set_ylabel('Events per Generation')
        self.axes[1, 0].legend()
        self.axes[1, 0].set_xlabel('Generation')
        
        # Plot 4: Diversity (species/population ratio)
        diversity = [s / max(p, 1) for s, p in zip(self.species_history, self.population_history)]
        self.axes[1, 1].plot(gens, diversity, 
                            color='#00ffff', linewidth=2, label='Diversity')
        self.axes[1, 1].set_title('Species Diversity (Species/Population)')
        self.axes[1, 1].set_ylabel('Diversity Ratio')
        self.axes[1, 1].legend()
        self.axes[1, 1].set_xlabel('Generation')
        
        # Render to numpy array
        self.fig.canvas.draw()
        
        # Get the RGBA buffer from the figure
        w, h = self.fig.canvas.get_width_height()
        buf = np.frombuffer(self.fig.canvas.buffer_rgba(), dtype=np.uint8)
        buf = buf.reshape(h, w, 4)[:, :, :3]  # Drop alpha channel
        
        return buf
    
    def save(self, filename: str):
        """Save current graphs to file"""
        if self.fig:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Graphs saved to {filename}")
    
    def close(self):
        """Clean up matplotlib resources"""
        if self.fig:
            plt.close(self.fig)
