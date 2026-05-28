import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
import time

# Create dummy image and psf
img = np.random.rand(300, 400, 3)
psf = np.random.rand(100, 100)
psf /= psf.sum()

start = time.time()
blurred = np.zeros_like(img)
for c in range(3):
    blurred[:, :, c] = fftconvolve(img[:, :, c], psf, mode='same')
print(f"Time taken: {time.time() - start:.3f} s")
