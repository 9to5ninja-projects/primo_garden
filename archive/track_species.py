"""
Advanced species tracking and interaction analysis
Tracks lineages, interactions, and competitive dynamics
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from collections import defaultdict


def analyze_species_dynamics(csv_path):
    """Deep analysis of species interactions and survival"""
    df = pd.read_csv(csv_path)
    
    print("\n" + "=" * 70)
    print(f"SPECIES DYNAMICS ANALYSIS: {Path(csv_path).name}")
    print("=" * 70)
    
    # Parse dominant species column
    species_over_time = []
    for idx, row in df.iterrows():
        gen = row['generation']
        species_str = row['dominant_species']
        # Extract species ID from string like "Species(3, pop=0, id=3)"
        if 'id=' in species_str:
            species_id = int(species_str.split('id=')[1].split(')')[0])
            species_over_time.append({
                'generation': gen,
                'species_id': species_id,
                'total_pop': row['population'],
                'species_count': row['species_count']
            })
    
    species_df = pd.DataFrame(species_over_time)
    
    # 1. SPECIES LONGEVITY ANALYSIS
    print("\n" + "=" * 70)
    print("SPECIES LONGEVITY")
    print("=" * 70)
    
    species_lifespans = {}
    species_first_seen = {}
    species_last_seen = {}
    
    for _, row in species_df.iterrows():
        sid = row['species_id']
        gen = row['generation']
        
        if sid not in species_first_seen:
            species_first_seen[sid] = gen
        species_last_seen[sid] = gen
    
    for sid in species_first_seen:
        lifespan = species_last_seen[sid] - species_first_seen[sid]
        species_lifespans[sid] = {
            'first': species_first_seen[sid],
            'last': species_last_seen[sid],
            'lifespan': lifespan
        }
    
    # Sort by lifespan
    sorted_species = sorted(species_lifespans.items(), 
                           key=lambda x: x[1]['lifespan'], 
                           reverse=True)
    
    print(f"\nTotal unique species observed: {len(sorted_species)}")
    print("\nTop 10 Longest-Living Species:")
    print(f"{'Species ID':<12} {'First Seen':<12} {'Last Seen':<12} {'Lifespan':<12} {'Status'}")
    print("-" * 70)
    
    final_gen = df['generation'].max()
    for sid, info in sorted_species[:10]:
        status = "SURVIVED" if info['last'] == final_gen else "EXTINCT"
        print(f"{sid:<12} {info['first']:<12} {info['last']:<12} {info['lifespan']:<12} {status}")
    
    # 2. SUCCESSION ANALYSIS
    print("\n" + "=" * 70)
    print("SPECIES SUCCESSION (Dominance Changes)")
    print("=" * 70)
    
    dominant_changes = []
    prev_dominant = None
    
    for _, row in species_df.iterrows():
        current = row['species_id']
        if prev_dominant is not None and current != prev_dominant:
            dominant_changes.append({
                'generation': row['generation'],
                'from': prev_dominant,
                'to': current,
                'pop_at_change': row['total_pop']
            })
        prev_dominant = current
    
    print(f"\nTotal dominance shifts: {len(dominant_changes)}")
    if dominant_changes:
        print("\nMajor Succession Events:")
        print(f"{'Generation':<12} {'From Species':<15} {'To Species':<15} {'Population'}")
        print("-" * 70)
        
        for change in dominant_changes[:20]:  # Show first 20
            print(f"{change['generation']:<12} {change['from']:<15} {change['to']:<15} {change['pop_at_change']}")
    
    # 3. DIVERSITY COLLAPSE ANALYSIS
    print("\n" + "=" * 70)
    print("DIVERSITY COLLAPSE ANALYSIS")
    print("=" * 70)
    
    max_species = df['species_count'].max()
    final_species = df['species_count'].iloc[-1]
    
    print(f"\nPeak diversity: {max_species} species at generation {df[df['species_count'] == max_species]['generation'].iloc[0]}")
    print(f"Final diversity: {final_species} species")
    print(f"Diversity loss: {max_species - final_species} species ({((max_species - final_species) / max_species * 100):.1f}%)")
    
    # Find when diversity collapsed
    if max_species > 5:
        collapse_threshold = max_species * 0.5
        collapse_point = df[df['species_count'] < collapse_threshold]['generation'].min()
        if pd.notna(collapse_point):
            print(f"\nDiversity collapsed below 50% at generation {int(collapse_point)}")
    
    # 4. POPULATION PRESSURE ANALYSIS
    print("\n" + "=" * 70)
    print("POPULATION DYNAMICS")
    print("=" * 70)
    
    avg_pop = df['population'].mean()
    print(f"\nAverage population: {avg_pop:.1f}")
    print(f"Population range: {df['population'].min()} - {df['population'].max()}")
    
    # Stable periods (low variance)
    window = 50
    if len(df) >= window:
        df['pop_std'] = df['population'].rolling(window=window).std()
        stable_periods = df[df['pop_std'] < 30]  # Low variance = stable
        
        if len(stable_periods) > 0:
            print(f"\nStable periods (low variance over {window} gen):")
            print(f"  Total stable generations: {len(stable_periods)}")
            print(f"  Average population during stability: {stable_periods['population'].mean():.1f}")
    
    # 5. INTERACTION PATTERNS
    print("\n" + "=" * 70)
    print("COMPETITIVE EXCLUSION PATTERNS")
    print("=" * 70)
    
    # Look for species that rapidly replaced others
    rapid_takeovers = []
    for i in range(len(dominant_changes) - 1):
        current = dominant_changes[i]
        next_change = dominant_changes[i + 1]
        
        time_gap = next_change['generation'] - current['generation']
        if time_gap < 100:  # Rapid succession
            rapid_takeovers.append({
                'gen': current['generation'],
                'winner': current['to'],
                'loser': current['from'],
                'duration': time_gap
            })
    
    if rapid_takeovers:
        print(f"\nRapid takeovers (< 100 generations):")
        print(f"{'Generation':<12} {'Winner':<12} {'Defeated':<12} {'Time'}")
        print("-" * 70)
        for event in rapid_takeovers[:10]:
            print(f"{event['gen']:<12} {event['winner']:<12} {event['loser']:<12} {event['duration']} gen")
    else:
        print("\nNo rapid takeovers detected (stable coexistence)")
    
    # 6. VISUALIZATION
    create_species_timeline(species_df, Path(csv_path))
    
    return species_df, species_lifespans


def create_species_timeline(species_df, csv_path):
    """Create visualization of species succession"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Plot 1: Species diversity over time
    ax1 = axes[0]
    ax1.plot(species_df['generation'], species_df['species_count'], 'b-', linewidth=2)
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Number of Species')
    ax1.set_title('Species Diversity Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=1, color='r', linestyle='--', label='Monoculture')
    ax1.legend()
    
    # Plot 2: Dominant species changes
    ax2 = axes[1]
    species_ids = species_df['species_id'].unique()
    colors = plt.cm.tab20(range(len(species_ids)))
    species_colors = dict(zip(species_ids, colors))
    
    for i in range(len(species_df) - 1):
        row = species_df.iloc[i]
        next_row = species_df.iloc[i + 1]
        
        ax2.hlines(row['species_id'], row['generation'], next_row['generation'],
                  colors=species_colors[row['species_id']], linewidth=3)
    
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Dominant Species ID')
    ax2.set_title('Species Dominance Timeline')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Population vs Species Count
    ax3 = axes[2]
    scatter = ax3.scatter(species_df['generation'], species_df['total_pop'],
                         c=species_df['species_count'], cmap='viridis', 
                         alpha=0.6, s=20)
    ax3.set_xlabel('Generation')
    ax3.set_ylabel('Total Population')
    ax3.set_title('Population Size (colored by species diversity)')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='Species Count')
    
    plt.tight_layout()
    
    output_path = csv_path.parent / f"{csv_path.stem}_species_tracking.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n📊 Species timeline saved to: {output_path}")
    
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    else:
        # Find most recent export
        exports_dir = Path(__file__).parent / "exports"
        csv_files = list(exports_dir.glob("*.csv"))
        if not csv_files:
            print("No CSV files found in exports/ directory")
            sys.exit(1)
        
        csv_path = max(csv_files, key=lambda p: p.stat().st_mtime)
    
    print(f"Analyzing: {csv_path.name}\n")
    species_df, lifespans = analyze_species_dynamics(csv_path)
