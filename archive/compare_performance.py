"""
Performance Comparison Tool
Compares standard Grid vs Numba-optimized Grid
"""

import time
import sys
from enhanced_engine.grid import Grid as StandardGrid
from grid_optimized import GridOptimized
from enhanced_engine.species_enhanced import Species, SpeciesTraits

def benchmark_grid(GridClass, name, size=200, initial_pop=1000, generations=50):
    """Benchmark a grid implementation"""
    print(f"\n{'='*70}")
    print(f"BENCHMARKING: {name}")
    print(f"{'='*70}")
    print(f"Grid: {size}x{size}, Initial pop: {initial_pop}, Generations: {generations}")
    
    # Create grid
    grid = GridClass(size, size, wrap=True)
    grid.setup_zones("random")
    
    # Create diverse species
    species_list = []
    for i in range(5):
        traits = SpeciesTraits(
            complexity=i + 1,
            photosynthesis_rate=6.0 + i,
            energy_decay=4.0 + i * 0.5,
            metabolic_efficiency=0.5 + i * 0.1
        )
        species = Species(f"Species{i}", traits)
        species_list.append(species)
    
    # Seed populations
    cells_per_species = initial_pop // len(species_list)
    for species in species_list:
        grid.seed_species(species, cells_per_species, "random")
    
    initial_stats = grid.get_stats()
    print(f"Starting population: {initial_stats['population']}")
    print(f"Starting species: {initial_stats['species_count']}")
    
    # Run benchmark
    print(f"\nRunning {generations} generations...")
    times = []
    populations = []
    
    for gen in range(generations):
        start = time.time()
        grid.step()
        elapsed = time.time() - start
        times.append(elapsed)
        
        stats = grid.get_stats()
        populations.append(stats['population'])
        
        if gen % 10 == 0:
            avg_time = sum(times[-10:]) / min(10, len(times))
            print(f"  Gen {gen:3d}: {stats['population']:5d} cells, "
                  f"{stats['species_count']:2d} species, "
                  f"{elapsed*1000:6.1f}ms/step (avg: {avg_time*1000:.1f}ms)")
    
    # Results
    final_stats = grid.get_stats()
    total_time = sum(times)
    avg_time = total_time / len(times)
    min_time = min(times[5:])  # Skip first 5 (warmup)
    max_time = max(times[5:])
    avg_pop = sum(populations) / len(populations)
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {name}")
    print(f"{'='*70}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Avg time per gen: {avg_time*1000:.1f}ms")
    print(f"Min time per gen: {min_time*1000:.1f}ms (after warmup)")
    print(f"Max time per gen: {max_time*1000:.1f}ms")
    print(f"Generations/sec: {generations/total_time:.1f}")
    print(f"Final population: {final_stats['population']}")
    print(f"Final species: {final_stats['species_count']}")
    print(f"Avg population: {avg_pop:.0f}")
    print(f"{'='*70}\n")
    
    return {
        'name': name,
        'total_time': total_time,
        'avg_time_ms': avg_time * 1000,
        'min_time_ms': min_time * 1000,
        'gens_per_sec': generations / total_time,
        'final_pop': final_stats['population']
    }


def main():
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PERFORMANCE COMPARISON TOOL" + " "*26 + "║")
    print("╚" + "="*68 + "╝")
    
    # Configuration
    size = 200
    initial_pop = 1000
    generations = 50
    
    print(f"\nConfiguration:")
    print(f"  Grid size: {size}x{size}")
    print(f"  Initial population: {initial_pop}")
    print(f"  Generations to run: {generations}")
    print(f"  Species: 5 diverse species")
    
    # Run benchmarks
    results = []
    
    print("\n" + "="*70)
    print("STARTING BENCHMARKS")
    print("="*70)
    
    # Standard Grid
    try:
        result_std = benchmark_grid(StandardGrid, "Standard Grid (Pure Python)", 
                                   size, initial_pop, generations)
        results.append(result_std)
    except Exception as e:
        print(f"\n❌ Standard Grid failed: {e}")
    
    # Optimized Grid
    try:
        result_opt = benchmark_grid(GridOptimized, "Numba-Optimized Grid", 
                                   size, initial_pop, generations)
        results.append(result_opt)
    except Exception as e:
        print(f"\n❌ Optimized Grid failed: {e}")
    
    # Comparison
    if len(results) >= 2:
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + " "*22 + "FINAL COMPARISON" + " "*31 + "║")
        print("╚" + "="*68 + "╝")
        
        std = results[0]
        opt = results[1]
        
        speedup = std['avg_time_ms'] / opt['avg_time_ms']
        time_saved = std['total_time'] - opt['total_time']
        
        print(f"\n{'Metric':<30} {'Standard':<20} {'Optimized':<20}")
        print("-" * 70)
        print(f"{'Avg time per generation':<30} {std['avg_time_ms']:>6.1f}ms{'':>13} {opt['avg_time_ms']:>6.1f}ms")
        print(f"{'Min time per generation':<30} {std['min_time_ms']:>6.1f}ms{'':>13} {opt['min_time_ms']:>6.1f}ms")
        print(f"{'Generations per second':<30} {std['gens_per_sec']:>6.1f}{'':>13} {opt['gens_per_sec']:>6.1f}")
        print(f"{'Total time':<30} {std['total_time']:>6.2f}s{'':>13} {opt['total_time']:>6.2f}s")
        print("-" * 70)
        print(f"\n🚀 SPEEDUP: {speedup:.1f}x faster!")
        print(f"⏱️  TIME SAVED: {time_saved:.1f}s ({time_saved/std['total_time']*100:.0f}% faster)")
        
        # Projections
        print(f"\n📊 PROJECTIONS:")
        print(f"  For 1000 generations:")
        print(f"    Standard: {std['avg_time_ms']*1000/1000:.1f}s ({std['avg_time_ms']*1000/60000:.1f} minutes)")
        print(f"    Optimized: {opt['avg_time_ms']*1000/1000:.1f}s ({opt['avg_time_ms']*1000/60000:.1f} minutes)")
        print(f"    Time saved: {(std['avg_time_ms']-opt['avg_time_ms'])*1000/60:.1f} minutes")
        
        print(f"\n  With 10,000 cells:")
        est_std = std['avg_time_ms'] * 20  # Rough scaling
        est_opt = opt['avg_time_ms'] * 2   # Better scaling
        print(f"    Standard: ~{est_std:.0f}ms/gen (est)")
        print(f"    Optimized: ~{est_opt:.0f}ms/gen (est)")
        print(f"    Speedup: ~{est_std/est_opt:.0f}x")
        
        print("\n" + "="*70)
        
        if speedup >= 10:
            print("✅ EXCELLENT: 10x+ speedup achieved!")
        elif speedup >= 5:
            print("✅ GREAT: 5-10x speedup achieved!")
        elif speedup >= 2:
            print("✅ GOOD: 2-5x speedup achieved!")
        else:
            print("⚠️  MODEST: <2x speedup (may need larger population to see benefits)")
        
        print("\n💡 TIP: To use optimized grid in your simulation:")
        print("   In main_enhanced.py, change:")
        print("     from enhanced_engine.grid import Grid")
        print("   To:")
        print("     from grid_optimized import GridOptimized as Grid")
        
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
