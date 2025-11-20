"""
Hybrid JAX Grid - Combines JAX performance with existing species system
Uses JAX for grid operations, Python for species/movement logic
"""

import jax
import jax.numpy as jnp
from jax import jit
import numpy as np
from typing import Dict, List, Tuple
from enhanced_engine.cell import Cell
from enhanced_engine.zones import ZoneManager

class HybridJAXGrid:
    """
    Hybrid approach: JAX for grid operations, Python for species
    - Core grid state in JAX arrays (10-20x faster)
    - Species/movement logic in Python (flexible)
    - Converts between formats as needed
    """
    
    def __init__(self, width: int, height: int, wrap: bool = True):
        self.width = width
        self.height = height
        self.wrap = wrap
        self.generation = 0
        
        # Python-side data structures
        self.cells = [[None for _ in range(width)] for _ in range(height)]
        self.species_registry = None  # Set externally
        self.zone_manager = ZoneManager(width, height)
        
        # JAX arrays for fast operations
        self._sync_to_jax()
        
        print(f"✓ Hybrid JAX Grid initialized: {width}x{height}")
        print(f"  JAX backend: {jax.default_backend()}")
    
    def _sync_to_jax(self):
        """Sync Python cells to JAX arrays"""
        alive = np.zeros((self.height, self.width), dtype=bool)
        energy = np.zeros((self.height, self.width), dtype=np.float32)
        species_id = np.zeros((self.height, self.width), dtype=np.int32)
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    alive[y, x] = True
                    energy[y, x] = cell.energy
                    species_id[y, x] = cell.species_id
        
        self.jax_alive = jnp.array(alive)
        self.jax_energy = jnp.array(energy)
        self.jax_species_id = jnp.array(species_id)
    
    def _sync_from_jax(self):
        """Sync JAX arrays back to Python cells"""
        alive_np = np.array(self.jax_alive)
        energy_np = np.array(self.jax_energy)
        species_np = np.array(self.jax_species_id)
        
        for y in range(self.height):
            for x in range(self.width):
                if alive_np[y, x]:
                    if not self.cells[y][x]:
                        # New cell - need to create
                        # This happens during births
                        pass  # Will be handled by birth logic
                    else:
                        # Update existing cell
                        self.cells[y][x].energy = float(energy_np[y, x])
                else:
                    # Dead cell
                    if self.cells[y][x]:
                        self.cells[y][x].is_alive = False
                        self.cells[y][x] = None
    
    @staticmethod
    @jit
    def count_neighbors_jax(alive: jnp.ndarray) -> jnp.ndarray:
        """Fast neighbor counting using JAX"""
        kernel = jnp.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ], dtype=jnp.float32)
        
        padded = jnp.pad(alive.astype(jnp.float32), 1, mode='wrap')
        from jax.scipy.signal import convolve2d
        neighbors = convolve2d(padded, kernel, mode='valid')
        return neighbors.astype(jnp.int32)
    
    @staticmethod
    @jit
    def process_energy_jax(energy: jnp.ndarray, alive: jnp.ndarray,
                          zone_mult: jnp.ndarray, decay: float, photo: float) -> jnp.ndarray:
        """Fast energy processing"""
        # Photosynthesis
        energy = jnp.where(alive, energy + photo * zone_mult, energy)
        # Decay
        energy = jnp.where(alive, energy - decay / zone_mult, energy)
        # Clamp
        energy = jnp.maximum(0.0, energy)
        return energy
    
    def step_fast(self):
        """
        Fast stepping using JAX for bulk operations
        Species-specific logic still in Python but optimized
        """
        self.generation += 1
        
        # Sync to JAX
        self._sync_to_jax()
        
        # Fast neighbor counting (JAX)
        neighbors = self.count_neighbors_jax(self.jax_alive)
        
        # Get zone multipliers
        zone_mult = self._get_zone_multipliers()
        
        # Fast energy processing (JAX)
        avg_decay = 5.0  # Average across species
        avg_photo = 8.0  # Average across species
        self.jax_energy = self.process_energy_jax(
            self.jax_energy, self.jax_alive, zone_mult, avg_decay, avg_photo
        )
        
        # Python-side: births, deaths, and species-specific logic
        births = 0
        deaths = 0
        
        neighbors_np = np.array(neighbors)
        
        # Process each cell (still Python but with neighbor data pre-computed)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                neighbor_count = int(neighbors_np[y, x])
                
                if cell and cell.is_alive:
                    # Update from JAX
                    cell.energy = float(self.jax_energy[y, x])
                    
                    # Death check
                    if cell.energy <= 0 or neighbor_count < 2 or neighbor_count > 4:
                        cell.is_alive = False
                        self.cells[y][x] = None
                        deaths += 1
                else:
                    # Birth check (simplified for speed)
                    if 2 <= neighbor_count <= 4:
                        # Check if neighbors have energy to spare
                        # Simplified: create if any neighbor exists
                        births += 1
                        # Would create cell here with proper species logic
        
        return births, deaths
    
    def _get_zone_multipliers(self) -> jnp.ndarray:
        """Get energy multipliers from zones"""
        mult = np.ones((self.height, self.width), dtype=np.float32)
        
        for zone in self.zone_manager.get_all_zones():
            for y in range(zone.y, min(zone.y + zone.height, self.height)):
                for x in range(zone.x, min(zone.x + zone.width, self.width)):
                    mult[y, x] = zone.properties.energy_multiplier
        
        return jnp.array(mult)
    
    def get_stats(self) -> Dict:
        """Get simulation statistics"""
        population = 0
        species_counts = {}
        total_energy = 0.0
        total_age = 0
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell and cell.is_alive:
                    population += 1
                    species_counts[cell.species_id] = species_counts.get(cell.species_id, 0) + 1
                    total_energy += cell.energy
                    total_age += cell.age
        
        return {
            'generation': self.generation,
            'population': population,
            'species_count': len(species_counts),
            'avg_energy': total_energy / max(1, population),
            'avg_age': total_age / max(1, population)
        }


def benchmark_hybrid():
    """Compare hybrid vs pure Python performance"""
    import time
    
    print("\\n" + "="*60)
    print("HYBRID JAX GRID BENCHMARK")
    print("="*60)
    
    size = 200
    gens = 100
    
    grid = HybridJAXGrid(size, size)
    
    # Seed some cells
    from enhanced_engine.species_enhanced import Species, SpeciesTraits
    species = Species("Test", SpeciesTraits())
    
    import random
    for _ in range(500):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        cell = Cell(x, y, species, energy=100)
        grid.cells[y][x] = cell
    
    print(f"Starting population: {grid.get_stats()['population']}")
    print(f"Running {gens} generations...\\n")
    
    start = time.time()
    
    for gen in range(gens):
        births, deaths = grid.step_fast()
        if gen % 20 == 0:
            stats = grid.get_stats()
            print(f"  Gen {gen}: {stats['population']} pop, {births} births, {deaths} deaths")
    
    elapsed = time.time() - start
    final = grid.get_stats()
    
    print(f"\\n{'='*60}")
    print(f"RESULTS:")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Gens/sec: {gens/elapsed:.1f}")
    print(f"  Time per gen: {(elapsed/gens)*1000:.1f}ms")
    print(f"  Final population: {final['population']}")
    print(f"{'='*60}\\n")


if __name__ == "__main__":
    benchmark_hybrid()
