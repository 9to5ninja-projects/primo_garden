#!/usr/bin/env python3
"""
Quick analysis script for exported simulation data
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def analyze_simulation(csv_path):
    """Analyze simulation CSV and generate plots"""
    df = pd.read_csv(csv_path)
    
    print("=" * 60)
    print(f"Simulation Analysis: {Path(csv_path).name}")
    print("=" * 60)
    
    # Basic stats
    print(f"\nTotal generations: {len(df)}")
    print(f"Generation range: {df['generation'].min()} - {df['generation'].max()}")
    print(f"\nPopulation stats:")
    print(f"  Min: {df['population'].min()}")
    print(f"  Max: {df['population'].max()}")
    print(f"  Mean: {df['population'].mean():.1f}")
    print(f"  Final: {df['population'].iloc[-1]}")
    
    print(f"\nSpecies stats:")
    print(f"  Min: {df['species_count'].min()}")
    print(f"  Max: {df['species_count'].max()}")
    print(f"  Final: {df['species_count'].iloc[-1]}")
    
    # Calculate species/population ratio
    df['species_ratio'] = df['species_count'] / df['population']
    print(f"\nSpecies/Population ratio:")
    print(f"  Start: {df['species_ratio'].iloc[0]:.3f}")
    print(f"  End: {df['species_ratio'].iloc[-1]:.3f}")
    print(f"  Change: {(df['species_ratio'].iloc[-1] - df['species_ratio'].iloc[0]):.3f}")
    
    # Check if new columns exist
    has_detailed_stats = 'births' in df.columns
    
    if has_detailed_stats:
        print(f"\nGeneration activity (last recorded):")
        print(f"  Births: {df['births'].iloc[-1]}")
        print(f"  Deaths: {df['deaths'].iloc[-1]}")
        print(f"  Mutations: {df['mutations'].iloc[-1]}")
        print(f"  Avg species age: {df['avg_species_age'].iloc[-1]:.1f} generations")
    
    # Diversity index might not exist in older exports
    if 'diversity_index' in df.columns:
        print(f"\nDiversity stats:")
        print(f"  Min Shannon index: {df['diversity_index'].min():.3f}")
        print(f"  Max Shannon index: {df['diversity_index'].max():.3f}")
        print(f"  Final: {df['diversity_index'].iloc[-1]:.3f}")
    
    # Detect if in oscillator state
    recent = df.tail(50)
    pop_std = recent['population'].std()
    if pop_std < 5:
        print(f"\n⚠ STABLE OSCILLATOR DETECTED")
        print(f"  Population variance (last 50 gen): {pop_std:.2f}")
        print(f"  Species still increasing: {recent['species_count'].iloc[-1] > recent['species_count'].iloc[0]}")
    
    # Create plots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle(f'Simulation Analysis: {Path(csv_path).name}', fontsize=14)
    
    # Plot 1: Population and Species over time
    ax1 = axes[0]
    ax1_twin = ax1.twinx()
    
    ax1.plot(df['generation'], df['population'], 'b-', label='Population', linewidth=2)
    ax1_twin.plot(df['generation'], df['species_count'], 'r-', label='Species', linewidth=2)
    
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Population', color='b')
    ax1_twin.set_ylabel('Species Count', color='r')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Population vs Species Count')
    
    # Plot 2: Species/Population Ratio
    ax2 = axes[1]
    ax2.plot(df['generation'], df['species_ratio'], 'g-', linewidth=2)
    ax2.axhline(y=1.0, color='r', linestyle='--', label='Full Fragmentation (ratio=1.0)')
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Species/Population Ratio')
    ax2.set_title('Genetic Fragmentation Progress')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Plot 3: Diversity Index (if available)
    ax3 = axes[2]
    if 'diversity_index' in df.columns:
        ax3.plot(df['generation'], df['diversity_index'], 'm-', linewidth=2)
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('Shannon Diversity Index')
        ax3.set_title('Species Diversity Over Time')
    else:
        # Plot births/deaths instead
        ax3.plot(df['generation'], df['births'], 'g-', label='Births', linewidth=2)
        ax3.plot(df['generation'], df['deaths'], 'r-', label='Deaths', linewidth=2)
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('Events per Generation')
        ax3.set_title('Births & Deaths Over Time')
        ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    output_path = Path(csv_path).parent / f"{Path(csv_path).stem}_analysis.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n📊 Plot saved to: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # Find most recent export
        exports_dir = Path(__file__).parent / "exports"
        csv_files = list(exports_dir.glob("*.csv"))
        if not csv_files:
            print("No CSV files found in exports/ directory")
            sys.exit(1)
        csv_path = max(csv_files, key=lambda p: p.stat().st_mtime)
        print(f"Analyzing most recent export: {csv_path.name}\n")
    
    analyze_simulation(csv_path)
