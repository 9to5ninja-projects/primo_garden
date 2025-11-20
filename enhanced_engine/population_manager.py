"""
Population Management System
Handles large populations efficiently with adaptive strategies
"""

import numpy as np
from typing import Dict, List, Tuple

class PopulationManager:
    """Manages large populations with performance optimization"""
    
    def __init__(self, max_cells_per_species=200, total_cell_limit=5000):
        self.max_cells_per_species = max_cells_per_species
        self.total_cell_limit = total_cell_limit
        self.cull_stats = {'total_culled': 0, 'by_species': {}}
        
    def should_cull_population(self, total_population: int, species_count: int) -> bool:
        """Determine if population needs culling"""
        return total_population > self.total_cell_limit or species_count > 100
    
    def cull_population_intelligent(self, grid_cells, generation: int, species_registry=None):
        """
        Intelligently reduce population while preserving diversity
        
        Strategy:
        1. Keep all unique species (at least 1 representative)
        2. Limit per-species population based on fitness
        3. Prefer higher energy, more complex, and younger organisms
        4. Maintain spatial distribution
        
        Accepts:
        - Dictionary {pos: cell}
        - 2D array [[cell, cell, ...], ...]
        
        Args:
            grid_cells: Grid cells (dict or 2D array)
            generation: Current generation number
            species_registry: Dict of {species_id: Species} for looking up species data
        
        Returns same format as input
        """
        # Convert to dictionary format for processing
        if isinstance(grid_cells, dict):
            cells_dict = grid_cells
            return_dict = True
        else:
            # Convert 2D array to dict
            cells_dict = {}
            for y, row in enumerate(grid_cells):
                for x, cell in enumerate(row):
                    if cell and hasattr(cell, 'is_alive') and cell.is_alive:
                        cells_dict[(x, y)] = cell
            return_dict = False
        
        if not cells_dict:
            return grid_cells  # Return original format if empty
        
        # Group by species
        species_groups = {}
        for pos, cell in cells_dict.items():
            species_id = cell.species_id
            if species_id not in species_groups:
                species_groups[species_id] = []
            species_groups[species_id].append((pos, cell))
        
        culled_cells = {}
        total_kept = 0
        total_removed = 0
        
        # Calculate per-species limits based on diversity
        num_species = len(species_groups)
        base_per_species = max(50, self.total_cell_limit // max(num_species, 10))
        
        for species_id, cells in species_groups.items():
            if len(cells) <= base_per_species:
                # Keep all if under limit
                for pos, cell in cells:
                    culled_cells[pos] = cell
                total_kept += len(cells)
            else:
                # Score each organism
                scored_cells = []
                for pos, cell in cells:
                    score = self._calculate_fitness_score(cell, generation, species_registry)
                    scored_cells.append((score, pos, cell))
                
                # Keep top performers + random sampling for diversity
                scored_cells.sort(reverse=True, key=lambda x: x[0])
                
                # Keep top 70% based on score, 30% random for diversity
                elite_count = int(base_per_species * 0.7)
                random_count = base_per_species - elite_count
                
                # Elite organisms
                for i in range(min(elite_count, len(scored_cells))):
                    _, pos, cell = scored_cells[i]
                    culled_cells[pos] = cell
                    total_kept += 1
                
                # Random sampling from the rest for genetic diversity
                remaining = scored_cells[elite_count:]
                if remaining and random_count > 0:
                    import random
                    random_sample = random.sample(remaining, min(random_count, len(remaining)))
                    for _, pos, cell in random_sample:
                        culled_cells[pos] = cell
                        total_kept += 1
                
                removed = len(cells) - (min(elite_count, len(scored_cells)) + min(random_count, len(remaining)))
                total_removed += removed
                
                if species_id not in self.cull_stats['by_species']:
                    self.cull_stats['by_species'][species_id] = 0
                self.cull_stats['by_species'][species_id] += removed
        
        self.cull_stats['total_culled'] += total_removed
        
        if total_removed > 0:
            print(f"🔪 CULLED: Removed {total_removed} cells, kept {total_kept} ({num_species} species)")
        
        # Convert back to original format
        if return_dict:
            return culled_cells
        else:
            # Convert back to 2D array
            import numpy as np
            height = max(pos[1] for pos in culled_cells.keys()) + 1
            width = max(pos[0] for pos in culled_cells.keys()) + 1
            new_grid = [[None for _ in range(width)] for _ in range(height)]
            for (x, y), cell in culled_cells.items():
                new_grid[y][x] = cell
            return new_grid
    
    def _calculate_fitness_score(self, cell, generation: int, species_registry=None) -> float:
        """
        Calculate fitness score for organism selection
        Higher score = more likely to survive culling
        
        Args:
            cell: Cell object
            generation: Current generation
            species_registry: Optional dict of {species_id: Species}
        """
        score = 0.0
        
        # Get species data if available
        species = None
        if species_registry:
            species = species_registry.get(cell.species_id)
        
        # Energy level (0-100 points)
        if species:
            energy_ratio = cell.energy / (species.traits.base_energy * 2)
        else:
            energy_ratio = cell.energy / 100  # Fallback
        score += min(100, energy_ratio * 50)
        
        # Complexity (0-50 points)
        if species:
            complexity = species.traits.complexity
            score += min(50, complexity * 10)
        
        # Age bonus (younger = fresher genes, 0-30 points)
        age = cell.age if hasattr(cell, 'age') else (generation - getattr(cell, 'birth_generation', 0))
        age_score = max(0, 30 - (age * 0.5))
        score += age_score
        
        # Metabolic efficiency (0-40 points)
        if species:
            efficiency = species.traits.metabolic_efficiency
            score += efficiency * 40
        
        # Predator bonus (more complex ecosystem role, +20 points)
        if species and hasattr(species, 'can_hunt'):
            if species.can_hunt():
                score += 20
        
        # Random factor for diversity (0-10 points)
        import random
        score += random.random() * 10
        
        return score
    
    def get_population_stats(self, grid_cells) -> Dict:
        """Get current population statistics (handles dict or 2D array)"""
        # Convert to dict if needed
        if isinstance(grid_cells, dict):
            cells_dict = grid_cells
        else:
            cells_dict = {}
            for y, row in enumerate(grid_cells):
                for x, cell in enumerate(row):
                    if cell and hasattr(cell, 'is_alive') and cell.is_alive:
                        cells_dict[(x, y)] = cell
        
        if not cells_dict:
            return {'total': 0, 'species': 0}
        
        species_counts = {}
        for cell in cells_dict.values():
            species_id = cell.species_id
            species_counts[species_id] = species_counts.get(species_id, 0) + 1
        
        return {
            'total': len(cells_dict),
            'species': len(species_counts),
            'largest_species': max(species_counts.values()) if species_counts else 0,
            'per_species_breakdown': species_counts
        }
    
    def adaptive_birth_control(self, current_pop: int, current_species: int) -> float:
        """
        Adjust birth rates based on population pressure
        Returns multiplier for birth chance (0.0 to 1.0)
        """
        # When approaching limits, reduce birth rates
        pop_ratio = current_pop / self.total_cell_limit
        species_ratio = current_species / 100
        
        pressure = max(pop_ratio, species_ratio)
        
        if pressure < 0.5:
            return 1.0  # Full birth rate
        elif pressure < 0.7:
            return 0.8  # Slight reduction
        elif pressure < 0.85:
            return 0.5  # Moderate reduction
        elif pressure < 0.95:
            return 0.25  # Heavy reduction
        else:
            return 0.1  # Emergency brakes
    
    def print_culling_report(self):
        """Print report of culling activity"""
        if self.cull_stats['total_culled'] == 0:
            print("No culling performed yet.")
            return
        
        print("\n" + "=" * 60)
        print("POPULATION CULLING REPORT")
        print("=" * 60)
        print(f"Total organisms culled: {self.cull_stats['total_culled']:,}")
        print(f"Species affected: {len(self.cull_stats['by_species'])}")
        
        if self.cull_stats['by_species']:
            print("\nTop 10 most culled species:")
            sorted_species = sorted(
                self.cull_stats['by_species'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            for species_id, count in sorted_species:
                print(f"  Species {species_id}: {count:,} culled")
        
        print("=" * 60 + "\n")
