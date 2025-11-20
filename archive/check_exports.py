import pandas as pd
import os
from pathlib import Path

export_dir = Path("e:/garden/files/exports")
csv_files = sorted(export_dir.glob("*.csv"), key=os.path.getmtime, reverse=True)[:5]

print("=" * 70)
print("RECENT EXPORT ANALYSIS")
print("=" * 70)

for csv_file in csv_files:
    print(f"\n📊 {csv_file.name}")
    print("-" * 70)
    
    try:
        df = pd.read_csv(csv_file)
        
        total_records = len(df)
        generations = df['generation'].max()
        peak_pop = df['population'].max()
        species_count = df['species_count'].max()
        
        # File size
        file_size_mb = csv_file.stat().st_size / (1024 * 1024)
        
        # Final generation stats
        final_gen = df[df['generation'] == generations].iloc[0]
        
        print(f"  Generations: {generations:,}")
        print(f"  Total records: {total_records:,}")
        print(f"  File size: {file_size_mb:.2f} MB")
        print(f"  Peak population: {peak_pop:,} cells")
        print(f"  Max species count: {species_count}")
        print(f"  Final population: {final_gen['population']:,.0f}")
        print(f"  Final species: {final_gen['species_count']}")
        
        # Check for massive populations
        if peak_pop > 10000:
            print(f"  🔥 MASSIVE POPULATION: {peak_pop:,} cells!")
        elif peak_pop > 5000:
            print(f"  ⚠️  LARGE: {peak_pop:,} cells")
        
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")

print("\n" + "=" * 70)
