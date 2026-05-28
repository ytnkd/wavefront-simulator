import numpy as np
import scipy.ndimage

def scale_psf(psf, current_arcmin_per_px, target_arcmin_per_px):
    scale_factor = current_arcmin_per_px / target_arcmin_per_px
    scaled_psf = scipy.ndimage.zoom(psf, scale_factor, order=1)
    scaled_psf /= scaled_psf.sum()
    return scaled_psf

psf = np.zeros((100, 100))
psf[50, 50] = 1.0
scaled = scale_psf(psf, 0.1, 1.0)
print(scaled.shape)
