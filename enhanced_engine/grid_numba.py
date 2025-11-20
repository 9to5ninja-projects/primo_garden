"""
Numba-optimized grid operations for Primordial Garden
These functions integrate with the existing Grid class for performance
"""
import numpy as np
from numba import jit, prange


@jit(nopython=True, parallel=True, cache=True)
def count_all_neighbors(alive_grid, wrap=True):
    """
    Count living neighbors for every position in the grid
    
    Args:
        alive_grid: 2D numpy bool array (height x width)
        wrap: Whether edges wrap around
    
    Returns:
        2D numpy int array with neighbor counts
    """
    height, width = alive_grid.shape
    neighbor_counts = np.zeros((height, width), dtype=np.int32)
    
    for y in prange(height):
        for x in range(width):
            count = 0
            
            # Check all 8 neighbors
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    
                    nx = x + dx
                    ny = y + dy
                    
                    if wrap:
                        nx = nx % width
                        ny = ny % height
                    else:
                        if nx < 0 or nx >= width or ny < 0 or ny >= height:
                            continue
                    
                    if alive_grid[ny, nx]:
                        count += 1
            
            neighbor_counts[y, x] = count
    
    return neighbor_counts


@jit(nopython=True, parallel=True, cache=True)
def process_energy_decay_batch(energy_array, alive_array, decay_rates, width, height):
    """
    Process energy decay for all cells in parallel
    
    Args:
        energy_array: 2D array of current energy values (height x width)
        alive_array: 2D bool array of which cells are alive
        decay_rates: 2D array of energy decay rates per cell
        width: Grid width
        height: Grid height
    
    Returns:
        Updated energy_array, Updated alive_array (died if energy <= 0)
    """
    deaths = 0
    
    for y in prange(height):
        for x in range(width):
            if alive_array[y, x]:
                energy_array[y, x] -= decay_rates[y, x]
                
                # Check for starvation
                if energy_array[y, x] <= 0:
                    alive_array[y, x] = False
                    energy_array[y, x] = 0
                    deaths += 1
    
    return energy_array, alive_array, deaths


@jit(nopython=True)
def get_birth_and_death_positions(alive_grid, neighbor_counts, width, height):
    """
    Determine which positions should have births and deaths
    Based on Conway's rules + energy requirements
    
    This is a PURE CONWAY ANALYSIS - actual birth/death logic stays in Python
    to handle species, energy, zones, etc.
    
    Returns:
        potential_births: List of (x, y) positions that meet Conway birth criteria (2-4 neighbors)
        potential_deaths: List of (x, y) positions that meet Conway death criteria
    """
    birth_positions = []
    death_positions = []
    
    for y in range(height):
        for x in range(width):
            neighbors = neighbor_counts[y, x]
            
            if alive_grid[y, x]:
                # Living cell death checks (under/overcrowding)
                if neighbors < 2 or neighbors > 3:
                    death_positions.append((x, y))
            else:
                # Empty cell birth checks (2-4 neighbors for relaxed Conway)
                if 2 <= neighbors <= 4:
                    birth_positions.append((x, y))
    
    return birth_positions, death_positions
