"""
Pygame Renderer
Handles visualization of the simulation
"""

import pygame
import numpy as np


class Renderer:
    def __init__(self, world, screen_size=(1600, 900)):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Primordial Garden")
        
        self.world = world
        self.screen_width, self.screen_height = screen_size
        
        # Calculate cell size to fit grid on screen
        self.cell_width = self.screen_width // world.width
        self.cell_height = self.screen_height // world.height
        
        # Colors
        self.bg_color = (10, 10, 15)  # Dark background
        self.dead_color = np.array([20, 20, 25], dtype=np.uint8)  # Dead cell color
        
        # Font for UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Preallocate color array for fast rendering
        self.color_array = np.zeros((world.height, world.width, 3), dtype=np.uint8)
        
        # Create surface for fast pixel access
        self.grid_surface = pygame.Surface((world.width, world.height))
    
    def draw_frame(self, show_stats=True, speed=1, paused=False):
        """Draw one frame of the simulation"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw grid
        self._draw_grid()
        
        # Draw stats overlay
        if show_stats:
            self._draw_stats(speed, paused)
        
        pygame.display.flip()
    
    def _draw_grid(self):
        """Draw the cellular automata grid using fast numpy operations"""
        # Start with dead color everywhere
        self.color_array[:] = self.dead_color
        
        # For each living species, set colors using numpy boolean indexing
        for species_id, species in self.world.species_registry.items():
            mask = self.world.grid == species_id
            if np.any(mask):
                self.color_array[mask] = species.color
        
        # Use surfarray for ultra-fast pixel rendering
        pygame.surfarray.blit_array(self.grid_surface, self.color_array.swapaxes(0, 1))
        
        # Scale to screen size
        scaled_surface = pygame.transform.scale(
            self.grid_surface, 
            (self.world.width * self.cell_width, self.world.height * self.cell_height)
        )
        
        # Blit to main screen
        self.screen.blit(scaled_surface, (0, 0))
    
    def _draw_stats(self, speed, paused):
        """Draw statistics overlay"""
        stats_x = 30
        stats_y = 20
        line_height = 25
        
        # Background panel - make it taller for more stats
        panel_width = 340
        panel_height = 280
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill((0, 0, 0))
        self.screen.blit(panel_surface, (stats_x - 10, stats_y - 10))
        
        # Calculate diversity metrics
        avg_age = self.world.get_average_species_age()
        species_count = len(self.world.species_registry)
        pop = self.world.total_population
        
        # Stats text
        stats = [
            f"Generation: {self.world.generation}",
            f"Population: {pop}",
            f"Species: {species_count}",
            f"Ratio: {(species_count/pop*100) if pop > 0 else 0:.1f}%",
            f"",
            f"Births: {self.world.births_this_gen}",
            f"Deaths: {self.world.deaths_this_gen}",
            f"Mutations: {self.world.mutations_this_gen}",
            f"Avg Age: {avg_age:.1f} gen",
            f"",
            f"Speed: {speed}x {'(PAUSED)' if paused else ''}",
            "",
            "SPACE: Pause | 1-5: Speed",
            "S: Stats | R: Reset | Q: Quit"
        ]
        
        for i, line in enumerate(stats):
            text_surface = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(text_surface, (stats_x, stats_y + i * line_height))
        
        # Species list (top 5)
        if self.world.species_registry:
            species_y = stats_y + panel_height + 20
            
            # Sort by population
            sorted_species = sorted(
                self.world.species_registry.values(),
                key=lambda s: s.population,
                reverse=True
            )[:5]
            
            species_panel = pygame.Surface((panel_width, 150))
            species_panel.set_alpha(180)
            species_panel.fill((0, 0, 0))
            self.screen.blit(species_panel, (stats_x - 5, species_y - 5))
            
            title = self.font.render("Top Species:", True, (200, 200, 200))
            self.screen.blit(title, (stats_x, species_y))
            
            for i, species in enumerate(sorted_species):
                # Color swatch
                swatch_rect = pygame.Rect(stats_x, species_y + 30 + i * 20, 15, 15)
                pygame.draw.rect(self.screen, species.color, swatch_rect)
                
                # Species info
                info = f"ID {species.id}: {species.population} cells"
                text = self.small_font.render(info, True, (200, 200, 200))
                self.screen.blit(text, (stats_x + 20, species_y + 30 + i * 20))
