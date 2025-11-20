# JAX GPU Setup Guide for Primordial Garden
## Hardware: NVIDIA RTX (CUDA capable)

## Step 1: Install JAX with CUDA support

Open PowerShell/terminal and run:

```powershell
# Install JAX with CUDA 12 support (for RTX 30/40 series)
pip install --upgrade "jax[cuda12]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Or for older CUDA 11 (RTX 20 series)
# pip install --upgrade "jax[cuda11_local]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

## Step 2: Verify JAX sees your GPU

```powershell
python -c "import jax; print('Devices:', jax.devices())"
```

Expected output:
```
Devices: [cuda(id=0)]
```

If you see `cpu`, something went wrong with CUDA installation.

## Step 3: Test JAX Performance

```python
import jax.numpy as jnp
import time

# CPU test
x = jnp.ones((10000, 10000))
start = time.time()
y = jnp.dot(x, x).block_until_ready()
print(f"JAX time: {time.time() - start:.3f}s")
```

Should be very fast (~0.1s or less on GPU).

---

## Implementation Plan

### Phase 1: Core Grid as JAX Arrays (Day 1-2)
Convert grid representation:
```python
# From: List of Cell objects
# To: JAX arrays
self.alive = jnp.array([[False, True, ...]])
self.energy = jnp.array([[0.0, 50.0, ...]])
self.species_id = jnp.array([[0, 5, ...]])
```

### Phase 2: Vectorized Operations (Day 2-3)
Parallelize across GPU:
- Neighbor counting (Conway rules)
- Energy updates
- Movement calculations
- Zone pressure

### Phase 3: Species Logic Bridge (Day 3-4)
Keep complex species behavior on CPU, run grid updates on GPU:
```python
# GPU: Fast grid operations
grid_state = jax_update_grid(grid_state)  # GPU

# CPU: Complex species decisions
for species in active_species:
    behavior = species.get_movement_strategy()  # CPU
```

### Phase 4: Optimize Rendering (Day 4-5)
GPU → CPU transfer optimization for display

---

## Architecture Design

```
┌─────────────────────────────────────┐
│         Python Control Layer        │
│  (Species logic, UI, I/O)          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│         JAX Computation Layer       │
│  @jit compiled functions            │
│  - Grid updates                     │
│  - Neighbor counting                │
│  - Energy calculations              │
│  - Movement processing              │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│            NVIDIA GPU               │
│  Parallel processing of cells       │
└─────────────────────────────────────┘
```

---

## Expected Performance Gains

Current (CPU):
- 200x200 grid: ~5 FPS
- 400x400 grid: <1 FPS

With JAX (GPU):
- 200x200 grid: ~200 FPS (40x faster)
- 400x400 grid: ~60 FPS (60x faster)
- 1000x1000 grid: ~20 FPS (playable!)
- 2000x2000 grid: ~5 FPS (possible!)

---

## Let's Start!

Ready to begin? I'll:

1. Create a JAX-accelerated version of the grid
2. Keep species behavior intact
3. Test on small grid first
4. Scale up once working

Say "go" and I'll start refactoring!
