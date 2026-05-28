import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

bad_block = """def get_vision_simulation_base64(psf, arcmin_per_px, crop_radius_arcmin=60.0):
    load_vision_images()
    kernel = crop_psf(psf, arcmin_per_px, crop_radius_arcmin=crop_radius_arcmin)
    
    results = []"""

good_block = """import scipy.ndimage

def get_vision_simulation_base64(psf, arcmin_per_px, crop_radius_arcmin=60.0):
    load_vision_images()
    kernel = crop_psf(psf, arcmin_per_px, crop_radius_arcmin=crop_radius_arcmin)
    
    # Scale kernel so it matches a realistic FOV (e.g. 20 degrees for a 1000px image)
    photo_arcmin_per_px = 1.2
    scale_factor = arcmin_per_px / photo_arcmin_per_px
    if scale_factor < 1.0:
        kernel = scipy.ndimage.zoom(kernel, scale_factor, order=1)
        k_sum = kernel.sum()
        if k_sum > 1e-9:
            kernel /= k_sum
        else:
            kernel = np.array([[1.0]])

    results = []"""

content = content.replace(bad_block, good_block)

with open('backend/simulator.py', 'w') as f:
    f.write(content)

print("Applied vision blur scale fix!")
