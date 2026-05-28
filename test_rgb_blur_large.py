import numpy as np
from scipy.signal import fftconvolve
import time

img = np.random.rand(1086, 1448, 3)
psf = np.random.rand(120, 120)
psf /= psf.sum()

start = time.time()
blurred = np.zeros_like(img)
for c in range(3):
    blurred[:, :, c] = fftconvolve(img[:, :, c], psf, mode='same')
print(f"Time taken: {time.time() - start:.3f} s")
