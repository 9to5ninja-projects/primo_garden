"""
Biodiversity Mechanics for Primordial Garden v0.9.0
Implements niche specialization, competitive exclusion, and mutualism
"""


class BiodiversityManager:
    """Manages ecological interactions that promote diversity"""
    
    def __init__(self):
        self.species_niches = {}  # species_id -> niche profile
        self.competitive_pressure = {}  # (species_a, species_b) -> competition strength
        
    def calculate_niche(self, species):
        """
        Calculate a species' ecological niche
        Niche = combination of energy source, zone preference, complexity
        """
        niche = {
            'energy_source': species.traits.energy_source,
            'native_zone': species.traits.native_zone_type,
            'complexity': species.traits.complexity,
            'strategy': species.traits.get_movement_strategy(),
            'colonial': species.traits.colonial_affinity > 1.15,
            'specialist': max(
                species.traits.heat_tolerance,
                species.traits.cold_tolerance,
                species.traits.toxin_resistance
            ) > 0.7
        }
        self.species_niches[species.id] = niche
        return niche
    
    def calculate_niche_overlap(self, species_a, species_b) -> float:
        """
        Calculate niche overlap between two species (0.0 = no overlap, 1.0 = identical)
        Higher overlap = more competition
        """
        niche_a = self.species_niches.get(species_a.id) or self.calculate_niche(species_a)
        niche_b = self.species_niches.get(species_b.id) or self.calculate_niche(species_b)
        
        overlap = 0.0
        weights = {
            'energy_source': 0.3,
            'native_zone': 0.25,
            'complexity': 0.2,
            'strategy': 0.15,
            'colonial': 0.05,
            'specialist': 0.05
        }
        
        # Energy source overlap
        if niche_a['energy_source'] == niche_b['energy_source']:
            overlap += weights['energy_source']
        elif 'hybrid' in [niche_a['energy_source'], niche_b['energy_source']]:
            overlap += weights['energy_source'] * 0.5  # Partial overlap
        
        # Zone preference overlap
        if niche_a['native_zone'] == niche_b['native_zone']:
            overlap += weights['native_zone']
        
        # Complexity overlap (similar complexity = compete for same resources)
        complexity_diff = abs(niche_a['complexity'] - niche_b['complexity'])
        if complexity_diff == 0:
            overlap += weights['complexity']
        elif complexity_diff == 1:
            overlap += weights['complexity'] * 0.5
        
        # Strategy overlap
        if niche_a['strategy'] == niche_b['strategy']:
            overlap += weights['strategy']
        
        # Colonial overlap
        if niche_a['colonial'] == niche_b['colonial']:
            overlap += weights['colonial']
        
        # Specialist overlap
        if niche_a['specialist'] == niche_b['specialist']:
            overlap += weights['specialist']
        
        return overlap
    
    def get_competitive_exclusion_penalty(self, species_a, species_b, 
                                         population_a: int, population_b: int) -> float:
        """
        Apply competitive exclusion when species with high niche overlap coexist
        Returns energy penalty multiplier for reproduction (0.5 - 1.0)
        """
        overlap = self.calculate_niche_overlap(species_a, species_b)
        
        # No competition if different niches
        if overlap < 0.4:
            return 1.0
        
        # Calculate population ratio
        total_pop = population_a + population_b
        if total_pop == 0:
            return 1.0
        
        pop_ratio = population_a / total_pop
        
        # Competitive exclusion principle:
        # When niches overlap and one species dominates, suppress the minority
        if overlap > 0.7:  # High overlap = strong competition
            if pop_ratio < 0.3:  # Minority species (< 30% of combined population)
                # Reproduction penalty scales with overlap and minority status
                penalty = 0.5 + ((pop_ratio / 0.3) * 0.3)  # 0.5x to 0.8x
                return penalty
        
        return 1.0
    
    def get_mutualism_bonus(self, species, neighbor_species_list) -> float:
        """
        Bonus for beneficial species interactions (complementary niches)
        Returns energy bonus multiplier (1.0 - 1.3)
        """
        if not neighbor_species_list:
            return 1.0
        
        bonus = 1.0
        my_niche = self.species_niches.get(species.id) or self.calculate_niche(species)
        
        for neighbor_species in neighbor_species_list:
            neighbor_niche = self.species_niches.get(neighbor_species.id) or self.calculate_niche(neighbor_species)
            
            # Mutualism examples:
            # 1. Photosynthesizers + predators (food chain)
            if (my_niche['energy_source'] == 'photosynthesis' and 
                neighbor_niche['energy_source'] == 'predation'):
                bonus *= 1.05  # Slight bonus
            
            # 2. Different complexity levels (ecosystem layers)
            complexity_diff = abs(my_niche['complexity'] - neighbor_niche['complexity'])
            if complexity_diff >= 2:
                bonus *= 1.05
            
            # 3. Complementary zone preferences (reduce competition)
            if my_niche['native_zone'] != neighbor_niche['native_zone']:
                bonus *= 1.03
        
        return min(1.3, bonus)  # Cap at 30% bonus
    
    def should_prevent_monoculture(self, dominant_species_pop: int, 
                                  total_population: int) -> bool:
        """
        Check if a monoculture is forming (one species > 80% of population)
        Returns True if diversity mechanisms should activate
        """
        if total_population == 0:
            return False
        
        dominance = dominant_species_pop / total_population
        return dominance > 0.8
    
    def get_monoculture_penalty(self, species_pop: int, total_pop: int) -> float:
        """
        Penalty for monoculture dominance (encourages diversity)
        Returns reproduction penalty multiplier
        """
        if total_pop == 0:
            return 1.0
        
        dominance = species_pop / total_pop
        
        if dominance > 0.9:
            return 0.5  # Severe penalty
        elif dominance > 0.8:
            return 0.7  # Moderate penalty
        elif dominance > 0.7:
            return 0.85  # Slight penalty
        
        return 1.0
