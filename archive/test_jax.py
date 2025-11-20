import jax
import jax.numpy as jnp

print("=" * 50)
print("JAX INSTALLATION TEST")
print("=" * 50)
print(f"JAX version: {jax.__version__}")
import jaxlib
print(f"JAXlib version: {jaxlib.__version__}")
print()

print("Available devices:")
devices = jax.devices()
for i, device in enumerate(devices):
    print(f"  [{i}] {device}")
print()

print(f"Default backend: {jax.default_backend()}")
print()

# Quick performance test
print("Quick computation test:")
x = jnp.arange(1000)
y = jnp.sum(x ** 2)
print(f"  Sum of squares(0..999) = {y}")
print()

if jax.default_backend() == 'gpu':
    print("✓ GPU ACCELERATION ENABLED!")
elif jax.default_backend() == 'cuda':
    print("✓ CUDA GPU ACCELERATION ENABLED!")
else:
    print("⚠ Running on CPU (no GPU acceleration)")
    print("  This is normal on Windows - CUDA support limited")
    print("  JAX will still work but slower than GPU")

print("=" * 50)
