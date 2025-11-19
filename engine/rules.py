"""
Environmental Rules System
Defines the physical laws of the simulation
"""


class EnvironmentalRules:
    def __init__(self, params):
        """
        Initialize rules from parameter dictionary
        
        Expected params:
        - solar_radiation: float (energy input rate)
        - mutation_rate: float (probability of mutation per cell per generation)
        - survival_range: [min, max] neighbors for survival
        - birth_range: [min, max] neighbors for birth
        - cosmic_events: float (extinction event probability)
        - initial_density: float (starting life density)
        """
        self.energy_input = params.get('solar_radiation', 0.3)
        self.mutation_rate = params.get('mutation_rate', 0.001)
        self.survival_range = tuple(params.get('survival_range', [2, 3]))
        self.birth_range = tuple(params.get('birth_range', [3, 3]))
        self.extinction_pressure = params.get('cosmic_events', 0.0)
        
        # Future expansion parameters
        self.temperature = params.get('temperature', 1.0)
        self.chemistry = params.get('chemistry', 'neutral')
